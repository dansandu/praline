import os.path
import yaml


def get_configuration():
    with open(f"{os.path.dirname(__file__)}/../../../resources/praline-server.config", 'r') as f:
        return yaml.load(f.read(), Loader=yaml.SafeLoader)


configuration = get_configuration()
