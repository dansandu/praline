from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common.hashing import DeltaType, delta, hash_file, progression_resolution


@stage(requirements=[['clang_format_executable', 'test_headers']], output=['formatted_test_headers'], cacheable=True)
def format_test_headers(arguments: StageArguments):
    file_system = arguments.file_system
    resources   = arguments.resources
    cache       = arguments.cache
    
    progress_bar_supplier = arguments.progress_bar_supplier

    headers      = resources['test_headers']
    clang_format = resources['clang_format_executable']
    hasher       = lambda f: hash_file(file_system, f)
    new_cache    = {}

    resolution = progression_resolution(headers, cache)
    with progress_bar_supplier.create(resolution) as progress_bar:
        for item in delta(headers, hasher, cache, new_cache):
            header = item.key
            if item.delta_type in [DeltaType.Added, DeltaType.Modified]:
                progress_bar.update_summary(header)
                file_system.execute_and_fail_on_bad_return([clang_format, '-i', '-style=file', header])
            progress_bar.advance()

    resources['formatted_test_headers'] = headers
    cache.clear()
    cache.update(new_cache)
