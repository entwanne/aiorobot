import asyncio
import threading
import time
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
    closed = False
    async def get(self, **kwargs):
        super_get = super().get
        if kwargs:
            return await wait_sync(lambda: super_get(**kwargs))
        else:
            return await wait_sync(super_get)


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
    robot = pyglet.shapes.Rectangle(100, 500, 25, 25, color=(55, 55, 255))

    speed = 50 # 50 pixels per second
    angle = 1+0j
    events = []

    @window.event
    def on_draw():
        window.clear()
        bg.draw()
        robot.draw()

    def update(dt):
        nonlocal angle
        if events:
            pid, t = events.pop(0)
            if time.time() < t:
                dz = angle * dt * speed
                #robot.x += dt * speed
                robot.x += dz.real
                robot.y += dz.imag
                events.append((pid, t))
            else:
                tx.put_nowait((pid, 'drive_distance_finished'))

        if rx.empty():
            return

        pid, cmd, *args = rx.get_nowait()
        if cmd == 'drive_distance':
            dist, = args
            events.append((pid, time.time() + dist / speed))
        elif cmd == 'rotate_angle':
            import cmath
            ddegrees, = args
            angle *= cmath.exp(-ddegrees * cmath.pi / 1800 * 1j)
            tx.put_nowait((pid, 'rotate_angle_finished'))

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
        async def _notify():
            while not tx.closed:
                try:
                    msg = await tx.get(timeout=1)
                except:
                    continue
                self.callback(self, msg)
        self.notify = asyncio.create_task(_notify())

    async def stop_notify(self, tx):
        tx.closed = True
        await self.notify
        self.notify = None
        self.callback = None

    async def write_gatt_char(self, rx, message):
        rx.put_nowait(message)


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
