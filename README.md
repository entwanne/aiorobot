# Root robot

Python async API for iRobot Root (coding robot) over bluetooth-low-energy protocol.

Protocol specifications from <https://github.com/RootRobotics/root-robot-ble-protocol>.

## Installation

Install the `aiorobot` package from PyPI with `pip`.

```sh
pip install aiorobot
```

## Quickstart

To simply run the robot, use the `run` function of `aiorobot` module.
It takes coroutine callbacks for different root robot events.

```python
from aiorobot import run

async def main(robot):
    for i in range(4):
        await robot.led.on((0, i * 80, 100))
        await robot.motor.drive(150)
        await robot.motor.rotate(900)
    await robot.disconnect()

run(started=main)
```

This will search for a root robot in bluetooth devices, connect to it and call the `main` coroutine when the root is ready.
So make sure you have bluetooth enabled and working on your computer.

Accepted keyword-arguments of `run` function are event names listed in [aiorobot/events.py](https://github.com/entwanne/aiorobot/blob/master/aiorobot/events.py).

You can also directly get a robot and interact with it with `get_robot` function that you can use as an async context-manager to start the connection.

```python
import asyncio
from aiorobot import get_robot

async def main():
    async with get_robot() as robot:
        await robot.motor.drive(150)

asyncio.run(main())
```

Then you will need to handle events yourself (iterate over `robot.events` or call `robots.events.process()`) to get updates from the robot.

See more code examples in [aiorobot/examples](https://github.com/entwanne/aiorobot/tree/master/aiorobot/examples) directory.
