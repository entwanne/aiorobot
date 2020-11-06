import inspect
import operator

from . import protocol
from .types import *


class Event(tuple):
    event_name = 'event'
    __fields__ = ()
    _register = {}

    def __new__(cls, *args):
        return super().__new__(cls, args)

    def __init_subclass__(cls):
        if cls.__fields__ is Ellipsis:
            sig = inspect.signature(cls._parse_args)
            cls.__fields__ = tuple(sig.parameters)

        if cls.__fields__:
            for i, field in enumerate(cls.__fields__):
                setattr(cls, field, property(operator.itemgetter(i)))

        cls._register[cls.event_name] = cls

    @classmethod
    def parse(cls, event_name, *args):
        event_cls = cls._register[event_name]
        event_args = event_cls._parse_args(*args)
        return event_cls(*event_args)

    @staticmethod
    def _parse_args():
        return ()

    def __repr__(self):
        if self.__fields__ is None:
            args = ', '.join(map(str, self))
        else:
            args = ', '.join(f'{name}={value}' for name, value in zip(self.__fields__, self))
        return f'{self.__class__.__qualname__}({args})'


class StartedEvent(Event):
    event_name = 'started'


class VersionReponse(Event):
    event_name = 'version'
    __fields__ = ('board', 'firmware', 'hardware', 'bootloader', 'protocol')

    @staticmethod
    def _parse_args(board, fw_maj, fw_min, hw_maj, hw_min, boot_maj, boot_min, proto_maj, proto_min):
        firmware = Version.parse(f'{fw_maj}.{fw_min}')
        hardware = Version.parse(f'{hw_maj}.{hw_min}')
        bootloader = Version.parse(f'{boot_maj}.{boot_min}')
        protocol = Version.parse(f'{proto_maj}.{proto_min}')
        return Board(board), firmware, hardware, bootloader, protocol


class NameResponse(Event):
    event_name = 'name'
    __fields__ = ...

    @staticmethod
    def _parse_args(name):
        return name.decode(protocol.encoding),


class StoppedEvent(Event):
    event_name = 'stopped'


class EnabledEventsResponse(Event):
    event_name = 'enabled_events'
    __fields__ = ...

    @staticmethod
    def _parse_args(data):
        return data,


class SerialNumberResponse(Event):
    event_name = 'serial_number'
    __fields__ = ...

    @staticmethod
    def _parse_args(serial_number):
        return serial_number.decode(protocol.encoding),


class SKUEvent(Event):
    event_name = 'sku'
    __fields__ = ...

    @staticmethod
    def _parse_args(sku):
        return sku.decode(protocol.encoding),


class DriveDistanceResponse(Event):
    event_name = 'drive_distance_finished'


class RotateAngleResponse(Event):
    event_name = 'rotate_angle_finished'


class DriveArcResponse(Event):
    event_name = 'drive_arc_finished'


class MotorStallEvent(Event):
    event_name = 'motor_stall'
    __fields__ = ...

    @staticmethod
    def _parse_args(timestamp, motor, cause):
        return timestamp, Motor(motor), MotorStallCause(cause)


class MarkerEraserResponse(Event):
    event_name = 'marker_erase_finished'
    __fields__ = ...

    @staticmethod
    def _parse_args(position):
        return MarkerEraserPosition(position),


class ColorResponse(Event):
    event_name = 'color_response'
    __fields__ = None

    @staticmethod
    def _parse_args(*data):
        return data


class ColorEvent(Event):
    event_name = 'color_event'
    __fields__ = None

    @staticmethod
    def _parse_args(data):
        data = ((b >> 4 & 0b1111, b & 0b1111) for b in data)
        colors = [Color(i) for d in data for i in d]
        return colors


class PlayNoteResponse(Event):
    event_name = 'play_note_finished'


class SayPhraseResponse(Event):
    event_name = 'say_phrase_finished'


class BumperEvent(Event):
    event_name = 'bumper_event'
    __fields__ = ...

    @staticmethod
    def _parse_args(timestamp, state):
        return timestamp, Bumper(state)


class LightEvent(Event):
    event_name = 'light_event'
    __fields__ = ...

    @staticmethod
    def _parse_args(timestamp, state, left, right):
        return timestamp, LightBright(state), left, right


class BatteryEvent(Event):
    event_name = 'battery_event'
    __fields__ = ...

    @staticmethod
    def _parse_args(timestamp, voltage, percent):
        return timestamp, voltage, percent


class BatteryResponse(Event):
    event_name = 'battery_response'
    __fields__ = ...

    @staticmethod
    def _parse_args(timestamp, voltage, percent):
        return timestamp, voltage, percent


class TouchEvent(Event):
    event_name = 'touch_event'
    __fields__ = ...

    @staticmethod
    def _parse_args(timestamp, state):
        return timestamp, Sensor(state)


class CliffEvent(Event):
    event_name = 'cliff_event'
    __fields__ = ...

    @staticmethod
    def _parse_args(timestamp, cliff, sensor, threshold):
        return timestamp, Cliff(cliff), sensor, threshold
