import pyglet


window = pyglet.window.Window(800, 600)
bg = pyglet.shapes.Rectangle(0, 0, 800, 600, color=(255, 255, 255))
robot = pyglet.shapes.Rectangle(100, 100, 50, 50, color=(55, 55, 255))
robot.anchor_position = (25, 25)
lvector = pyglet.shapes.Rectangle(100, 100, 25, 4, color=(255, 55, 55))
lvector.anchor_position = (25, 2)
rvector = pyglet.shapes.Rectangle(100, 100, 25, 4, color=(55, 255, 55))
rvector.anchor_position = (0, 2)


@window.event
def on_draw():
    window.clear()
    bg.draw()
    robot.draw()
    lvector.draw()
    rvector.draw()


@window.event
def on_expose():
    pass


@window.event
def on_key_press(symbol, modifiers):
    import math, cmath
    # Right motor - rotate around left motor
    if symbol in (pyglet.window.key.LEFT, pyglet.window.key.RIGHT):
        d = -1 if symbol == pyglet.window.key.LEFT else 1
        angle = d * 10

        rotation1 = robot.rotation
        robot.rotation += angle
        rotation2 = robot.rotation
        dz = 25 * (cmath.exp(math.radians(180 - rotation2) * 1j) - cmath.exp(math.radians(180 - rotation1) * 1j))
        robot.position = (robot.position[0] - dz.real, robot.position[1] - dz.imag)

        lvector.rotation = rvector.rotation = robot.rotation
        lvector.position = rvector.position = robot.position
    # Left motor - rotate around right motor
    elif symbol in (pyglet.window.key.UP, pyglet.window.key.DOWN):
        d = -1 if symbol == pyglet.window.key.DOWN else 1
        angle = d * 10

        rotation1 = robot.rotation
        robot.rotation += angle
        rotation2 = robot.rotation
        dz = 25 * (cmath.exp(math.radians(-rotation2) * 1j) - cmath.exp(math.radians(-rotation1) * 1j))
        robot.position = (robot.position[0] - dz.real, robot.position[1] - dz.imag)

        lvector.rotation = rvector.rotation = robot.rotation
        lvector.position = rvector.position = robot.position


on_draw()
pyglet.app.run()
