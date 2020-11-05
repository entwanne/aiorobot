import asyncio
import itertools

import aiorobot


async def drive(robot):
    for i in range(4):
        await robot.motor.drive(150)
        await robot.motor.rotate(900)


async def color(robot):
    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
    ]
    for i in itertools.count():
        await robot.led.on(colors[i % 3])
        await asyncio.sleep(0.5)


async def main():
    async with aiorobot.get_robot() as robot:
        asyncio.create_task(color(robot))
        await drive(robot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
