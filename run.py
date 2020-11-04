import asyncio
from contextlib import asynccontextmanager

from bleak import discover
from bleak import BleakClient

from protocol import extract_event
from protocol import format_command


async def get_client(timeout=1):
    root_identifier_uuid = '48c5d828-ac2a-442d-97a3-0c9822b04979'
    devices = await discover(
        timeout=timeout,
        filters={'UUIDs': [root_identifier_uuid]},
    )
    device = devices[0]
    return BleakClient(device)


async def get_chars(client, uart_service_uuid, rx_char_uuid, tx_char_uuid):
    services = await client.get_services()
    uart = next(service for service in services if service.uuid == uart_service_uuid)
    rx = uart.get_characteristic(rx_char_uuid)
    assert 'write' in rx.properties
    tx = uart.get_characteristic(tx_char_uuid)
    assert 'notify' in tx.properties
    return rx, tx


def notification_handler(sender, data):
    print(sender, *extract_event(data))


@asynccontextmanager
async def notify(client, tx):
    await client.start_notify(tx, notification_handler)
    try:
        yield
    finally:
        await client.stop_notify(tx)


async def run():
    client = await get_client()
    async with client:
        print(client)
        rx, tx = await get_chars(
            client,
            uart_service_uuid='6e400001-b5a3-f393-e0a9-e50e24dcca9e',
            rx_char_uuid='6e400002-b5a3-f393-e0a9-e50e24dcca9e',
            tx_char_uuid='6e400003-b5a3-f393-e0a9-e50e24dcca9e',
        )

        async with notify(client, tx):
            #pkg = format_command('get_version', 0xA5)
            pkg = format_command('get_name')
            #pkg = format_command('get_enabled_events')
            #pkg = format_command('get_serial_number')
            #pkg = format_command('get_sku')
            #pkg = format_command('set_motor_speed', 50, 100)
            #pkg = format_command('set_left_motor_speed', 100)
            #pkg = format_command('set_right_motor_speed', 100)
            #pkg = format_command('set_gravity_compensation', 1, 3000)
            #pkg = format_command('drive_distance', 200)
            #pkg = format_command('rotate_angle', 900)
            #pkg = format_command('drive_arc', -900, -120)
            #pkg = format_command('set_marker_eraser', 1)
            #pkg = format_command('get_color_data', 0, 4, 0)
            #pkg = format_command('set_led_animation', 1, 255, 0, 255)
            #pkg = format_command('play_note', 100, 1000)
            #pkg = format_command('stop_note')
            #pkg = format_command('say_phrase', b'hello')
            #pkg = format_command('get_battery_level')
            await client.write_gatt_char(rx, pkg)
            await asyncio.sleep(10)


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
