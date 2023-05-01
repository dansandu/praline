from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem
from typing import Any, Dict


@stage(requirements=[['project_structure', 'formatted_headers', 'formatted_main_sources', 
                      'formatted_main_executable_source', 'external_headers'],
                     ['project_structure', 'headers', 'main_sources', 'main_executable_source', 'external_headers']],
       output=['main_objects', 'main_executable_object'],
       cacheable=True)
def compile_main_sources(file_system: FileSystem, 
                         resources: StageResources, 
                         cache: Dict[str, Any], 
                         program_arguments: Dict[str, Any], 
                         configuration: Dict[str, Any], 
                         remote_proxy: RemoteProxy,
                         progressBarSupplier: ProgressBarSupplier):    
    if resources.activation == 0:
        headers           = resources['formatted_headers'] + resources['external_headers']
        sources           = resources['formatted_main_sources']
        executable_source = resources['formatted_main_executable_source']
    elif resources.activation == 1:
        headers           = resources['headers'] + resources['external_headers']
        sources           = resources['main_sources']
        executable_source = resources['main_executable_source']

    project_structure = resources['project_structure']
    compiler          = configuration['compiler']

    resources['main_objects'] = compiler.compile_using_cache(project_structure,
                                                             headers,
                                                             sources,
                                                             cache,
                                                             progressBarSupplier)

    if executable_source:
        yield_descriptor = compiler.get_yield_descriptor()
        resources['main_executable_object'] = yield_descriptor.get_object(project_structure.sources_root, 
                                                                          project_structure.objects_root,
                                                                          executable_source)
    else:
        resources['main_executable_object'] = None
