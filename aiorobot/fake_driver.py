import asyncio
import math
import threading
import time
import uuid
from contextlib import asynccontextmanager
from queue import SimpleQueue

import pyglet

from .driver import Driver
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


async def discover_devices(timeout=0):
    return [None]


def get_client(device):
    return Client(device)


@asynccontextmanager
async def get_driver(device):
    async with get_client(device) as client:
        async with Driver(client, None, None) as driver:
            yield driver


def pyglet_thread(cmdq, notifq):
    window = pyglet.window.Window(width=800, height=600)
    bg = pyglet.shapes.Rectangle(0, 0, 800, 600, color=(255, 255, 255))
    robot = pyglet.shapes.Rectangle(100, 500, 25, 25, color=(55, 55, 255))
    robot.anchor_position = (12.5, 12.5)

    speed = 50 # 50 pixels per second
    left_motor = right_motor = 0 # speed factor (-1 to 1)
    gap = robot.height # gap between wheels
    events = []

    @window.event
    def on_draw():
        window.clear()
        bg.draw()
        robot.draw()

    @window.event
    def on_expose():
        pass

    def update(dt):
        nonlocal left_motor, right_motor

        if left_motor or right_motor:
            event = None
            if events:
                current_time = time.time()
                if current_time >= events[0][0]:
                    t, event = events.pop(0)
                    dt -= current_time - t

            # Run
            if left_motor == right_motor:
                dist = dt * speed * left_motor
                angle = math.radians(-robot.rotation)
                robot.x += dist * math.cos(angle)
                robot.y += dist * math.sin(angle)
            # Rotate
            elif left_motor == -right_motor:
                dist = dt * speed * left_motor
                angle_d = 360 * dist / (gap * math.pi)
                robot.rotation += angle_d
            # General case
            else:
                motor_speed = (left_motor + right_motor) / 2
                dist = dt * speed * motor_speed
                radius = (gap / 2) * (left_motor + right_motor) / (left_motor - right_motor)
                angle = dist / radius
                abs_angle = math.radians(-robot.rotation) - math.pi/2
                robot.rotation += math.degrees(angle)
                robot.x += radius * (math.cos(abs_angle + angle) - math.cos(abs_angle))
                robot.y += radius * (math.sin(abs_angle + angle) - math.sin(abs_angle))

            # Stop event
            if event:
                left_motor = right_motor = 0
                notifq.put_nowait(event)

        if cmdq.empty():
            return

        pid, cmd, *args = cmdq.get_nowait()

        if cmd == 'set_motor_speed':
            left_speed, right_speed = args
            left_motor = max(min(left_speed, 100), -100) / 100
            right_motor = max(min(right_speed, 100), -100) / 100
        if cmd == 'drive_distance':
            left_motor = right_motor = 1
            dist, = args
            event = (pid, 'drive_distance_finished')
            events.append((time.time() + abs(dist) / speed, event))
        elif cmd == 'rotate_angle':
            ddegrees, = args
            if ddegrees < 0:
                left_motor, right_motor = -1, 1
            else:
                left_motor, right_motor = 1, -1

            dist = abs(gap * math.pi * ddegrees/3600)
            event = (pid, 'rotate_angle_finished')
            events.append((time.time() + dist / speed, event))

    pyglet.clock.schedule_interval(update, 0.01)
    on_draw()
    pyglet.app.run()


class Client:
    def __init__(self, _device):
        self.callback = None
        self.cmdq = Queue()
        self.notifq = Queue()

    async def __aenter__(self):
        self.thread = threading.Thread(
            target=pyglet_thread,
            kwargs={'cmdq': self.cmdq, 'notifq': self.notifq},
        )
        self.thread.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await wait_sync(self.thread.join)

    async def start_notify(self, _tx, callback):
        self.callback = callback
        async def _notify():
            while not self.notifq.closed:
                try:
                    msg = await self.notifq.get(timeout=1)
                except:
                    continue
                self.callback(self, msg)
        self.notify = asyncio.create_task(_notify())

    async def stop_notify(self, _tx):
        self.notifq.closed = True
        await self.notify
        self.notify = None
        self.callback = None

    async def write_gatt_char(self, _rx, message):
        self.cmdq.put_nowait(message)
