from aiorobot import run


async def main(robot):
    for i in range(4):
        await robot.led.on((0, i * 80, 100))
        await robot.motor.drive(150)
        await robot.motor.rotate(900)
    await robot.disconnect()


if __name__ == '__main__':
    run(started=main)
