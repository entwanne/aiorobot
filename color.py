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

async def touch(robot):
    red = max(await robot.color.get(ColorSensor.LEFT, ColorLightning.RED, ColorFormat.ADC))
    green = max(await robot.color.get(ColorSensor.LEFT, ColorLightning.GREEN, ColorFormat.ADC))
    blue = max(await robot.color.get(ColorSensor.LEFT, ColorLightning.BLUE, ColorFormat.ADC))
    print(red, green, blue)

    red = min(int(255 * red / 500), 255)
    green = min(int(255 * green / 200), 255)
    blue = min(int(255 * blue / 800), 255)

    print(red, green, blue)
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
