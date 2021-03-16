from aiorobot import run
from aiorobot.fake_driver import Client


async def main(robot):
    await robot.marker.down()

    radius = 100
    await robot.motor.drive_arc(1800, radius)
    #await robot.motor.drive_arc(3600, radius)
    await robot.motor.rotate(900)
    await robot.motor.drive(2 * radius)

    #await robot.motor.rotate(900)
    #await robot.motor.drive_arc(3600, radius)

    await robot.marker.up()
    await robot.motor.drive(200)
    await robot.disconnect()

run(started=main, client_cls=Client)
#run(started=main)
