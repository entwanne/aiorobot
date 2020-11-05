import asyncio

from .robot import get_robot
from .robot import run_robot

def run(*args, **kwargs):
    try:
        asyncio.run(run_robot(*args, **kwargs))
    except KeyboardInterrupt:
        pass
