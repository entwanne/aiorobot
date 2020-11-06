import asyncio
import threading
from queue import SimpleQueue

from aiorobot import run
from aiorobot.examples.callbacks import bump


class Queue(SimpleQueue):
    async def get(self):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, super().get)


def run_thread(*args, **kwargs):
    thread = threading.Thread(
        target=run,
        args=args,
        kwargs=kwargs,
    )
    thread.start()
    return thread


queue = Queue()


async def start(robot):
    while True:
        cmd = await queue.get()
        if not cmd:
            break

        if cmd == 'forward':
            await robot.motor.set_speed(100, 100)
        if cmd == 'backward':
            await robot.motor.set_speed(-100, -100)
        elif cmd == 'stop':
            await robot.motor.set_speed(0, 0)

    await robot.disconnect()


def main():
    thread = run_thread(
        started=start,
        bumper_event=bump,
    )
    try:
        print('type "forward" to go forward, "backward" to go backward and "stop" to stop')
        for cmd in iter(lambda: input('> '), ''):
            queue.put_nowait(cmd)
    finally:
        queue.put_nowait(None)
        thread.join()


if __name__ == '__main__':
    main()
