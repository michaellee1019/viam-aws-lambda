import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.generic import Generic

import boto3
secrets = boto3.client('ssm')
import json

def printer_event(event, context):
    print(event)
    progress = event.get('progress', dict()).get('completion')
    return asyncio.run(printer_event_main('UKN' if progress is None else progress))

async def printer_event_main(progress: str):
    location_secret = secrets.get_parameter(Name='/printerstatus/location-secret', WithDecryption=True)
    robot_fqdn = secrets.get_parameter(Name='/printerstatus/robot-fqdn', WithDecryption=True)
    robot = await connect(location_secret, robot_fqdn)
    led_segment = Generic.from_robot(robot, "segments")
    await led_segment.do_command({"print":{"value":"PRINT" + progress}})

    await robot.close()

    response = {'result': "success"}
    return response

def chachinga(event, context):
    asyncio.run(chachinga_main())

async def chachinga_main():
    location_secret = secrets.get_parameter(Name='/chachinga/location_secret', WithDecryption=True)
    robot_fqdn = secrets.get_parameter(Name='/chachinga/robot_fqdn', WithDecryption=True)
    robot = await connect(location_secret, robot_fqdn)
    speaker = Generic.from_robot(robot, "speaker")
    await speaker.do_command({"play":{"sound":"chaching"}})

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
    asyncio.run(printer_event_main())