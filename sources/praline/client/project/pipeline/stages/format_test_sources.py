from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem
from praline.common.hashing import hash_file, key_delta
from typing import Any, Dict


@stage(requirements=[['clang_format_executable', 'test_sources']],
       output=['formatted_test_sources'],
       cacheable=True)
def format_test_sources(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    test_sources = resources['test_sources']
    hasher       = lambda f: hash_file(file_system, f)
    updated, _, new_cache = key_delta(test_sources, hasher, cache)
    if updated:
        clang_format_executable = resources['clang_format_executable']
        file_system.execute_and_fail_on_bad_return([clang_format_executable, '-i', '-style=file'] + updated)
    resources['formatted_test_sources'] = test_sources
    cache.clear()
    cache.update(new_cache)
