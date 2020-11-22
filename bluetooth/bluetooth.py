import asyncio
from bleak import BleakScanner, BleakClient
import binascii
from bleak.uuids import uuid16_dict
import time
import dotenv
import os

MAC_ADDRESS = os.environ['MAC_ADDRESS']
HANDLES = {'battery':34,
            'unknown':38}
CHARACTERISTICS = MAC_ADDRESS = os.environ['CHARACTERISTICS']
SERVICE = os.environ['SERVICE']

async def discover():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d, d.metadata, '\n')


async def poll_thermobeacon():
    for i in range(2):
        print(i)
        time.sleep(5)
        devices = await BleakScanner.discover()
        for d in devices:
            if d.address == MAC_ADDRESS:
                try:
                    print(type(d.metadata['manufacturer_data'][16]))
                except:
                    print('No metadata')
                    pass


async def connect(mac_address):
    client = BleakClient(mac_address)
    await client.connect()
    await client.pair()
    services = await client.get_services()
    for s in services:
        print('Service: ', s.description, s.uuid)
        characteristics = s.characteristics
        for c in characteristics:
            print('\tCharacteristic:', c.description, c.uuid, c.properties, )
            descriptors = c.descriptors
            for d in descriptors:
                print('\t\tDescriptor:', d.description, d.uuid, d.handle)
    await client.unpair()
    await client.disconnect()

async def test_descriptor(mac_address, handle):
    client = BleakClient(mac_address)
    await client.connect()
    descriptor_value = await client.read_gatt_descriptor(handle)
    print( binascii.hexlify(descriptor_value))
    await client.disconnect()

def notification_handler(sender, data):
    print("{0}: {1}".format(sender, data))

async def test_notify(mac_address, char_uuid):
    client = BleakClient(mac_address)
    await client.connect()
    print('Connected')
    await client.start_notify(char_uuid, notification_handler)
    await asyncio.sleep(10)
    await client.stop_notify(char_uuid)
    await client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(poll_thermobeacon())
# loop.run_until_complete(test_descriptor(MAC_ADDRESS, HANDLES['battery']))
# loop.run_until_complete(connect(MAC_ADDRESS))
# loop.run_until_complete(test_notify(MAC_ADDRESS, CHARACTERISTICS['test']))

