import asyncio
import enum
from contextlib import asynccontextmanager

import bleak

from . import protocol
from .events import Event, StartedEvent
from .types import *


async def discover_devices(timeout=1):
    return await bleak.discover(
        timeout=timeout,
        filters={'UUIDs': [protocol.root_identifier_uuid]},
    )


def get_client(device):
    return bleak.BleakClient(device)


def get_characteristics(client):
    uart = client.services.get_service(protocol.uart_service_uuid)
    rx = uart.get_characteristic(protocol.rx_char_uuid)
    assert 'write' in rx.properties
    tx = uart.get_characteristic(protocol.tx_char_uuid)
    assert 'notify' in tx.properties
    return rx, tx


@asynccontextmanager
async def get_driver(device):
    async with get_client(device) as client:
        rx, tx = get_characteristics(client)
        async with Driver(client, rx, tx) as driver:
            yield driver


class Driver:
    def __init__(self, client, rx, tx):
        self.client = client
        self.rx = rx
        self.tx = tx
        self._responses = {}
        self._event_queue = asyncio.Queue()
        self._event_queue.put_nowait(StartedEvent())

    async def __aenter__(self):
        await self.client.start_notify(self.tx, self._notification)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.stop_notify(self.tx)

    async def _send(self, cmd, *args, wait_response=True):
        message, hdr = protocol.format_command(cmd, *args)
        if wait_response:
            self._responses[hdr] = waiter = asyncio.Event()
        await self.client.write_gatt_char(self.rx, message)
        if wait_response:
            await waiter.wait()
            return self._responses.pop(hdr)

    def _notification(self, _sender, message):
        name, args, hdr = protocol.extract_event(message)
        waiter = self._responses.pop(hdr, None)

        event = Event.parse(name, *args)
        if waiter is None:
            self._event_queue.put_nowait(event)
        else:
            self._responses[hdr] = event
            waiter.set()

    async def get_events(self, loop=False):
        # + handle disconnection from robot
        q = self._event_queue
        while loop or not q.empty():
            event = await q.get()
            q.task_done()
            if event is None:
                break
            yield event

    async def get_version(self, board: Board):
        version = await self._send('get_version', board.value)
        return version

    async def set_name(self, name: str):
        await self._send('set_name', name.encode(protocol.encoding), wait_response=False)

    async def get_name(self):
        name, = await self._send('get_name')
        return name

    async def cancel(self):
        # + reset waiters to cancel jobs?
        await self._send('cancel', wait_response=False)

    async def disconnect(self):
        await self._send('disconnect', wait_response=False)
        self._event_queue.put_nowait(None)

    async def enable_events(self, devices: Devices):
        bitfield = devices.to_bytes()
        await self._send('enable_events', bitfield, wait_response=False)

    async def disable_events(self, devices: Devices):
        bitfield = devices.to_bytes()
        await self._send('disable_events', bitfield, wait_response=False)

    async def get_enabled_events(self):
        bitfield, = await self._send('get_enabled_events')
        return Devices.from_bytes(bitfield)

    async def get_serial_number(self):
        serial, = await self._send('get_serial_number')
        return serial

    async def get_sku(self):
        sku, = await self._send('get_sku')
        return sku

    async def set_motor_speed(self, left: int, right: int):
        await self._send('set_motor_speed', left, right, wait_response=False)

    async def set_left_motor_speed(self, speed: int):
        await self._send('set_left_motor_speed', speed, wait_response=False)

    async def set_right_motor_speed(self, speed: int):
        await self._send('set_right_motor_speed', speed, wait_response=False)

    async def set_gravity_compensation(self, state: GravityState, amount: int):
        await self._send('set_gravity_compensation', state.value, amount, wait_response=False)

    async def drive_distance(self, dist: int, wait=True):
        await self._send('drive_distance', dist, wait_response=wait)

    async def rotate_angle(self, angle: int, wait=True):
        await self._send('rotate_angle', angle, wait_response=wait)

    async def drive_arc(self, angle: int, radius: int, wait=True):
        await self._send('drive_arc', angle, radius, wait_response=wait)

    async def set_marker_eraser(self, position: MarkerEraserPosition, wait=True):
        ret = await self._send('set_marker_eraser', position.value, wait_response=wait)
        if wait:
            position, = ret
            return MarkerEraserPosition(position)

    async def get_color_data(self, sensor: ColorSensor, lightning: ColorLightning, format: ColorFormat):
        return await self._send('get_color_data', sensor.value, lightning.value, format.value)

    async def set_led_animation(self, anim: LEDAnimation, red: int, green: int, blue: int):
        await self._send('set_led_animation', anim.value, red, green, blue, wait_response=False)

    async def play_note(self, frequency: int, duration: int, wait=True):
        await self._send('play_note', frequency, duration, wait_response=wait)

    async def stop_note(self):
        await self._send('stop_note', wait_response=False)

    async def say_phrase(self, phrase: str, wait=True):
        await self._send('say_phrase', phrase.encode(protocol.encoding), wait_response=wait)

    async def get_battery_level(self):
        _, voltage, rate = await self._send('get_battery_level')
        return voltage, rate
