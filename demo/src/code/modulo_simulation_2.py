async def main(robot):
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
            z, angle = await goto(robot, z, z1, angle)

        if z2 != z:
            await robot.marker.down()
            z, angle = await goto(robot, z, z2, angle)

    await robot.disconnect()

await run_robot(started=main, client_cls=Client)
