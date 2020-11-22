import json
import os
import psycopg2
import pytz
from datetime import datetime, timedelta
import requests

#Comment this out in AWS envinronment
from dotenv import load_dotenv
load_dotenv()

POSTGRES_HOST=os.environ['POSTGRES_HOST']
POSTGRES_PORT=os.environ['POSTGRES_PORT']
POSTGRES_DB=os.environ['POSTGRES_DB']
POSTGRES_USER=os.environ['POSTGRES_USER']
POSTGRES_PASSWORD=os.environ['POSTGRES_PASSWORD']
OCTOPUS_API_USER=os.environ['OCTOPUS_API_USER']
OCTOPUS_API_PW=os.environ['OCTOPUS_API_PW']
MPRN=os.environ['MPRN']
SERIAL_NUMBER=os.environ['SERIAL_NUMBER']
DAY_LAG=int(os.environ['DAY_LAG'])
M3_TO_KWH=11.1868

OCTOPUS_URL_TEMPLATE='https://api.octopus.energy/v1/{fuel}-meter-points/{mpxn}/meters/{serial_number}/consumption/'


def collect_readings(fuel, mpxn, serial_number, period_from, period_to):
    data = {
            'period_from':period_from,
            'period_to':period_to,
            'page_size':25000,
            }
    url = OCTOPUS_URL_TEMPLATE.format(fuel=fuel, mpxn=mpxn, serial_number=serial_number)
    print(url)
    r = requests.get(url, params=data, auth=(OCTOPUS_API_USER, OCTOPUS_API_PW))
    output = {}
    if r.json().get('results'):
        readings = r.json().get('results')
        for reading in readings:
            if fuel == 'gas':
                reading['consumption'] = convert_gas_delta(reading['consumption'])
            reading['interval_start'] = process_timestamp(reading['interval_start'])
            reading['interval_end'] = process_timestamp(reading['interval_end'])
            reading['fuel'] = fuel
            reading['mpxn'] = mpxn
            reading['serial_number'] = serial_number
        return readings
    else:
        return r.json()


def process_timestamp(time_string):
    """Return UTC time"""
    dt = datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S%z')
    return dt.astimezone(pytz.utc)

def convert_gas_delta(delta):
    return M3_TO_KWH*delta

class MeterReading():

    def __init__(self, reading):
        self.interval_start = reading['interval_start']
        self.interval_end = reading['interval_end']
        self.consumption_kwh = reading['consumption']
        self.fuel = reading['fuel']
        self.mpxn = reading['mpxn']
        self.serial_number = reading['serial_number']



    def construct_sql(self):
        return f"""INSERT INTO meter_reading (interval_start,
                                            interval_end,
                                            consumption_kwh,
                                            fuel,
                                            mpxn,
                                            serial_number)

                        VALUES ('{self.interval_start}',
                            '{self.interval_end}',
                            {self.consumption_kwh}, 
                             '{self.fuel}',
                             '{self.mpxn}',
                             '{self.serial_number}'
                             )
                        ON CONFLICT (interval_start, mpxn, serial_number) 
                            DO 
                        UPDATE SET consumption_kwh = EXCLUDED.consumption_kwh;"""


    def write_to_db(self):
        conn = psycopg2.connect(host=POSTGRES_HOST,
                                port=POSTGRES_PORT,
                                user=POSTGRES_USER,
                                password=POSTGRES_PASSWORD,
                                database=POSTGRES_DB) # To remove slash

        cursor = conn.cursor()
        sql = self.construct_sql()
        cursor.execute(sql)
        conn.commit() # <- We MUST commit to reflect the inserted data
        cursor.close()
        conn.close()


def lambda_handler(event, context):
    r = collect_readings('gas', MPRN, SERIAL_NUMBER,
                         datetime.now() - timedelta(days=DAY_LAG), datetime.now())
    for reading in r:
        mr = MeterReading(reading)
        mr.write_to_db()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }