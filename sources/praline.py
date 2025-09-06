#!/usr/bin/env python3
import logging
import logging.config
import os.path
import yaml
import traceback


with open(f"{os.path.dirname(__file__)}/../resources/praline-client.config", 'r') as f:
    configuration = yaml.load(f.read(), Loader=yaml.SafeLoader)
    logging.config.dictConfig(configuration['logging'])


from praline.client.project.pipeline.orchestration import invoke_stage
from praline.client.project.pipeline.program_arguments import get_program_arguments
from praline.client.project.pipeline.stages import get_stages
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common import DirectUserMessageException
from praline.common.pralinefile import read_pralinefile
from praline.common.file_system import FileSystem, join
from praline.common.configuration import get_compiler


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    try:
        file_system       = FileSystem()
        stages            = get_stages()
        program_arguments = get_program_arguments(stages)
        remote_proxy      = RemoteProxy(file_system, configuration['remote-repository'])

        try:
            project_directory = file_system.get_working_directory()
            pralinefile_path  = join(project_directory, 'Pralinefile')
            pralinefile = read_pralinefile(file_system, pralinefile_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Pralinefile was not found in working directory {project_directory}") from e

        compiler = get_compiler(file_system, program_arguments, pralinefile)
        project_structure = compiler.project_structure
        artifact_manifest = compiler.artifact_manifest
        
        stage = program_arguments['global']['running_stage']

        invoke_stage(file_system, configuration, program_arguments, remote_proxy, project_structure, artifact_manifest, compiler, stage, stages)

        exit(0)

    except DirectUserMessageException as exception:
        logger.error(f"{type(exception).__name__} was raised with message: {exception}")
        exit(-1)
    except Exception:
        traceback.print_exc()
        exit(-1)
 