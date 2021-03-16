from tkinter import Tk

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

def tk_thread():
    root = Tk()
    keyboard = Keyboard(root, update_func=handle_keys)
    root.bind('<KeyPress>', keyboard.key_pressed)
    root.bind('<KeyRelease>', keyboard.key_released)
    try:
        root.mainloop()
    finally:
        q.put_nowait(None)
