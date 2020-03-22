from config import getConfig
from json import loads
from json import dumps

config = getConfig("config.json")

def setScores(d):
    """Writes a dict to the scores json file"""
    with open(config["scores"], 'w') as scores:
        scores.write(dumps(d))

def getScores():
    """Returns scores as a dict"""
    with open(config["scores"], 'r') as scores:
        return loads(scores.read())
