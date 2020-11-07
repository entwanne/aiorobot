import curses

from aiorobot.examples.thread import run_thread, queue as q


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
    while True:
        key = await q.get()
        if key is None:
            break
        await mapping[key](robot)
    await robot.disconnect()


def main(stdscr):
    while True:
        key = stdscr.get_wch()
        if key in mapping:
            q.put_nowait(key)

try:
    run_thread(started=start)
    curses.wrapper(main)
finally:
    q.put_nowait(None)
