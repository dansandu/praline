from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common.hashing import DeltaType, delta, hash_file, progression_resolution


@stage(requirements=[['clang_format_executable', 'main_sources', 'main_executable_source']],
       output=['formatted_main_sources', 'formatted_main_executable_source'],
       cacheable=True)
def format_main_sources(arguments: StageArguments):
    resources    = arguments.resources
    file_system  = arguments.file_system
    cache        = arguments.cache
    progress_bar_supplier = arguments.progress_bar_supplier

    main_sources = resources['main_sources']
    clang_format = resources['clang_format_executable']
    hasher       = lambda f: hash_file(file_system, f)
    new_cache    = {}

    resolution = progression_resolution(main_sources, cache)
    with progress_bar_supplier.create(resolution) as progress_bar:
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
