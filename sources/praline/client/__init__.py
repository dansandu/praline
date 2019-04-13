import logging.config
from praline.client.configuration import configuration

logging.config.dictConfig(configuration['logging'])
