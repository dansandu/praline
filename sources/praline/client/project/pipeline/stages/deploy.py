from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem
from typing import Any, Dict


@stage(requirements=[['headers_only_package'], ['main_library_package'], ['main_executable_package']], exposed=True)
def deploy(file_system: FileSystem, 
           resources: StageResources, 
           cache: Dict[str, Any], 
           program_arguments: Dict[str, Any], 
           configuration: Dict[str, Any], 
           remote_proxy: RemoteProxy,
           progressBarSupplier: ProgressBarSupplier):
    if resources.activation == 0:
        remote_proxy.push_package(resources['headers_only_package'])
    elif resources.activation == 1:
        remote_proxy.push_package(resources['main_library_package'])
    elif resources.activation == 2:
        remote_proxy.push_package(resources['main_executable_package'])
