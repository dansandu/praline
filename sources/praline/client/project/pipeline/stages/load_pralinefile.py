from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.compiling.compiler import get_compilers
from praline.common.file_system import FileSystem, join
from praline.common.pralinefile import pralinefile_from_path
from typing import Any, Dict


class NoMatchingCompilerFoundError(Exception):
    pass


class UnsupportedArchitectureError(Exception):
    pass


class UnsupportedPlatformError(Exception):
    pass


@stage(output=['project_directory', 'pralinefile', 'compiler'])
def load_pralinefile(file_system: FileSystem, 
                     resources: StageResources, 
                     cache: Dict[str, Any], 
                     program_arguments: Dict[str, Any], 
                     configuration: Dict[str, Any], 
                     remote_proxy: RemoteProxy,
                     progressBarSupplier: ProgressBarSupplier):
    resources['project_directory'] = project_directory = file_system.get_working_directory()
    pralinefile_path = join(project_directory, 'Pralinefile')
    try:
        resources['pralinefile'] = pralinefile = pralinefile_from_path(file_system, pralinefile_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"no Pralinefile was found in current working directory {project_directory}") from e

    architecture = file_system.get_architecture()
    if architecture not in pralinefile['architectures']:
        raise UnsupportedArchitectureError(f"system architecture '{architecture}' is not supported -- supported architectures for this project are {pralinefile['architectures']}")

    platform = file_system.get_platform()
    if platform not in pralinefile['platforms']:
        raise UnsupportedPlatformError(f"{platform} is not supported -- supported architectures are {pralinefile['platforms']}")

    mode = 'release' if program_arguments['global']['release'] else pralinefile['modes'][0]

    logging_level = program_arguments['global']['logging_level']

    exported_symbols = program_arguments['global']['exported_symbols']

    matching_compilers = [compiler for compiler in get_compilers(file_system, architecture, platform, mode, logging_level, exported_symbols) if compiler.matches()]
    compilers = [compiler for compiler in matching_compilers if compiler.get_name() in pralinefile['compilers']]
    if not compilers:
        raise NoMatchingCompilerFoundError(f"no suitable compiler was found -- matching compilers are {[c.get_name() for c in matching_compilers]} while specified compilers are {pralinefile['compilers']}")
    resources['compiler'] = compilers[0]
