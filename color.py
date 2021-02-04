#from aiorobot import run
from aiorobot.examples.thread import run_thread, queue as q
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

def calibrate_color(color, a=1, b=0):
    return min(int(255 * color / a + b), 255)

async def touch(robot):
    red = max(await robot.color.get(ColorSensor.LEFT, ColorLightning.RED, ColorFormat.ADC))
    green = max(await robot.color.get(ColorSensor.LEFT, ColorLightning.GREEN, ColorFormat.ADC))
    blue = max(await robot.color.get(ColorSensor.LEFT, ColorLightning.BLUE, ColorFormat.ADC))
    black = max(await robot.color.get(ColorSensor.LEFT, ColorLightning.OFF, ColorFormat.ADC))

    red -= black
    green -= black
    blue -= black

    print(red, green, blue, black)

    black = calibrate_color(black, 400)
    red = calibrate_color(red, 600, black)
    green = calibrate_color(green, 200, black)
    blue = calibrate_color(blue, 700, black)

    print(red, green, blue, black)
    return red, green, blue

async def start_tk(robot):
    await q.get()
    await robot.disconnect()

async def touch_tk(robot):
    r, g, b = await touch(robot)
    color = f'#{r:02x}{g:02x}{b:02x}'
    print(color)
    canvas.configure(bg=color)

#run(started=start)
#run(stopped=touch)
run_thread(started=start_tk, stopped=touch_tk)

import tkinter as tk
root = tk.Tk()
canvas = tk.Canvas(root)
canvas.pack()
try:
    root.mainloop()
finally:
    q.put_nowait(None)
