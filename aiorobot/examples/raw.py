import asyncio

from aiorobot import driver


async def main():
    clients = await driver.Client.discover()

    async with clients[0] as client:
        payload, hdr = client.protocol.format_command('get_name')
        event = asyncio.Event()

        def response(sender, payload):
            _, args, hdr2 = client.protocol.extract_event(payload)
            if hdr2 == hdr:
                print(args)
                event.set()

        await client.start_notify(response)
        await client.send(payload)
        await event.wait()


if __name__ == '__main__':
    asyncio.run(main())
