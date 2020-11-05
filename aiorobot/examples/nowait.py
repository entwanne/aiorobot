import asyncio

import aiorobot


async def main():
    async with aiorobot.get_robot() as robot:
        await robot.motor.drive(150, wait=False)
        await robot.led.on((0, 0, 255))
        await asyncio.sleep(2)
        await robot.motor.drive(-150, wait=False)
        await robot.led.on((0, 255, 0))
        await asyncio.sleep(2)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
