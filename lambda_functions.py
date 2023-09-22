import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import asyncio
import time

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.generic import Generic

import boto3
secrets = boto3.client('ssm')
import json

def printer_clear(event, context):
    for robot in event.get("robots"):
        asyncio.run(printer_event_main('        '), robot)

def printer_event(event, context):
    print(event)

    os.environ['TZ'] = 'EST+05EDT'
    time.tzset()
    print("it is now: ",time.localtime())
    if time.localtime().tm_hour > (9+12):
        print("sleeping because its past 10pm")
        asyncio.run(printer_event_main('        '))

    message = 'UNK. STAT.'
    topic = event.get('topic')
    if topic == 'User Action Needed':
        message = 'HELP NOW'
    else:
        progress = "{:.0f}".format(event.get('progress', dict()).get('completion')).rjust(3,' ')
        message = "PRINT" + progress
    for robot in event.get("robots"):
        asyncio.run(printer_event_main(message, robot))

async def printer_event_main(progress: str, robot: str):
    try:
        location_secret = secrets.get_parameter(Name="/{0}/location-secret".format(robot), WithDecryption=True)
        robot_fqdn = secrets.get_parameter(Name='/{0}/robot-fqdn'.format(robot), WithDecryption=True)
        robot = await connect(location_secret, robot_fqdn)
        led_segment = Generic.from_robot(robot, "led_displays")
        await led_segment.do_command({"print":{"value":progress}})
        await robot.close()
    except Exception as ex:
        print(ex)
        return {'result': "failure"}

    response = {'result': "success"}
    return response

def chachinga(event, context):
    print(event)
    asyncio.run(chachinga_main(event.get('sound')))

async def chachinga_main(sound: str):
    location_secret = secrets.get_parameter(Name='/chachinga/location_secret', WithDecryption=True)
    robot_fqdn = secrets.get_parameter(Name='/chachinga/robot_fqdn', WithDecryption=True)
    robot = await connect(location_secret, robot_fqdn)
    speaker = Generic.from_robot(robot, "speaker")
    await speaker.do_command({"play":{"sound":sound}})

    await robot.close()

    response = {'result': "success"}
    return response

async def connect(location_secret, robot_fqdn):
    creds = Credentials(
        type='robot-location-secret',
        payload=location_secret['Parameter']['Value'])
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(robot_fqdn['Parameter']['Value'], opts)

if __name__ == '__main__':
    asyncio.run(printer_event_main("TESTING1","printerstatus"))