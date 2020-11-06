import enum


class Board(enum.Enum):
    MAIN = 0xA5
    COLOR = 0xC6


class Version(tuple):
    def __new__(cls, *version):
        return super().__new__(cls, version)

    @classmethod
    def parse(cls, version):
        return cls(*map(int, version.split('.')))

    def __repr__(self):
        args = ', '.join(str(v) for v in self)
        return f'{self.__class__.__qualname__}({args})'

    def __str__(self):
        return '.'.join(str(v) for v in self)

    @property
    def major(self):
        return self[0]

    @property
    def minor(self):
        return self[1] if len(self) > 1 else 0


class Devices(enum.Flag):
    NONE = 0

    GENERAL = 1
    MOTORS = 1 << 1
    MARKER_ERASER = 1 << 2
    LED_LIGHTS = 1 << 3
    COLOR_SENSOR = 1 << 4
    SOUND = 1 << 5
    BUMPERS = 1 << 12
    LIGHT_SENSORS = 1 << 13
    BATTERY = 1 << 14
    TOUCH_SENSORS = 1 << 17
    CLIFF_SENSOR = 1 << 20

    ALL = (
        GENERAL | MOTORS | MARKER_ERASER | LED_LIGHTS | COLOR_SENSOR |
        SOUND | BUMPERS | LIGHT_SENSORS | BATTERY | TOUCH_SENSORS | CLIFF_SENSOR
    )

    @classmethod
    def from_bytes(cls, data):
        value = int.from_bytes(data, 'big')
        return cls(value)

    def to_bytes(self):
        return self.value.to_bytes(16, 'big')


class GravityState(enum.Enum):
    OFF = 0
    ON = 1
    ON_MARKER = 2


class Motor(enum.Enum):
    LEFT = 0
    RIGHT = 1
    MARKER = 2


class MotorStallCause(enum.Enum):
    NO = 0
    OVERCURRENT = 1
    UNDERCURRENT = 2
    UNDERSPEED = 3
    SATURATED_PID = 4
    TIMEOUT = 5


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


class Color(enum.Enum):
    WHITE = 0
    BLACK = 1
    RED = 2
    GREEN = 3
    BLUE = 4


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


class LightBright(enum.Enum):
    NONE = 4
    RIGHT = 5
    LEFT = 6
    BOTH = 7


class Sensor(enum.Flag):
    NONE = 0

    FRONT_LEFT = 1 << 7
    FRONT_RIGHT = 1 << 6
    REAR_RIGHT = 1 << 5
    REAR_LEFT = 1 << 4

    LEFT = FRONT_LEFT | REAR_LEFT
    RIGHT = FRONT_RIGHT | REAR_RIGHT
    FRONT = FRONT_LEFT | FRONT_RIGHT
    REAR = REAR_LEFT | REAR_RIGHT

    ALL = LEFT | RIGHT


class Cliff(enum.Enum):
    NO = 0
    CLIFF = 1
