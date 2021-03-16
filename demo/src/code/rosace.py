from aiorobot import run_robot

async def flower(robot):
    for _ in range(3):
        await robot.motor.rotate(600)
        await robot.motor.drive_arc(1200, 200)
        await robot.motor.rotate(600)

async def main(robot):
    await robot.motor.drive(200)

    await robot.marker.down()
    await robot.motor.drive_arc(3600, 200)
    await flower(robot)

    await robot.motor.drive_arc(600, 200)
    await flower(robot)

    await robot.marker.up()
    await robot.motor.drive(200)
    await robot.disconnect()

await run_robot(started=main)
