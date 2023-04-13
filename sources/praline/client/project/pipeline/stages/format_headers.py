from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem
from praline.common.hashing import hash_file, delta, DeltaType, progression_resolution
from typing import Any, Dict


@stage(requirements=[['clang_format_executable', 'headers']],
       output=['formatted_headers'],
       cacheable=True)
def format_headers(file_system: FileSystem, 
                   resources: StageResources, 
                   cache: Dict[str, Any], 
                   program_arguments: Dict[str, Any], 
                   configuration: Dict[str, Any], 
                   remote_proxy: RemoteProxy,
                   progressBarSupplier: ProgressBarSupplier):
    headers   = resources['headers']
    hasher    = lambda f: hash_file(file_system, f)
    new_cache = {}

    resolution = progression_resolution(headers, cache)
    with progressBarSupplier.create(resolution) as progress_bar:
        for item in delta(headers, hasher, cache, new_cache):
            header = item.key
            if item.delta_type == DeltaType.Modified:
                progress_bar.update_summary(header)
                clang_format_executable = resources['clang_format_executable']
                file_system.execute_and_fail_on_bad_return([clang_format_executable, '-i', '-style=file', header])
            progress_bar.advance()

    resources['formatted_headers'] = headers
    cache.clear()
    cache.update(new_cache)
