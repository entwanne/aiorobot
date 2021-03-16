from aiorobot import run_robot
from aiorobot.fake_driver import Client, FakeRobot

FakeRobot.speed = 500
N, F = 50, 2

def get_point(i):
    angle = (i / N) * 2 * math.pi
    x, y = 400 + 250 * math.cos(angle), 300 + 250 * math.sin(angle)
    return x + y*1j

async def goto(robot, src, dst, angle_src):
    vec = dst - src
    angle_dst = cmath.log(vec / abs(vec)).imag
    await robot.motor.rotate(int(math.degrees(angle_src - angle_dst) * 10))
    await robot.motor.drive(int(abs(vec)))
    return dst, angle_dst

points = [get_point(i) for i in range(N)]
to_draw = set(range(N))
segments = []
