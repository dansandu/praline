from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.compiling.compiler import compile_using_cache
from praline.common.file_system import FileSystem, join
from praline.common.hashing import hash_file, key_delta
from typing import Any, Dict


@stage(requirements=[['project_directory', 'compiler', 'headers_root', 'external_headers_root', 'main_sources_root', 'formatted_headers', 'formatted_main_sources', 'formatted_main_executable_source'],
                     ['project_directory', 'compiler', 'headers_root', 'external_headers_root', 'main_sources_root',           'headers',           'main_sources',           'main_executable_source']],
       output=['main_objects_root', 'main_objects', 'main_executable_object'],
       cacheable=True)
def compile_main_sources(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    project_directory     = resources['project_directory']
    compiler              = resources['compiler']
    header_roots          = resources['headers_root']
    external_headers_root = resources['external_headers_root']
    sources_root          = resources['main_sources_root']
    
    if resources.activation == 0:
        headers           = resources['formatted_headers']
        sources           = resources['formatted_main_sources']
        executable_source = resources['formatted_main_executable_source']
    elif resources.activation == 1:
        headers           = resources['headers']
        sources           = resources['main_sources']
        executable_source = resources['main_executable_source']

    resources['main_objects_root'] = objects_root = join(project_directory, 'target', 'objects')
    resources['main_objects']      = compile_using_cache(file_system,
                                                         compiler,
                                                         header_roots,
                                                         external_headers_root,
                                                         sources_root,
                                                         objects_root,
                                                         headers,
                                                         sources,
                                                         cache)

    if executable_source:
        resources['main_executable_object'] = compiler.get_yield_descriptor().get_object(sources_root, objects_root, executable_source)
    else:
        resources['main_executable_object'] = None
