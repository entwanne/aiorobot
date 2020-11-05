import asyncio

import aiorobot


async def main():
    async with aiorobot.get_robot() as robot:
        for i in range(4):
            await robot.led.on((0, i * 80, 0))
            await robot.motor.drive(150)
            await robot.motor.rotate(900)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
