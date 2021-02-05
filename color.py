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
    #color = await robot.color[12]
    #print(color)
    #return color
    #colors = await robot.color.all()
    #colors = await robot.color[10:20]
    #print(colors)
    #return colors[5]
    #color = await robot.color.mean(0, 8)
    color = await robot.color.max(0, 8)
    print(color)
    return color

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
