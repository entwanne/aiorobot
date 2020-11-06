import asyncio
from contextlib import asynccontextmanager

from . import driver
from . import protocol

async def discover(timeout=1):
    devices = await driver.discover_devices(timeout=timeout)
    return [Robot(device) for device in devices]


@asynccontextmanager
async def get_robot(timeout=1):
    robots = await discover(timeout=timeout)
    async with robots[0] as robot:
        yield robot


async def run_robot(timeout=1, init=True, **callbacks):
    async with get_robot(timeout=timeout) as robot:
        if init:
            await robot.events.enable_all()
        robot.events.set_callbacks(**callbacks)
        await robot.events.process()


class Robot:
    def __init__(self, device):
        self._device = device
        self._driver = None
        self._ctx = None

        self.events = None
        self.motor = None
        self.marker = None
        self.eraser = None
        self.led = None
        self.music = None

    async def __aenter__(self):
        self._ctx = driver.get_driver(self._device)
        self._driver = await self._ctx.__aenter__()

        self.events = RobotEvents(self)
        self.motor = RobotMotor(self)
        self.marker = RobotMarker(self)
        self.eraser = RobotEraser(self)
        self.color = RobotColor(self)
        self.led = RobotLED(self)
        self.music = RobotMusic(self)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._ctx.__aexit__(exc_type, exc, tb)
        self._ctx = None
        self._driver = None

    async def get_name(self):
        return await self._driver.get_name()

    async def set_name(self, name):
        await self._driver.set_name(name)

    async def get_version(self):
        return await self._driver.get_version(driver.Board.MAIN)

    async def get_color_board_version(self):
        return await self._driver.get_version(driver.Board.COLOR)

    async def get_serial_number(self):
        return await self._driver.get_serial_number()

    async def get_sku(self):
        return await self._driver.get_sku()

    async def get_battery_level(self):
        return await self._driver.get_battery_level()

    async def cancel(self):
        await self._driver.cancel()

    async def disconnect(self):
        await self._driver.disconnect()


class _RobotComponent:
    def __init__(self, robot):
        self._robot = robot
        self._driver = robot._driver


class RobotEvents(_RobotComponent):
    def __init__(self, robot):
        super().__init__(robot)
        self._callbacks = {}

    async def _iter_events(self, loop):
        async for event in self._driver.get_events(loop=loop):
            callback = self._callbacks.get(event.event_name, None)
            if callback is not None:
                asyncio.create_task(callback(self._robot, *event))

            yield event

    def set_callback(self, event_type, callback):
        if isinstance(event_type, driver._Event):
            event_name = event_type.event_name
        else:
            event_name = event_type

        self._callbacks[event_name] = callback

    def set_callbacks(self, **callbacks):
        self._callbacks.update(callbacks)

    async def __aiter__(self):
        "Iterate over all events, waiting for new ones"
        async for event in self._iter_events(True):
            yield event

    @property
    async def current(self):
        "Iterate over currently received events"
        async for event in self._iter_events(False):
            yield event

    async def process(self, wait=True, loop=True):
        """
        Process events (invoking callbacks)

        blocking if wait is true
        wait for new events if loop is true
        """
        if not wait:
            return asyncio.create_task(self.process(loop=loop))

        async for event in self._iter_events(loop):
            pass

    async def enable(self, devices):
        await self._driver.enable_events(devices)

    async def enable_all(self):
        await self.enable(driver.Devices.ALL)

    async def disable(self, devices):
        await self._driver.disable_events(devices)

    async def disable_all(self):
        await self.enable(driver.Devices.ALL)

    async def get_enabled(self):
        return await self._driver.get_enabled_events()


class RobotMotor(_RobotComponent):
    async def set_speed(self, left, right):
        await self._driver.set_motor_speed(left, right)

    async def set_left_speed(self, speed):
        await self._driver.set_left_motor_speed(speed)

    async def set_right_speed(self, speed):
        await self._driver.set_right_motor_speed(speed)

    async def disable_gravity_compensation(self):
        await self._driver.set_gravity_compensation(driver.GravityState.OFF, 0)

    async def enable_gravity_compensation(self, amount=500):
        await self._driver.set_gravity_compensation(driver.GravityState.ON, amount)

    async def enable_gravity_compensation_on_marker(self, amount=500):
        await self._driver.set_gravity_compensation(driver.GravityState.ON_MARKER, amount)

    async def drive(self, distance, wait=True):
        await self._driver.drive_distance(distance, wait=wait)

    async def rotate(self, angle, wait=True):
        await self._driver.rotate_angle(angle, wait=wait)

    async def drive_arc(self, angle: int, radius: int, wait=True):
        await self._driver.drive_arc(angle, radius, wait=wait)


class RobotMarker(_RobotComponent):
    async def down(self, wait=True):
        await self._driver.set_marker_eraser(driver.MarkerEraserPosition.MARKER_DOWN, wait=wait)

    async def up(self, wait=True):
        await self._driver.set_marker_eraser(driver.MarkerEraserPosition.UP, wait=wait)


class RobotEraser(_RobotComponent):
    async def down(self, wait=True):
        await self._driver.set_marker_eraser(driver.MarkerEraserPosition.ERASER_DOWN, wait=wait)

    async def up(self, wait=True):
        await self._driver.set_marker_eraser(driver.MarkerEraserPosition.UP, wait=wait)


class RobotColor(_RobotComponent):
    async def get(self, sensor, lightning, format):
        return await self._driver.get_color_data(sensor, lightning, format)


class RobotLED(_RobotComponent):
    def __init__(self, robot):
        super().__init__(robot)
        self._anim = None
        self._color = (0, 0, 0)

    @property
    def color(self):
        return self._color

    async def _update(self, anim, color=None):
        self._anim = anim
        if color is not None:
            self._color = color

        r, g, b = self._color
        await self._driver.set_led_animation(self._anim, r, g, b)

    async def off(self):
        await self._update(driver.LEDAnimation.OFF)

    async def on(self, color=None):
        await self._update(driver.LEDAnimation.ON, color)

    async def blink(self, color=None):
        await self._update(driver.LEDAnimation.BLINK, color)

    async def spin(self, color=None):
        await self._update(driver.LEDAnimation.SPIN, color)


class RobotMusic(_RobotComponent):
    # + handle notes

    async def play(self, frequency, duration=1000):
        await self._driver.play_note(frequency, duration)

    async def stop(self):
        await self._driver.stop_note()

    async def say(self, phrase, wait=True):
        # + handle long phrase
        await self._driver.say_phrase(phrase, wait=wait)
