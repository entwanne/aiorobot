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


class FakeRobot:
    speed = 50 # 50 pixels per second
    gap = 25 # gap between wheels
    width = height = gap

    def __init__(self, x, y, batch=None):
        # speed factor (-1 to 1)
        self.left_motor = 0
        self.right_motor = 0
        self.marker = False

        self.batch = batch
        self.bg_group = pyglet.graphics.OrderedGroup(1)
        self.fg_group = pyglet.graphics.OrderedGroup(2)

        self.sprite = pyglet.shapes.Rectangle(
            x, y, self.width, self.height,
            color=(55, 55, 255),
            batch=self.batch,
            group=self.fg_group,
        )
        self.sprite.anchor_position = (self.width/2, self.height/2)

        self.segments = []

    @property
    def position(self):
        return self.sprite.position

    @property
    def x(self):
        return self.sprite.x

    @property
    def y(self):
        return self.sprite.y

    def move(self, dx, dy):
        self.sprite.x += dx
        self.sprite.y += dy

    @property
    def angle(self):
        return math.radians(-self.sprite.rotation)

    def rotate(self, angle):
        self.sprite.rotation += math.degrees(angle)

    def set_motors(self, left=0, right=0):
        self.left_motor, self.right_motor = left, right

    def walk(self, dt):
        if not self.left_motor and not self.right_motor:
            return

        old_position = self.position

        if self.left_motor == self.right_motor:  # Run
            dist = dt * self.speed * self.left_motor
            angle = self.angle
            self.move(dist * math.cos(angle), dist * math.sin(angle))
        elif self.left_motor == -self.right_motor:  # Rotate
            dist = dt * self.speed * self.left_motor
            angle = 2 * dist / self.gap # 2pi * dist / (gap * pi)
            self.rotate(angle)
        else:  # General case
            motor_speed = (self.left_motor + self.right_motor) / 2
            dist = dt * self.speed * motor_speed
            radius = (self.gap / 2) * (self.left_motor + self.right_motor) / (self.left_motor - self.right_motor)
            angle = dist / radius
            abs_angle = self.angle - math.pi/2
            self.rotate(angle)
            self.move(
                radius * (math.cos(abs_angle + angle) - math.cos(abs_angle)),
                radius * (math.sin(abs_angle + angle) - math.sin(abs_angle)),
            )

        if self.marker and self.position != old_position:
            self.segments.append(pyglet.shapes.Line(
                *old_position, *self.position, color=(0, 0, 0),
                batch=self.batch, group=self.bg_group,
            ))


def pyglet_thread(cmdq, notifq):
    window = pyglet.window.Window(width=800, height=600)
    batch = pyglet.graphics.Batch()
    bg = pyglet.shapes.Rectangle(
        0, 0, 800, 600, color=(255, 255, 255),
        batch=batch, group=pyglet.graphics.OrderedGroup(0),
    )
    robot = FakeRobot(100, 500, batch=batch)

    events = []

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

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

    def handle_command():
        if cmdq.empty():
            return

        pid, cmd, *args = cmdq.get_nowait()

        if cmd == 'set_motor_speed':
            left_speed, right_speed = args
            robot.set_motors(
                max(min(left_speed, 100), -100) / 100,
                max(min(right_speed, 100), -100) / 100,
            )
        elif cmd == 'drive_distance':
            robot.set_motors(1, 1)
            dist, = args
            add_event(
                abs(dist) / robot.speed,
                (pid, 'drive_distance_finished'),
                robot.set_motors,
            )
        elif cmd == 'rotate_angle':
            ddegrees, = args
            if ddegrees < 0:
                robot.set_motors(-1, 1)
            else:
                robot.set_motors(1, -1)

            add_event(
                abs(robot.gap * math.pi * ddegrees/3600) / robot.speed,
                (pid, 'rotate_angle_finished'),
                robot.set_motors,
            )
        elif cmd == 'drive_arc':
            ddegrees, radius = args
            #angle = math.radians(ddegrees / 10)
            '''
            circ = 2 * math.pi * radius
            dist = circ * angle / (2 * math.pi)
            x = radius * 2 / robot.gap
            robot.set_motors(1, 1)
            add_event(
                abs(dist) / robot.speed,
                (pid, 'drive_arc_finished'),
                robot.set_motors,
            )
            '''
            left_speed = (radius + robot.gap / 2) / radius
            right_speed = (radius - robot.gap / 2) / radius
            abs_speed = max(abs(left_speed), abs(right_speed))
            left_speed /= abs_speed
            right_speed /= abs_speed
            robot.set_motors(left_speed, right_speed)


            speed = abs(left_speed + right_speed) / 2
            #speed = (abs(left_speed) + abs(right_speed)) / 2
            circ = 2 * math.pi * abs(radius)
            dist = circ * abs(ddegrees) / 3600
            add_event(
                dist / speed / robot.speed,
                (pid, 'drive_arc_finished'),
                robot.set_motors,
            )
        elif cmd == 'set_marker_eraser':
            pos, = args
            if pos == 0:
                robot.marker = False
            elif pos == 1:
                robot.marker = True
            notifq.put_nowait((pid, 'marker_eraser_finished', pos))
        else:
            print(f'Unknown command {cmd!r}')

    def update(dt):
        event, delay = get_event()
        if delay:
            dt -= delay

        robot.walk(dt)

        if event:
            event.action()
            notifq.put_nowait(event.notif)

        handle_command()

    pyglet.clock.schedule_interval(update, 0.01)
    on_draw()
    pyglet.app.run()
