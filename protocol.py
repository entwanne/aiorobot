import itertools
import struct

from crc8 import crc8


FULL_PACKET_LEN = 20
SIMPLE_PACKET_LEN = FULL_PACKET_LEN - 1

_msg_prefix = '>3B'
_msg_prefix_len = struct.calcsize(_msg_prefix)

_commands = {
    # name: (dev, cmd, fmt)

    'get_version': (0, 0, 'B'),  # board (A5=main|C6=color)
    'set_name': (0, 1, '16s'),  # name
    'get_name': (0, 2, ''),
    'cancel': (0, 3, ''),
    'disconnect': (0, 6, ''),
    'enable_events': (0, 7, '16s'),  # devices bitfield (1=enable|0=unchange)
    'disable_events': (0, 9, '16s'),  # devices bitfield (1=disable|0=unchange)
    'get_enabled_events': (0, 11, ''),
    'get_serial_number': (0, 14, ''),
    'get_sku': (0, 15, ''),

    'set_motor_speed': (1, 4, 'ii'),  # left in mm/s, right in mm/s
    'set_left_motor_speed': (1, 6, 'i'),  # left in mm/s, right in mm/s
    'set_right_motor_speed': (1, 7, 'i'),  # left in mm/s, right in mm/s
    'set_gravity_compensation': (1, 14, 'BH'),  # state (0=off|1=on|2=marker), amount in ‰

    'drive_distance': (1, 8, 'i'),  # distance in mm
    'rotate_angle': (1, 12, 'i'),  # angle in decidegrees
    'drive_arc': (1, 27, 'ii'),  # angle in decidegrees, radius in mm

    'reset_position': (1, 15, ''),
    'get_position': (1, 16, ''),
    'nav_to_position': (1, 17, '3h'),  # X in mm, Y in mm, orientation in decidegrees (-1 to let it choice)

    'set_marker_eraser': (2, 0, 'B'),  # position (0=up|1=marker down|2=eraser down)
    'get_color_data': (4, 1, '3B'),  # sensor (0 to 3, from left to right), lightning (0=off|1=red|2=green|3=blue|4=all), format (0=12bit|1=mv)

    'set_led_animation': (3, 2, '4B'),  # anim (0=off|1=on|2=blink|3=spin), red, green, blue

    'play_note': (5, 0, 'IH'),  # freq in Hz, duration in ms
    'stop_note': (5, 1, ''),
    'say_phrase': (5, 4, '16s'),  # phrase (bytes, utf8 encoded)
    'play_sweep': (5, 5, '2IH6B'),  # start freq in mHz, end freq in mHz, duration in ms, attack in ms, release in ms, volume, modulation type, modulation rate, append

    'get_light_values': (13, 1, ''),

    'get_battery_level': (14, 1, ''),

    'get_accelerometer': (16, 1, ''),
}

_events = {
    # (dev, cmd): (name, fmt)

    (0, 0): ('version', '9B'),  # board, FWmaj, FWmin, HWmaj, HWmin, Bootmaj, Bootmin, Protomaj, Protomin
    (0, 2): ('name', '16s'),  # name
    (0, 4): ('stopped', ''),
    (0, 11): ('enabled_events', '16s'),  # devices bitfield
    (0, 14): ('serial_number', '12s'),  # serial number
    (0, 15): ('sku', '16s'),  # SKU
    (1, 8): ('drive_distance_finished', ''),
    (1, 12): ('rotate_angle_finished', ''),
    (1, 27): ('drive_arc_finished', ''),
    (1, 16): ('get_position', 'I3h'),  # X in mm, Y in mm, orientation in decidegrees
    (1, 17): ('nav_to_position_finished', '3h'),  # X in mm, Y in mm, orientation in decidegrees
    (1, 29): ('motor_stall', 'I2B'),  # timestamp, motor (0=left|1=right|2=marker), cause
    (2, 0): ('marker_eraser_finished', 'B'),  # position
    (4, 1): ('color_response', '8H'),  # 8 16bit colors
    (4, 2): ('color_event', '16s'),  #
    (5, 0): ('play_note_finished', ''),
    (5, 4): ('say_phrase_finished', ''),
    (5, 5): ('play_sweep_finished', ''),
    (12, 0): ('bumper_event', 'IB'),  # timestamp, state(00=no|40=right|80=left|C0=both)
    (13, 0): ('light_event', 'IB2H'),  # timestamp, state, left, right
    (13, 1): ('light_values', 'I2H'),  # timestamp, left, right
    (14, 0): ('battery_event', 'IHB'),  # timestamp, voltage, percent
    (14, 1): ('battery_response', 'IHB'),  # timestamp, voltage, percent
    (16, 1): ('accelerometer', 'I3h'),  # timestamp, X, Y, Z
    (17, 0): ('touch_event', 'IB'),  # timestamp, state
    (20, 0): ('cliff_event', 'IB2H'),  # timestamp, cliff, sensor, threshold
}


_packet_ids = itertools.count(1)

def format_command(command, *args):
    dev, cmd, fmt = _commands[command]
    inc = next(_packet_ids)
    packet = struct.pack(_msg_prefix + fmt, dev, cmd, inc, *args)

    if len(packet) < SIMPLE_PACKET_LEN:
        packet += bytes(SIMPLE_PACKET_LEN - len(packet))

    packet += crc8(packet).digest()

    assert len(packet) == FULL_PACKET_LEN

    return bytearray(packet)


def extract_event(payload):
    dev, cmd, eid = struct.unpack_from(_msg_prefix, payload)
    name, fmt = _events.get((dev, cmd), (f'unknown-{dev}-{cmd}', '16s'))

    if fmt:
        payload = payload[_msg_prefix_len:]
        args = struct.unpack_from(fmt, payload)
    else:
        args = ()

    return (name, eid) + args
