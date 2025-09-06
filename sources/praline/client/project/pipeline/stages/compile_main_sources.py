from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[
            ['project_directories', 'external_headers', 'formatted_main_headers', 'formatted_main_sources', 'generated_main_farseer_cpp_headers', 'generated_main_farseer_cpp_sources'],
            ['project_directories', 'external_headers', 'formatted_main_headers', 'formatted_main_sources'],
            ['project_directories', 'external_headers',           'main_headers',           'main_sources', 'generated_main_farseer_cpp_headers', 'generated_main_farseer_cpp_sources'],
            ['project_directories', 'external_headers',           'main_headers',           'main_sources'],
       ],
       output=['main_objects'],
       has_progress_bar=True)
def compile_main_sources(arguments: StageArguments):
    resources = arguments.resources
    compiler  = arguments.compiler
    cache     = arguments.cache

    progress_bar_supplier = arguments.progress_bar_supplier

    headers = []
    headers.extend(resources['external_headers'])

    sources = []

    if 'formatted_main_headers' in resources:
        headers.extend(resources['formatted_main_headers'])

        sources.extend(resources['formatted_main_sources'])
    else:
        headers.extend(resources['main_headers'])

        sources.extend(resources['main_sources'])

    if 'generated_main_farseer_cpp_headers' in resources:
        headers.extend(resources['generated_main_farseer_cpp_headers'])
        
        sources.extend(resources['generated_main_farseer_cpp_sources'])

    resources['main_objects'] = compiler.compile_sources_using_cache(headers, sources, cache, progress_bar_supplier, main_sources=True)
