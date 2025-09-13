from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_headers',
        'main_headers', 'main_farseer_cpp_headers',
        'test_headers', 'test_farseer_cpp_headers',
        'test_sources', 'test_farseer_cpp_sources',
        'formatted_sources',
    ],
    output=['test_objects']
)
def compile_test_sources(arguments: StageArguments):
    resources = arguments.resources

    headers = []
    headers.extend(resources['external_headers'])
    headers.extend(resources['main_farseer_cpp_headers'])
    headers.extend(resources['test_farseer_cpp_headers'])
    headers.extend(resources['main_headers'])
    headers.extend(resources['test_headers'])

    sources = []
    sources.extend(resources['test_farseer_cpp_sources'])
    sources.extend(resources['test_sources'])

    if arguments.skipOrExceptionIf(len(sources) == 0, "There are no test source files the compile"):
        resources['test_objects'] = []
        return

    resources['test_objects'] = arguments.compiler.compile_sources_using_cache(
        headers, sources, arguments.cache, arguments.progress_bar_supplier, main_sources=False)
