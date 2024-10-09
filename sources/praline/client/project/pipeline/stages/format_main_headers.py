from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common.hashing import DeltaItem, DeltaType, delta, hash_file, progression_resolution


@stage(requirements=[['clang_format_executable', 'main_headers']], 
       output=['formatted_main_headers'],
       has_progress_bar=True)
def format_main_headers(arguments: StageArguments):
    file_system = arguments.file_system
    resources   = arguments.resources
    cache       = arguments.cache
    
    progress_bar_supplier = arguments.progress_bar_supplier

    headers      = resources['main_headers']
    clang_format = resources['clang_format_executable']
    hasher       = lambda f: hash_file(file_system, f)
    new_cache    = {}

    resolution = progression_resolution(headers, cache)
    with progress_bar_supplier.create(resolution) as progress_bar:
        def consumer(item: DeltaItem):
            header = item.key
            if item.delta_type in [DeltaType.Added, DeltaType.Modified]:
                progress_bar.update_description(header)
                file_system.execute_and_fail_on_bad_return([clang_format, '-i', '-style=file', header])
            progress_bar.advance()

        delta(headers, hasher, cache, new_cache, consumer)

    resources['formatted_main_headers'] = headers
    cache.clear()
    cache.update(new_cache)
