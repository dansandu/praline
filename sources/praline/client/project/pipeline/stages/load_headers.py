from typing import Any, Dict

from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem
from praline.common.progress_bar import ProgressBarSupplier


@stage(requirements=[['project_structure']], output=['headers'])
def load_headers(file_system: FileSystem, 
                 resources: StageResources, 
                 cache: Dict[str, Any], 
                 program_arguments: Dict[str, Any], 
                 configuration: Dict[str, Any], 
                 remote_proxy: RemoteProxy,
                 progressBarSupplier: ProgressBarSupplier):
    project_structure = resources['project_structure']
    sources_root      = project_structure.sources_root
    resources['headers'] = [f for f in file_system.files_in_directory(sources_root) if f.endswith('.hpp')]
