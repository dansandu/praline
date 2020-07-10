from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem
from typing import Any, Dict


@stage(requirements=[['formatted_headers', 'formatted_main_sources', 'formatted_test_sources'],
                     ['formatted_headers', 'formatted_main_sources']], exposed=True)
def format(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    pass
