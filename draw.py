import math

import pyglet


N, F = 50, 2

window = pyglet.window.Window(800, 600)
batch = pyglet.graphics.Batch()
#bg = pyglet.shapes.Circle(400, 300, 250, color=(255, 255, 255), batch=batch)
bg = pyglet.shapes.Rectangle(0, 0, 800, 600, color=(255, 255, 255), batch=batch)

def get_point(i):
    angle = (i / N) * 2 * math.pi
    return 400 + 250 * math.cos(angle), 300 + 250 * math.sin(angle)


points = [get_point(i) for i in range(N)]
to_draw = set(range(N))
segments = []


@window.event
def on_draw():
    window.clear()
    batch.draw()


@window.event
def on_expose():
    pass


lastj = 0
def update(dt):
    global lastj
    if not to_draw:
        pyglet.clock.unschedule(update)
        return

    #i = min(to_draw)
    i = min(to_draw, key=lambda i: abs(i - lastj))
    j = (i*F) % len(points)
    to_draw.remove(i)

    if i == j:
        return update(dt)

    # optimization
    #if abs(i - j) < N / 12:
    #    return update(dt)

    lastj = j
    x1, y1 = points[i]
    x2, y2 = points[j]
    segments.append(pyglet.shapes.Line(x1, y1, x2, y2, color=(0, 0, 0), batch=batch))


pyglet.clock.schedule_interval(update, 0.2)

pyglet.app.run()
