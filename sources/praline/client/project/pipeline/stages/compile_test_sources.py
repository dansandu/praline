from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.compiling.compiler import compile_using_cache
from praline.common.file_system import FileSystem, join
from typing import Any, Dict


@stage(requirements=[['project_directory', 'compiler', 'headers_root', 'external_headers_root', 'test_sources_root', 'formatted_headers', 'formatted_test_sources'],
                     ['project_directory', 'compiler', 'headers_root', 'external_headers_root', 'test_sources_root',           'headers',           'test_sources']],
       output=['test_objects_root', 'test_objects'],
       cacheable=True)
def compile_test_sources(file_system: FileSystem, 
                         resources: StageResources, 
                         cache: Dict[str, Any], 
                         program_arguments: Dict[str, Any], 
                         configuration: Dict[str, Any], 
                         remote_proxy: RemoteProxy,
                         progressBarSupplier: ProgressBarSupplier):
    project_directory     = resources['project_directory']
    compiler              = resources['compiler']
    header_roots          = resources['headers_root']
    external_headers_root = resources['external_headers_root']
    sources_root          = resources['test_sources_root']

    if resources.activation == 0:
        headers           = resources['formatted_headers']
        sources           = resources['formatted_test_sources']
    elif resources.activation == 1:
        headers           = resources['headers']
        sources           = resources['test_sources']

    resources['test_objects_root'] = objects_root = join(project_directory, 'target', 'objects')
    resources['test_objects']      = compile_using_cache(file_system,
                                                         compiler,
                                                         header_roots,
                                                         external_headers_root,
                                                         sources_root,
                                                         objects_root,
                                                         headers,
                                                         sources,
                                                         cache,
                                                         progressBarSupplier)
