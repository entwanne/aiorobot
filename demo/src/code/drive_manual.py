from aiorobot import get_robot

async def main():
    async with get_robot() as robot:
        await robot.marker.down()
        for i in range(4):
            await robot.led.on((0, i * 80, 100))
            await robot.motor.drive(150)
            await robot.motor.rotate(900)
        await robot.marker.up()

await main()
