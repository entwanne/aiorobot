import asyncio

from robot import get_robot


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
    async with get_robot() as robot:
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
