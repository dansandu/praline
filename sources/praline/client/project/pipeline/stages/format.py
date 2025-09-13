from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common.exception import ClangFormatConfigurationException
from praline.common.hashing import DeltaItem, DeltaType, delta, hash_file, progression_resolution


@stage(
    requirements=[
        'clang_format_executable',
        'main_headers', 'main_sources', 'main_executable_source',
        'test_headers', 'test_sources', 'test_executable_source',
    ],
    output=['formatted_sources'],
    exposed=True
)
def format(arguments: StageArguments):
    file_system = arguments.file_system
    resources   = arguments.resources
    cache       = arguments.cache

    clang_format_executable = resources['clang_format_executable']
    main_executable_source  = resources['main_executable_source']
    test_executable_source  = resources['test_executable_source']

    files = []
    files.extend(resources['main_headers'])
    files.extend(resources['main_sources'])
    files.extend(resources['test_headers'])
    files.extend(resources['test_sources'])

    if main_executable_source != None:
        files.append(main_executable_source)

    if test_executable_source != None:
        files.append(test_executable_source)

    if arguments.skipOrExceptionIf(
        clang_format_executable == None, 
        "Coudn't find clang-format in path -- either supply it in the praline-client.config file or add it "
        "to the path environment variable",
        exception=ClangFormatConfigurationException
    ):
        resources['formatted_sources'] = False
        return

    hasher    = lambda f: hash_file(file_system, f)
    new_cache = {}

    resolution = progression_resolution(files, cache)
    with arguments.progress_bar_supplier.create(resolution) as progress_bar:
        def consumer(item: DeltaItem):
            header = item.key
            if item.delta_type in [DeltaType.Added, DeltaType.Modified]:
                progress_bar.update_description(header)
                file_system.execute_and_fail_on_bad_return([clang_format_executable, '-i', '-style=file', header])
            progress_bar.advance()

        delta(files, hasher, cache, new_cache, consumer)

    cache.clear()
    cache.update(new_cache)

    resources['formatted_sources'] = True
