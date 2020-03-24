import asyncio
from config import get_config
from json import loads
from json import dumps
from aiofile import AIOFile

config = get_config("config.json")

# def set_scores(d):
#    with open(config["scores"], "w") as scores:
#        scores.write(dumps(d))


async def set_scores(d):
    """Writes a dict to the scores json file"""
    async with AIOFile(config["scores"], "w") as afp:
        await afp.write(dumps(d))


def get_scores():
    """Returns scores as a dict"""
    with open(config["scores"], "r") as scores:
        return loads(scores.read())
