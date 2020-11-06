import asyncio

from aiorobot import driver
from aiorobot import protocol


async def main():
    devices = await driver.discover_devices()
    device = devices[0]

    async with driver.get_client(device) as client:
        rx, tx = driver.get_characteristics(client)

        payload, hdr = protocol.format_command('get_name')
        event = asyncio.Event()

        def response(sender, payload):
            _, args, hdr2 = protocol.extract_event(payload)
            if hdr2 == hdr:
                print(args)
                event.set()

        await client.start_notify(tx, response)
        await client.write_gatt_char(rx, payload)
        await event.wait()


if __name__ == '__main__':
    asyncio.run(main())
