from config import getConfig
from json import loads

config = getConfig("config.json")

def setScores(d):
    """Writes a dict to the scores json file"""
    with open(config["scores"], 'w') as scores:
        scores.write(str(d))

def getScores():
    """Returns scores as a dict"""
    with open(config["scores"], 'r') as scores:
        return loads(scores.read())
