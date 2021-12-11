#!/usr/bin/env python3.9
from praline.client.configuration import configuration
import logging.config
import logging


logging.config.dictConfig(configuration['logging'])


from praline.client.project.pipeline.orchestration import invoke_stage
from praline.client.project.pipeline.program_arguments import get_program_arguments
from praline.client.repository.remote_proxy import RemoteProxy
from praline.client.project.pipeline.stages.stage import registered_stages
from praline.common.file_system import FileSystem


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    try:
        file_system = FileSystem()
        remote_proxy = RemoteProxy(file_system, configuration['remote-repository'])
        program_arguments = get_program_arguments(registered_stages)
        stage = program_arguments['global']['running_stage']
        invoke_stage(stage, registered_stages, file_system, program_arguments, configuration, remote_proxy)
        exit(0)
    except RuntimeError as exception:
        logger.fatal(exception)
        exit(-1)
