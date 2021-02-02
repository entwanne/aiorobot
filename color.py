from aiorobot import run
from aiorobot.types import *

async def start(robot):
    #print(await robot.get_version())
    #print(await robot.get_color_board_version())

    #print(await robot.color.get(ColorSensor.LEFT, ColorLightning.OFF, ColorFormat.ADC))
    print(await robot.color.get(ColorSensor.LEFT, ColorLightning.RED, ColorFormat.ADC))
    print(await robot.color.get(ColorSensor.LEFT, ColorLightning.GREEN, ColorFormat.ADC))
    print(await robot.color.get(ColorSensor.LEFT, ColorLightning.BLUE, ColorFormat.ADC))
    print(await robot.color.get(ColorSensor.LEFT, ColorLightning.ALL, ColorFormat.ADC))

    #print(await robot.color.get(ColorSensor.LEFT, ColorLightning.OFF, ColorFormat.MV))
    print(await robot.color.get(ColorSensor.LEFT, ColorLightning.RED, ColorFormat.MV))
    print(await robot.color.get(ColorSensor.LEFT, ColorLightning.GREEN, ColorFormat.MV))
    print(await robot.color.get(ColorSensor.LEFT, ColorLightning.BLUE, ColorFormat.MV))
    print(await robot.color.get(ColorSensor.LEFT, ColorLightning.ALL, ColorFormat.MV))

    await robot.disconnect()

run(started=start)
