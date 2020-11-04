import asyncio

from protocol import extract_event
from protocol import format_command


class Driver:
    encoding = 'utf-8'

    def __init__(self, client, rx, tx):
        self.client = client
        self.rx = rx
        self.tx = tx
        self._responses = {}
        self._event_queue = asyncio.Queue()

    async def __aenter__(self):
        await self.client.start_notify(self.tx, self._notification)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.stop_notify(self.tx)

    async def _send(self, cmd, *args, wait_response=True):
        message, hdr = format_command(cmd, *args)
        if wait_response:
            self._responses[hdr] = waiter = asyncio.Event()
        await self.client.write_gatt_char(self.rx, message)
        if wait_response:
            await waiter.wait()
            return self._responses.pop(hdr)

    def _notification(self, _sender, message):
        name, args, hdr = extract_event(message)
        waiter = self._responses.pop(hdr, None)

        if waiter is None:
            self._event_queue.put_nowait((name, args, hdr))
        else:
            self._responses[hdr] = args
            waiter.set()

    async def get_events(self, loop=False):
        q = self._event_queue
        while loop or not q.empty():
            event = await q.get()
            q.task_done()
            yield event

    async def get_version(self, board):
        version = await self._send('get_version', board)
        return version

    async def set_name(self, name):
        await self._send('set_name', name.encode(self.encoding), wait_response=False)

    async def get_name(self):
        name, = await self._send('get_name')
        return name.decode(self.encoding)

    async def cancel(self):
        await self._send('cancel', wait_response=False)

    async def disconnect(self):
        await self._send('cancel', wait_response=False)

    async def enable_events(self, bitfield):
        await self._send('enable_events', bitfield, wait_response=False)

    async def disable_events(self, bitfield):
        await self._send('disable_events', bitfield, wait_response=False)

    async def get_enabled_events(self):
        bitfield, = await self._send('get_enabled_events')
        return bitfield

    async def get_serial_number(self):
        serial, = await self._send('get_serial_number')
        return serial.decode(self.encoding)

    async def get_sku(self):
        sku, = await self._send('get_sku')
        return sku.decode(self.encoding)

    async def set_motor_speed(self, left, right):
        await self._send('set_motor_speed', left, right, wait_response=False)

    async def set_left_motor_speed(self, speed):
        await self._send('set_left_motor_speed', speed, wait_response=False)

    async def set_right_motor_speed(self, speed):
        await self._send('set_right_motor_speed', speed, wait_response=False)

    async def set_gravity_compensation(self, state, amount):
        await self._send('set_gravity_compensation', state, amount, wait_response=False)

    async def drive_distance(self, dist, wait=True):
        await self._send('drive_distance', dist, wait_response=wait)

    async def rotate_angle(self, angle, wait=True):
        await self._send('rotate_angle', angle, wait_response=wait)

    async def drive_arc(self, angle, radius, wait=True):
        await self._send('drive_arc', angle, radius, wait_response=wait)

    async def set_marker_eraser(self, position, wait=True):
        await self._send('set_marker_eraser', position, wait_response=wait)

    async def get_color_data(self, sensor, lightning, format):
        return await self._send('get_color_data', sensor, lightning, format)

    async def set_led_animation(self, anim, red, green, blue):
        await self._send('set_led_animation', anim, red, green, blue)

    async def play_note(self, frequency, duration, wait=True):
        await self._send('play_note', frequency, duration, wait_response=wait)

    async def stop_note(self):
        await self._send('stop_note', wait_response=False)

    async def say_phrase(self, phrase, wait=True):
        await self._send('say_phrase', phrase.encode(self.encoding), wait_response=wait)

    async def get_battery_level(self):
        _, voltage, rate = await self._send('get_battery_level')
        return voltage, rate
