from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem
from praline.common.hashing import hash_file, key_delta
from typing import Any, Dict


@stage(requirements=[['clang_format_executable', 'main_sources', 'main_executable_source']],
       output=['formatted_main_sources', 'formatted_main_executable_source'],
       cacheable=True)
def format_main_sources(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    main_sources = resources['main_sources']
    hasher       = lambda f: hash_file(file_system, f)
    updated, _, new_cache = key_delta(main_sources, hasher, cache)
    if updated:
        clang_format_executable = resources['clang_format_executable']
        file_system.execute_and_fail_on_bad_return([clang_format_executable, '-i', '-style=file'] + updated)
    resources['formatted_main_sources']           = main_sources
    resources['formatted_main_executable_source'] = resources['main_executable_source']
    cache.clear()
    cache.update(new_cache)
