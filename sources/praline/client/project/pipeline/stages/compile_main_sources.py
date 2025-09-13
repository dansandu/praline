from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_headers',
        'main_farseer_cpp_headers', 'main_headers',
        'main_farseer_cpp_sources', 'main_sources',
        'formatted_sources',
    ],
    output=['main_objects']
)
def compile_main_sources(arguments: StageArguments):
    resources = arguments.resources

    headers = []
    headers.extend(resources['external_headers'])
    headers.extend(resources['main_farseer_cpp_headers'])
    headers.extend(resources['main_headers'])

    sources = []
    sources.extend(resources['main_farseer_cpp_sources'])
    sources.extend(resources['main_sources'])

    if arguments.skipOrExceptionIf(len(sources) == 0, "There are no main source files the compile"):
        resources['main_objects'] = []
        return

    resources['main_objects'] = arguments.compiler.compile_sources_using_cache(
        headers, sources, arguments.cache, arguments.progress_bar_supplier, main_sources=True)
