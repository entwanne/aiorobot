import time
from tkinter import Tk

from aiorobot.examples.thread import run_thread, queue as q
from aiorobot.fake_driver import Client


class Keyboard:
    def __init__(self, root, update_func=None):
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
                self.update_func(keyboard)

    def key_released(self, key):
        key = key.keysym
        root.after(10, self._real_key_released, key, time.time())

    def _real_key_released(self, key, t):
        if t >= self._last_pressed.get(key, 0):
            self._pressed.discard(key)
            if self.update_func:
                self.update_func(keyboard)


async def start(robot):
    while True:
        event = await q.get()
        if event is None:
            break
        left, right = event
        await robot.motor.set_speed(left, right)
    await robot.motor.set_speed(0, 0)
    await robot.disconnect()


def handle_keys(keyboard):
    left, right = 0, 0
    if 'Up' in keyboard:
        left += 100
        right += 100
    if 'Down' in keyboard:
        left -= 100
        right -= 100
    if 'Left' in keyboard:
        left -= 50
        right += 50
    if 'Right' in keyboard:
        left += 50
        right -= 50
    q.put_nowait((left, right))


run_thread(started=start, client_cls=Client)

root = Tk()
keyboard = Keyboard(root, update_func=handle_keys)
root.bind('<KeyPress>', keyboard.key_pressed)
root.bind('<KeyRelease>', keyboard.key_released)

try:
    root.mainloop()
finally:
    q.put_nowait(None)
