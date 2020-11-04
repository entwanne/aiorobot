import asyncio
from contextlib import asynccontextmanager

from bleak import discover
from bleak import BleakClient

from driver import Driver
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
    print(*extract_event(data))


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

        async with Driver(client, rx, tx) as driver:
            #await driver.drive_distance(200, wait=False)
            #await driver.drive_distance(200)
            #from driver import Board
            #print(await driver.get_version(Board.MAIN))
            print(await driver.get_name())
            #print(await driver.get_serial_number())
            #print(await driver.get_sku())
            #from driver import LEDAnimation
            #await driver.set_led_animation(LEDAnimation.SPIN, 100, 0, 255)
            #from driver import MarkerEraserPosition
            #print(await driver.set_marker_eraser(MarkerEraserPosition.MARKER_DOWN))
            await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
