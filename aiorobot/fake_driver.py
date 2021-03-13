import asyncio
import math
import threading
import time
import uuid
from contextlib import asynccontextmanager
from queue import SimpleQueue
from typing import NamedTuple

import pyglet

from . import protocol


async def wait_sync(func):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func)


class Protocol:
    @staticmethod
    def format_command(cmd, *args):
        pid = uuid.uuid4()
        return (pid, cmd, *args), pid

    @staticmethod
    def extract_event(message):
        pid, name, *args = message
        return name, args, pid

    def __getattr__(self, key):
        return getattr(protocol, key)


class Queue(SimpleQueue):
    closed = False
    async def get(self, **kwargs):
        super_get = super().get
        if kwargs:
            return await wait_sync(lambda: super_get(**kwargs))
        else:
            return await wait_sync(super_get)


class Client:
    protocol = Protocol()

    @classmethod
    async def discover(cls, **kwargs):
        return [cls()]

    def __init__(self):
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

    async def start_notify(self, callback):
        self.callback = callback
        async def _notify():
            while not self.notifq.closed:
                try:
                    msg = await self.notifq.get(timeout=1)
                except:
                    continue
                self.callback(self, msg)
        self.notify = asyncio.create_task(_notify())

    async def stop_notify(self):
        self.notifq.closed = True
        await self.notify
        self.notify = None
        self.callback = None

    async def send(self, message):
        self.cmdq.put_nowait(message)


class Event(NamedTuple):
    time: float
    notif: tuple
    action: None


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

    def add_event(delay, notif, action):
        events.append(Event(
            time.time() + delay,
            notif,
            action,
        ))

    def get_event():
        delay = 0
        event = None

        if events:
            current_time = time.time()
            if current_time >= events[0].time:
                event = events.pop(0)
                delay = current_time - event.time

        return event, delay

    def set_motors(left=0, right=0):
        nonlocal left_motor, right_motor
        left_motor, right_motor = left, right

    def update_motor(dt):
        if left_motor == right_motor:  # Run
            dist = dt * speed * left_motor
            angle = math.radians(-robot.rotation)
            robot.x += dist * math.cos(angle)
            robot.y += dist * math.sin(angle)
        elif left_motor == -right_motor:  # Rotate
            dist = dt * speed * left_motor
            angle_d = 360 * dist / (gap * math.pi)
            robot.rotation += angle_d
        else:  # General case
            motor_speed = (left_motor + right_motor) / 2
            dist = dt * speed * motor_speed
            radius = (gap / 2) * (left_motor + right_motor) / (left_motor - right_motor)
            angle = dist / radius
            abs_angle = math.radians(-robot.rotation) - math.pi/2
            robot.rotation += math.degrees(angle)
            robot.x += radius * (math.cos(abs_angle + angle) - math.cos(abs_angle))
            robot.y += radius * (math.sin(abs_angle + angle) - math.sin(abs_angle))

    def handle_command():
        if cmdq.empty():
            return

        pid, cmd, *args = cmdq.get_nowait()

        if cmd == 'set_motor_speed':
            left_speed, right_speed = args
            set_motors(
                max(min(left_speed, 100), -100) / 100,
                max(min(right_speed, 100), -100) / 100,
            )
        if cmd == 'drive_distance':
            set_motors(1, 1)
            dist, = args
            add_event(
                abs(dist) / speed,
                (pid, 'drive_distance_finished'),
                set_motors,
            )
        elif cmd == 'rotate_angle':
            ddegrees, = args
            if ddegrees < 0:
                set_motors(-1, 1)
            else:
                set_motors(1, -1)

            add_event(
                abs(gap * math.pi * ddegrees/3600) / speed,
                (pid, 'rotate_angle_finished'),
                set_motors,
            )

    def update(dt):
        event, delay = get_event()
        if delay:
            dt -= delay

        if left_motor or right_motor:
            update_motor(dt)

        if event:
            event.action()
            notifq.put_nowait(event.notif)

        handle_command()

    pyglet.clock.schedule_interval(update, 0.01)
    on_draw()
    pyglet.app.run()
