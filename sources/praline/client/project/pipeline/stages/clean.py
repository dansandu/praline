from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, join
from typing import Any, Dict


@stage(requirements=[['project_directory']], exposed=True)
def clean(file_system: FileSystem, 
          resources: StageResources, 
          cache: Dict[str, Any], 
          program_arguments: Dict[str, Any], 
          configuration: Dict[str, Any], 
          remote_proxy: RemoteProxy,
          progressBarSupplier: ProgressBarSupplier):
    target = join(resources['project_directory'], 'target')
    if file_system.exists(target):
        file_system.remove_directory_recursively(target)
