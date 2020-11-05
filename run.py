import asyncio

from aiorobot.robot import run_robot


async def started(robot):
    print(await robot.get_name())


async def bump(robot, timestamp, bumper):
    r = g = b = 0
    if bumper & bumper.LEFT:
        r = 255
    if bumper & bumper.RIGHT:
        b = 255
    await robot.led.on((r, g, b))


async def run():
    await run_robot(
        started=started,
        bumper_event=bump,
    )


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
