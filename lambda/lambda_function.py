import json
import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

POSTGRES_HOST=os.environ['POSTGRES_HOST']
POSTGRES_PORT=os.environ['POSTGRES_PORT']
POSTGRES_DB=os.environ['POSTGRES_DB']
POSTGRES_USER=os.environ['POSTGRES_USER']
POSTGRES_PASSWORD=os.environ['POSTGRES_PASSWORD']



def lambda_handler(event, context):
    measurement = Measurement(event)
    measurement.write_to_db()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


class Measurement():

    def __init__(self, lambda_event):
        self.datetime = lambda_event['queryStringParameters']['measurement_datetime']
        self.measurement_type = lambda_event['queryStringParameters']['measurement_type']
        self.meter_id = lambda_event['queryStringParameters']['meter_id']
        self.measurement_value = float(lambda_event['queryStringParameters']['measurement_value'])

    def construct_sql(self):
        return f"""INSERT INTO measurement (measurement_datetime, 
                                            measurement_type, 
                                            meter_id, 
                                            measurement_value)
                    VALUES ('{self.datetime}',
                            '{self.measurement_type}',
                            '{self.meter_id}', 
                             {self.measurement_value})"""

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