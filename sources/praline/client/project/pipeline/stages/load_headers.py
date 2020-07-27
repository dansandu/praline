from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem
from typing import Any, Dict


@stage(requirements=[['headers_root']], output=['headers'])
def load_headers(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    resources['headers'] = [f for f in file_system.files_in_directory(resources['headers_root']) if f.endswith('.hpp')]
