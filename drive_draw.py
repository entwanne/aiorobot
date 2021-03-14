import cmath
import math

from aiorobot import run
#from aiorobot.fake_driver import Client
from aiorobot.driver import Client


async def _main(robot):
    await robot.marker.down()
    for i in range(4):
        await robot.led.on((0, i * 80, 100))
        await robot.motor.drive(150)
        await robot.motor.rotate(900)
    await robot.marker.up()
    await robot.disconnect()


N, F = 50, 2


def get_point(i):
    angle = (i / N) * 2 * math.pi
    x, y = 400 + 250 * math.cos(angle), 300 + 250 * math.sin(angle)
    return x + y*1j


async def main(robot):
    points = [get_point(i) for i in range(N)]
    to_draw = set(range(N))
    segments = []

    z = 100 + 500j
    angle = 0

    while to_draw:
        i = min(
            to_draw,
            key=lambda i: abs(points[i] - z),
        )
        j = (i*F) % len(points)
        to_draw.remove(i)

        z1 = points[i]
        z2 = points[j]

        if z1 != z:
            await robot.marker.up()
            dist = z1 - z
            angle1 = cmath.log(dist / abs(dist)).imag
            await robot.motor.rotate(int(math.degrees(angle - angle1) * 10))
            await robot.motor.drive(int(abs(dist)))
            z = z1
            angle = angle1

        if z2 != z:
            await robot.marker.down()
            dist = z2 - z
            angle2 = cmath.log(dist / abs(dist)).imag
            await robot.motor.rotate(int(math.degrees(angle - angle2) * 10))
            await robot.motor.drive(int(abs(dist)))
            z = z2
            angle = angle2

    await robot.disconnect()


if __name__ == '__main__':
    run(started=main, client_cls=Client)
