from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem
from praline.common.hashing import hash_file, delta, progression_resolution, DeltaType
from typing import Any, Dict


@stage(requirements=[['clang_format_executable', 'test_sources']],
       output=['formatted_test_sources'],
       cacheable=True)
def format_test_sources(file_system: FileSystem, 
                        resources: StageResources, 
                        cache: Dict[str, Any], 
                        program_arguments: Dict[str, Any], 
                        configuration: Dict[str, Any], 
                        remote_proxy: RemoteProxy,
                        progressBarSupplier: ProgressBarSupplier):
    test_sources = resources['test_sources']
    clang_format = resources['clang_format_executable']
    hasher       = lambda f: hash_file(file_system, f)
    new_cache    = {}

    resolution = progression_resolution(test_sources, cache)
    with progressBarSupplier.create(resolution) as progress_bar:
        for item in delta(test_sources, hasher, cache, new_cache):
            test_source = item.key
            if item.delta_type in [DeltaType.Added, DeltaType.Modified]:
                progress_bar.update_summary(test_source)
                file_system.execute_and_fail_on_bad_return([clang_format, '-i', '-style=file', test_source])
            progress_bar.advance()

    resources['formatted_test_sources'] = test_sources
    cache.clear()
    cache.update(new_cache)
