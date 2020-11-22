import os
import glob
import time
import requests
from datetime import datetime

URL = os.environ['LAMBDA_URL']
measurement_period = 60*10
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')

 
def read_temp_raw(device_folder):
    device_file = device_folder + '/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(device_folder):
    lines = read_temp_raw(device_folder)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def register_measurement(device_folder):
    measurement = read_temp(device_folder)
    device = os.path.split(device_folder)[-1]
    if measurement > 40:
        pass
    else:
        data = {'measurement_datetime':datetime.now(),
            'measurement_type':'TEMPERATURE',
            'meter_id':device,
            'measurement_value':measurement}
        r = requests.get(url, params=data)
        return r 

while True:
    for df in device_folders:
        register_measurement(df)        
    time.sleep(measurement_period)