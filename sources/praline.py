#!/usr/bin/env python3
import logging
import logging.config
import os.path
import yaml


with open(f"{os.path.dirname(__file__)}/../resources/praline-client.config", 'r') as f:
    configuration = yaml.load(f.read(), Loader=yaml.SafeLoader)
    logging.config.dictConfig(configuration['logging'])


from praline.client.project.pipeline.orchestration import invoke_stage
from praline.client.project.pipeline.configuration import get_artifact_manifest_and_compiler
from praline.client.project.pipeline.program_arguments import get_program_arguments
from praline.client.project.pipeline.stages.stage import registered_stages
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.pralinefile import read_pralinefile
from praline.common.file_system import FileSystem, join


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    try:
        file_system       = FileSystem()
        program_arguments = get_program_arguments(registered_stages)
        remote_proxy      = RemoteProxy(file_system, configuration['remote-repository'])

        try:
            project_directory = file_system.get_working_directory()
            pralinefile_path  = join(project_directory, 'Pralinefile')
            pralinefile = read_pralinefile(file_system, pralinefile_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Pralinefile was not found in working directory {project_directory}") from e

        (artifact_manifest, compiler) = get_artifact_manifest_and_compiler(file_system, program_arguments, pralinefile)
        
        configuration['artifact_manifest'] = artifact_manifest
        configuration['compiler']          = compiler

        stage = program_arguments['global']['running_stage']

        invoke_stage(file_system, 
                     configuration, 
                     program_arguments, 
                     remote_proxy, 
                     stage, 
                     registered_stages)

        exit(0)
    except RuntimeError as exception:
        logger.fatal(exception)
        exit(-1)
 