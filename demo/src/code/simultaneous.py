from aiorobot import run_robot

async def drive(robot):
    await robot.motor.drive_arc(1800, 200)

async def color(robot):
    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
    ]
    for i in itertools.count():
        await robot.led.on(colors[i % 3])
        await asyncio.sleep(0.5)

async def main(robot):
    asyncio.create_task(color(robot))
    await drive(robot)
    await robot.disconnect()

await run_robot(started=main)
