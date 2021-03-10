import asyncio
import threading
import uuid
from contextlib import asynccontextmanager
from queue import SimpleQueue

import pyglet

#from . import protocol
from .driver import Driver as BaseDriver
from .driver import protocol
from .types import *


def format_command(cmd, *args):
    pid = uuid.uuid4()
    return (pid, cmd, *args), pid
protocol.format_command = format_command


def extract_event(message):
    pid, name, *args = message
    return name, args, pid
protocol.extract_event = extract_event


async def wait_sync(func):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func)


class Queue(SimpleQueue):
    async def get(self):
        return await wait_sync(super().get)


#queue = Queue()
rx, tx = Queue(), Queue()


async def discover_devices(timeout=0):
    return [None]


def get_client(device):
    return Client(device)


@asynccontextmanager
async def get_driver(device):
    async with get_client(device) as client:
        async with Driver(client, rx, tx) as driver:
            yield driver


def pyglet_thread():
    window = pyglet.window.Window(width=800, height=600)
    bg = pyglet.shapes.Rectangle(0, 0, 800, 600, color=(255, 255, 255))
    robot = pyglet.shapes.Rectangle(100, 100, 25, 25, color=(55, 55, 255))

    @window.event
    def on_draw():
        window.clear()
        bg.draw()
        robot.draw()

    def update(dt):
        if rx.empty():
            return
        x = rx.get_nowait()
        
        print(x)

    pyglet.clock.schedule_interval(update, 0.01)
    on_draw()
    pyglet.app.run()


class Client:
    def __init__(self, _device):
        self.callback = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def start_notify(self, tx, callback):
        self.callback = callback

    async def stop_notify(self, tx):
        self.callback = None

    async def write_gatt_char(self, rx, message):
        if self.callback is None:
            return
        rx.put_nowait(message)
        pid, cmd, *args = message
        if cmd == 'drive_distance':
            self.callback(self, (pid, 'drive_distance_finished'))
        elif cmd == 'rotate_angle':
            self.callback(self, (pid, 'rotate_angle_finished'))


class Driver(BaseDriver):
    async def __aenter__(self):
        self.thread = threading.Thread(
            target=pyglet_thread,
        )
        self.thread.start()
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await super().__aexit__(exc_type, exc, tb)
        await wait_sync(self.thread.join)

    #async def _send(self, cmd, *args, wait_response=True):
    #    print(cmd)
    #    request_id = uuid.uuid4()
    #    if cmd == 'drive_distance':
    #        print(args)

    #async def _notification(self, event_id):
    #    pass
