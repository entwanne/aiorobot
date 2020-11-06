import asyncio
import curses
import threading
import queue

from aiorobot import run


notes_freq = {
    'C': 131,
    'D': 145,
    'E': 165,
    'F': 175,
    'G': 196,
    'A': 220,
    'B': 247,

    'C#': 139,
    'Ef': 156,
    'F#': 185,
    'G#': 208,
    'Bf': 233,
}
notes_names = {
    'C': 'do',
    'D': 'ré',
    'E': 'mi',
    'F': 'fa',
    'G': 'sol',
    'A': 'la',
    'B': 'si',
}

# keyboard char -> (note, multiplicator)
mapping = dict(zip(
    'qsdfghjklmù*',
    zip('GABCDEFGABCD', (1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3)),
))


async def piano(robot):
    for letter, (note, _) in mapping.items():
        print(letter, notes_names[note])

    loop = asyncio.get_running_loop()
    while True:
        c = await loop.run_in_executor(None, q.get)
        if c is None:
            break
        note, mul = mapping[c]
        await robot.music.play(notes_freq[note]*2**mul, 500)
    await robot.disconnect()


def main(stdscr):
    while True:
        c = stdscr.get_wch()
        if c in mapping:
            q.put_nowait(c)

q = queue.SimpleQueue()
thr = threading.Thread(target=run, kwargs={'started': piano})
thr.start()
try:
    curses.wrapper(main)
finally:
    q.put_nowait(None)
