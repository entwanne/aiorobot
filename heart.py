from aiorobot import run
from aiorobot.fake_driver import Client


async def main(robot):
    await robot.marker.down()

    await robot.motor.drive(160)
    await robot.motor.rotate(1200)
    await robot.motor.drive(160)
    await robot.motor.rotate(300)
    await robot.motor.drive_arc(1800, 40)
    await robot.motor.rotate(1800)
    await robot.motor.drive_arc(1800, 40)

    await robot.marker.up()
    await robot.motor.drive(200)
    await robot.disconnect()

run(started=main, client_cls=Client)
#run(started=main)
