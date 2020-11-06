from aiorobot import run
from aiorobot.types import *

async def start(robot):
    print(await robot.color.get(ColorSensor.LEFT, ColorLightning.ALL, ColorFormat.ADC))
    await robot.disconnect()

run(started=start)
