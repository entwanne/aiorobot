import asyncio
import curses
import threading
import queue

from aiorobot import run

from print_piano import get_piano


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

    'C#': 'do#',
    'Ef': 'mi♭',
    'F#': 'fa#',
    'G#': 'sol#',
    'Bf': 'si♭',
}

# keyboard char -> (note, multiplicator)
mapping = dict(zip(
    'qsdfghjklmù*',
    zip('GABCDEFGABCD', (1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3)),
))
mapping.update(zip(
    'azetyiop$',
    zip(('F#', 'G#', 'Bf', 'C#', 'Ef', 'F#', 'G#', 'Bf', 'C#'), (1, 1, 1, 2, 2, 2, 2, 2, 3))
))


async def piano(robot):
    loop = asyncio.get_running_loop()
    while True:
        c = await loop.run_in_executor(None, q.get)
        if c is None:
            break
        note, mul = mapping[c]
        await robot.music.play(notes_freq[note]*2**mul, 500)
    await robot.disconnect()


def main(stdscr):
    piano = get_piano(
        'GABCDEFGABCD',
        'qsdfghjklmù*',
        ('F#', 'G#', 'Bf', None, 'C#', 'Ef', None, 'F#', 'G#', 'Bf', None, 'C#', ''),
        'aze ty iop $ ',
        200,
        30,
    )
    for y, line in enumerate(piano):
        stdscr.addstr(y, 0, line)

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
