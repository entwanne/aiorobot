import asyncio

from aiorobot import run
from aiorobot.examples.callbacks import start as music
from aiorobot.examples.simultaneous import drive


async def started(robot):
    asyncio.create_task(music(robot))
    await drive(robot)
    await robot.disconnect()


if __name__ == '__main__':
    run(
        started=started,
    )
