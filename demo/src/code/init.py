import asyncio
import cmath
import itertools
import math
import time


class Keyboard:
    def __init__(self, root, update_func=None):
        self.root = root
        self._pressed = set()
        self._last_pressed = {}
        self.update_func = update_func

    def __contains__(self, key):
        return key in self._pressed

    def __iter__(self):
        return iter(self._pressed)

    def key_pressed(self, key):
        key = key.keysym
        self._last_pressed[key] = time.time()
        if key not in self._pressed:
            self._pressed.add(key)
            if self.update_func:
                self.update_func(self)

    def key_released(self, key):
        key = key.keysym
        self.root.after(10, self._real_key_released, key, time.time())

    def _real_key_released(self, key, t):
        if t >= self._last_pressed.get(key, 0):
            self._pressed.discard(key)
            if self.update_func:
                self.update_func(self)
