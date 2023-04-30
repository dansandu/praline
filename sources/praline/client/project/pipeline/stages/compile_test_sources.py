from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.compiling.compiler import compile_using_cache
from praline.common.file_system import FileSystem
from typing import Any, Dict


@stage(requirements=[['project_structure', 'formatted_headers', 'formatted_test_sources', 'external_headers'],
                     ['project_structure',           'headers',           'test_sources', 'external_headers']],
       output=['test_objects'],
       cacheable=True)
def compile_test_sources(file_system: FileSystem, 
                         resources: StageResources, 
                         cache: Dict[str, Any], 
                         program_arguments: Dict[str, Any], 
                         configuration: Dict[str, Any], 
                         remote_proxy: RemoteProxy,
                         progressBarSupplier: ProgressBarSupplier):
    if resources.activation == 0:
        headers           = resources['formatted_headers']
        sources           = resources['formatted_test_sources']
    elif resources.activation == 1:
        headers           = resources['headers']
        sources           = resources['test_sources']


    project_structure = resources['project_structure']

    compiler = configuration['compiler']

    resources['test_objects'] = compile_using_cache(file_system,
                                                    project_structure,
                                                    compiler,
                                                    headers,
                                                    sources,
                                                    cache,
                                                    progressBarSupplier)
