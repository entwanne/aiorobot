from aiorobot import run
from aiorobot.types import Devices


async def started(robot):
    #await robot.events.disable(Devices.BUMPERS)
    print(await robot.events.get_enabled())


async def bump(robot, timestamp, bumper):
    print(bumper)


run(
    started=started,
    bumper_event=bump,
)
