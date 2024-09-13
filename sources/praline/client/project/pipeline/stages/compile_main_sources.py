from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories', 'formatted_main_headers', 'formatted_main_sources', 'external_headers'],
                     ['project_directories',           'main_headers',           'main_sources', 'external_headers']],
       output=['main_objects'],
       cacheable=True)
def compile_main_sources(arguments: StageArguments):
    resources = arguments.resources
    compiler  = arguments.compiler
    cache     = arguments.cache

    progress_bar_supplier = arguments.progress_bar_supplier
    
    if resources.activation == 0:
        headers = resources['formatted_main_headers'] + resources['external_headers']
        sources = resources['formatted_main_sources']
    elif resources.activation == 1:
        headers = resources['main_headers'] + resources['external_headers']
        sources = resources['main_sources']

    resources['main_objects'] = compiler.compile_sources_using_cache(headers, sources, cache, progress_bar_supplier, main_sources=True)
