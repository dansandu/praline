from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories', 'formatted_main_headers', 'formatted_test_headers', 'formatted_test_sources', 'external_headers'],
                     ['project_directories',           'main_headers',           'test_headers',           'test_sources', 'external_headers']],
       output=['test_objects'],
       cacheable=True)
def compile_test_sources(arguments: StageArguments):
    resources = arguments.resources
    compiler  = arguments.compiler
    cache     = arguments.cache
    progress_bar_supplier = arguments.progress_bar_supplier

    if resources.activation == 0:
        headers = resources['formatted_main_headers'] + resources['formatted_test_headers'] + resources['external_headers']
        sources = resources['formatted_test_sources']
    elif resources.activation == 1:
        headers = resources['main_headers'] + resources['test_headers'] + resources['external_headers']
        sources = resources['test_sources']

    resources['test_objects'] = compiler.compile_sources_using_cache(headers, sources, cache, progress_bar_supplier, main_sources=False)
