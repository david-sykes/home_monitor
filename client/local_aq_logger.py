from sgp30 import SGP30
import time
import logging
import os
from datetime import datetime

LOG_PATH = f'air_quality_{datetime.now().date()}.log'
MEASUREMENT_INTERVAL = 60

open(LOG_PATH, 'w').close()

logger = logging.getLogger('myapp')
hdlr = logging.FileHandler(LOG_PATH)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)


sgp30 = SGP30()

sgp30.start_measurement()


while True:
    result = sgp30.get_air_quality()
    print(result)
    logger.info(result)
    time.sleep(MEASUREMENT_INTERVAL)


