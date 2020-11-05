import asyncio
from contextlib import asynccontextmanager

import bleak

from . import driver
from . import protocol

async def discover(timeout=1):
    devices = await bleak.discover(
        timeout=timeout,
        filters={'UUIDs': [protocol.root_identifier_uuid]},
    )
    return [Robot(device) for device in devices]


@asynccontextmanager
async def get_robot(timeout=1):
    robots = await discover(timeout=timeout)
    async with robots[0] as robot:
        yield robot


async def run_robot(timeout=1, **callbacks):
    async with get_robot(timeout=timeout) as robot:
        robot.events.set_callbacks(**callbacks)
        await robot.events.process()


class Robot:
    def __init__(self, device):
        self._device = device
        self._client = None
        self._driver = None

        self.events = None
        self.motor = None
        self.marker = None
        self.eraser = None
        self.led = None
        self.music = None

    def _get_characteristics(self):
        uart = self._client.services.get_service(protocol.uart_service_uuid)
        rx = uart.get_characteristic(protocol.rx_char_uuid)
        assert 'write' in rx.properties
        tx = uart.get_characteristic(protocol.tx_char_uuid)
        assert 'notify' in tx.properties
        return rx, tx

    async def __aenter__(self):
        self._client = bleak.BleakClient(self._device)
        await self._client.__aenter__()

        rx, tx = self._get_characteristics()
        self._driver = driver.Driver(self._client, rx, tx)
        await self._driver.__aenter__()

        self.events = RobotEvents(self)
        self.motor = RobotMotor(self)
        self.marker = RobotMarker(self)
        self.eraser = RobotEraser(self)
        self.led = RobotLED(self)
        self.music = RobotMusic(self)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._driver.__aexit__(exc_type, exc, tb)
        self._driver = None
        await self._client.__aexit__(exc_type, exc, tb)
        self._client = None

    async def get_name(self):
        return await self._driver.get_name()

    async def set_name(self, name):
        await self._driver.set_name(name)

    async def get_main_board_version(self):
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
        await self._driver.drive_distance(distance, wait=True)

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
