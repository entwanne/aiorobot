import asyncio
import enum

from . import protocol


class Board(enum.Enum):
    MAIN = 0xA5
    COLOR = 0xC6


class GravityState(enum.Enum):
    OFF = 0
    ON = 1
    ON_MARKER = 2


class Motor(enum.Enum):
    LEFT = 0
    RIGHT = 1
    MARKER = 2


class MarkerEraserPosition(enum.Enum):
    UP = 0
    MARKER_DOWN = 1
    ERASER_DOWN = 2


class ColorSensor(enum.Enum):
    LEFT = 0
    CENTER_LEFT = 1
    CENTER_RIGHT = 2
    RIGHT = 3


class ColorLightning(enum.Enum):
    OFF = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    ALL = 4


class ColorFormat(enum.Enum):
    ADC = 0
    MV = 1


class LEDAnimation(enum.Enum):
    OFF = 0
    ON = 1
    BLINK = 2
    SPIN = 3


class Bumper(enum.Flag):
    NO = 0
    RIGHT = 0x40
    LEFT = 0x80
    BOTH = 0xC0


class _Event(tuple):
    event_name = 'event'
    __fields__ = ()
    _register = {}

    def __new__(cls, *args):
        args = cls._parse_args(*args)
        return super().__new__(cls, args)

    def __init_subclass__(cls):
        import inspect
        import operator
        if cls.__fields__ is None:
            sig = inspect.signature(cls._parse_args)
            cls.__fields__ = tuple(sig.parameters)

        for i, field in enumerate(cls.__fields__):
            setattr(cls, field, property(operator.itemgetter(i)))

        cls._register[cls.event_name] = cls

    @classmethod
    def from_name(cls, event_name, *args):
        return cls._register[event_name](*args)

    @staticmethod
    def _parse_args():
        return ()

    def __repr__(self):
        args = ', '.join(f'{name}={value}' for name, value in zip(self.__fields__, self))
        return f'{self.__class__.__qualname__}({args})'


class StartedEvent(_Event):
    event_name = 'started'


class VersionReponse(_Event):
    event_name = 'version'
    __fields__ = None

    @staticmethod
    def _parse_args(board, fw_maj, fw_min, hw_maj, hw_min, boot_maj, boot_min, proto_maj, proto_min):
        return Board(board), fw_maj, fw_min, hw_maj, hw_min, boot_maj, boot_min, proto_maj, proto_min


class NameResponse(_Event):
    event_name = 'name'
    __fields__ = None

    @staticmethod
    def _parse_args(name):
        return name.decode(protocol.encoding),


class StoppedEvent(_Event):
    event_name = 'stopped'


class EnabledEventsResponse(_Event):
    event_name = 'enabled_events'
    __fields__ = None

    @staticmethod
    def _parse_args(data):
        return data,


class SerialNumberResponse(_Event):
    event_name = 'serial_number'
    __fields__ = None

    @staticmethod
    def _parse_args(serial_number):
        return serial_number.decode(protocol.encoding),


class SKUEvent(_Event):
    event_name = 'sku'
    __fields__ = None

    @staticmethod
    def _parse_args(sku):
        return sku.decode(protocol.encoding),


class DriveDistanceResponse(_Event):
    event_name = 'drive_distance_finished'


class RotateAngleResponse(_Event):
    event_name = 'rotate_angle_finished'


class DriveArcResponse(_Event):
    event_name = 'drive_arc_finished'


class MotorStallEvent(_Event):
    event_name = 'motor_stall'
    __fields__ = None

    @staticmethod
    def _parse_args(timestamp, motor, cause):
        return timestamp, Motor(motor), cause


class MarkerEraserResponse(_Event):
    event_name = 'marker_erase_finished'
    __fields__ = None

    @staticmethod
    def _parse_args(position):
        return MarkerEraserPosition(position),


class ColorResponse(_Event):
    event_name = 'color_response'
    __fields__ = None

    @staticmethod
    def _parse_args(a, b, c, d, e, f, g, h):
        return a, b, c, d, e, f, g, h


class ColorEvent(_Event):
    event_name = 'color_event'
    __fields__ = None

    @staticmethod
    def _parse_args(data):
        return data,


class PlayNoteResponse(_Event):
    event_name = 'play_note_finished'


class SayPhraseResponse(_Event):
    event_name = 'say_phrase_finished'


class BumperEvent(_Event):
    event_name = 'bumper_event'
    __fields__ = None

    @staticmethod
    def _parse_args(timestamp, state):
        return timestamp, Bumper(state)


class LightEvent(_Event):
    event_name = 'light_event'
    __fields__ = None

    @staticmethod
    def _parse_args(timestamp, state, left, right):
        return timestamp, state, left, right


class BatteryEvent(_Event):
    event_name = 'battery_event'
    __fields__ = None

    @staticmethod
    def _parse_args(timestamp, voltage, percent):
        return timestamp, voltage, percent


class BatteryResponse(_Event):
    event_name = 'battery_response'
    __fields__ = None

    @staticmethod
    def _parse_args(timestamp, voltage, percent):
        return timestamp, voltage, percent


class TouchEvent(_Event):
    event_name = 'touch_event'
    __fields__ = None

    @staticmethod
    def _parse_args(timestamp, state):
        return timestamp, state


class CliffEvent(_Event):
    event_name = 'cliff_event'
    __fields__ = None

    @staticmethod
    def _parse_args(timestamp, cliff, sensor, threshold):
        return timestamp, cliff, sensor, threshold


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

        event = _Event.from_name(name, *args)
        if waiter is None:
            self._event_queue.put_nowait(event)
        else:
            self._responses[hdr] = event
            waiter.set()

    async def get_events(self, loop=False):
        # + handle disconnection
        q = self._event_queue
        while loop or not q.empty():
            event = await q.get()
            q.task_done()
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
        await self._send('cancel', wait_response=False)

    async def disconnect(self):
        await self._send('cancel', wait_response=False)

    async def enable_events(self, bitfield: bytes):
        await self._send('enable_events', bitfield, wait_response=False)

    async def disable_events(self, bitfield: bytes):
        await self._send('disable_events', bitfield, wait_response=False)

    async def get_enabled_events(self):
        bitfield, = await self._send('get_enabled_events')
        return bitfield

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
