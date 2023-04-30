from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem
from praline.common.hashing import DeltaType, delta, hash_file, progression_resolution
from typing import Any, Dict


@stage(requirements=[['clang_format_executable', 'main_sources', 'main_executable_source']],
       output=['formatted_main_sources', 'formatted_main_executable_source'],
       cacheable=True)
def format_main_sources(file_system: FileSystem, 
                        resources: StageResources, 
                        cache: Dict[str, Any], 
                        program_arguments: Dict[str, Any], 
                        configuration: Dict[str, Any], 
                        remote_proxy: RemoteProxy,
                        progressBarSupplier: ProgressBarSupplier):
    main_sources = resources['main_sources']
    clang_format = resources['clang_format_executable']
    hasher       = lambda f: hash_file(file_system, f)
    new_cache    = {}

    resolution = progression_resolution(main_sources, cache)
    with progressBarSupplier.create(resolution) as progress_bar:
        for item in delta(main_sources, hasher, cache, new_cache):
            main_source = item.key
            if item.delta_type in [DeltaType.Added, DeltaType.Modified]:
                progress_bar.update_summary(main_source)
                file_system.execute_and_fail_on_bad_return([clang_format, '-i', '-style=file', main_source])
            progress_bar.advance()

    resources['formatted_main_sources']           = main_sources
    resources['formatted_main_executable_source'] = resources['main_executable_source']
    cache.clear()
    cache.update(new_cache)
