import asyncio

from robot import get_robot


async def started():
    print('STARTED')


async def bump(timestamp, bumper):
    print(bumper)

async def run():
    async with get_robot() as robot:
        print(await robot.get_name())
        #await robot.motor.drive_distance(100)
        #await robot.eraser.down()
        '''
        await robot.led.on((255, 0, 0))
        await asyncio.sleep(2)
        await robot.led.spin()
        await asyncio.sleep(2)
        await robot.led.off()
        await asyncio.sleep(2)
        await robot.led.blink()
        await asyncio.sleep(2)
        '''
        #await robot.music.play(100)
        #await asyncio.sleep(2)
        #async for event in robot.events.current:
        #    print(event)
        #print('!')
        #async for event in robot.events:
        #    print(event)
        robot.events.set_callback('started', started)
        robot.events.set_callback('bumper_event', bump)
        await robot.events.process()


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
