import yaml
from os.path import dirname

def get_configuration():
    with open(f"{dirname(__file__)}/../../../resources/praline-server.config", 'r') as f:
        return yaml.load(f.read(), Loader=yaml.SafeLoader)


configuration = get_configuration()
