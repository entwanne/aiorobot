from aiorobot import run_robot
from aiorobot.examples.thread import queue as q

async def start(robot):
    while True:
        event = await q.get()
        if event is None:
            break
        left, right = event
        await robot.motor.set_speed(left, right)
    await robot.motor.set_speed(0, 0)
    await robot.disconnect()

loop = asyncio.get_running_loop()
await asyncio.gather(
    run_robot(started=start),
    loop.run_in_executor(None, tk_thread),
)
