import threading

import pyglet

from .driver import Driver as BaseDriver
from .types import *


async def discover_devices(timeout=0):
    return [None]


def get_driver(device):
    return Driver()


def pyglet_thread():
    window = pyglet.window.Window(width=800, height=600)
    pyglet.app.run()


def run_thread():
    thread = threading.Thread(
        target=pyglet_thread,
    )
    thread.start()
    return thread


class Driver(BaseDriver):
    def __init__(self):
        super().__init__(None, None, None)

    async def __aenter__(self):
        run_thread()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def _send(self, cmd, *args, wait_response=True):
        print(cmd)
