import itertools

from aiorobot import run_robot


async def start(robot):
    notes = [
        131,
        145,
        165,
        175,
        196,
        220,
        247,
        262,
    ]
    notes = [n*2 for n in notes]

    for note in itertools.cycle(notes + notes[::-1]):
        await robot.music.play(note, 500)


async def stop(robot):
    await robot.disconnect()


await run_robot(started=start, stopped=stop)
