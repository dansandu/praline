#!/usr/bin/env python3
from logging import getLogger
from praline.client.project.pipeline.conducting import conduct


if __name__ == '__main__':
    logger = getLogger(__name__)
    try:
        conduct()
        exit(0)
    except RuntimeError as exception:
        logger.fatal(exception)
        exit(-1)
