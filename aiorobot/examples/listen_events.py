import asyncio

import aiorobot


async def main():
    async with aiorobot.get_robot() as robot:
        async for event in robot.events:
            print(event)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
