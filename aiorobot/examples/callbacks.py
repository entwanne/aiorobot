import itertools

from aiorobot import run


async def start(robot):
    print(await robot.get_name())

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


async def touch(robot, timestamp, state):
    if state:
        await robot.led.spin((0, 255, 0))
    else:
        await robot.led.off()


async def bump(robot, timestamp, bumper):
    r = g = b = 0
    if bumper & bumper.LEFT:
        r = 255
    if bumper & bumper.RIGHT:
        b = 255
    await robot.led.on((r, g, b))


if __name__ == '__main__':
    run(
        started=start,
        stopped=stop,
        touch_event=touch,
        bumper_event=bump,
    )
