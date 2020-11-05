import asyncio

import aiorobot


async def main():
    async with aiorobot.get_robot() as robot:
        while True:
            await robot.motor.rotate(900)
            async for event in robot.events.current:
                print(event)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
