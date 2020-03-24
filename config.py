from json import loads

# simple config loader


def get_config(filename):
    """Returns filename.json as a dict"""
    with open(filename, "r") as file:
        content = file.read()
        return dict(loads(content))
