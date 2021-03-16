import asyncio

from aiorobot import run_robot


async def start(robot):
    await robot.motor.set_speed(100, 100)


async def stop(robot):
    await robot.disconnect()


async def bump(robot, timestamp, bumper):
    if bumper & bumper.LEFT:
        await robot.motor.set_speed(50, 100)
        await asyncio.sleep(1)
        await robot.motor.set_speed(100, 100)
    elif bumper & bumper.RIGHT:
        await robot.motor.set_speed(100, 50)
        await asyncio.sleep(1)
        await robot.motor.set_speed(100, 100)


await run_robot(started=start, stopped=stop, bumper_event=bump)
