import asyncio
import curses
import threading
import queue

from aiorobot import run


async def key_up(robot):
    await robot.motor.drive(100, wait=False)

async def key_down(robot):
    await robot.motor.drive(-100, wait=False)

async def key_left(robot):
    await robot.motor.rotate(-200, wait=False)

async def key_right(robot):
    await robot.motor.rotate(200, wait=False)


mapping = {
    curses.KEY_UP: key_up,
    curses.KEY_DOWN: key_down,
    curses.KEY_LEFT: key_left,
    curses.KEY_RIGHT: key_right,
}


async def start(robot):
    loop = asyncio.get_running_loop()
    while True:
        key = await loop.run_in_executor(None, q.get)
        if key is None:
            break
        await mapping[key](robot)
    await robot.disconnect()


def main(stdscr):
    while True:
        key = stdscr.get_wch()
        if key in mapping:
            q.put_nowait(key)

q = queue.SimpleQueue()
thr = threading.Thread(target=run, kwargs={'started': start})
thr.start()
try:
    curses.wrapper(main)
finally:
    q.put_nowait(None)
