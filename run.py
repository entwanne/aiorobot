import asyncio

from robot import get_robot



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
        async for event in robot.all_events:
            print(event)


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
