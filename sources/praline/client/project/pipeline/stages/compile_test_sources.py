from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[
           ['project_directories', 'external_headers', 'formatted_main_headers', 'formatted_test_headers', 'formatted_test_sources', 'generated_main_farseer_cpp_headers', 'generated_test_farseer_cpp_headers', 'generated_test_farseer_cpp_sources'],
           ['project_directories', 'external_headers', 'formatted_main_headers', 'formatted_test_headers', 'formatted_test_sources', 'generated_main_farseer_cpp_headers'],
           ['project_directories', 'external_headers', 'formatted_main_headers', 'formatted_test_headers', 'formatted_test_sources', 'generated_test_farseer_cpp_headers', 'generated_test_farseer_cpp_sources'],
           ['project_directories', 'external_headers', 'formatted_main_headers', 'formatted_test_headers', 'formatted_test_sources'],
           ['project_directories', 'external_headers',           'main_headers',           'test_headers',           'test_sources', 'generated_main_farseer_cpp_headers', 'generated_test_farseer_cpp_headers', 'generated_test_farseer_cpp_sources'],
           ['project_directories', 'external_headers',           'main_headers',           'test_headers',           'test_sources', 'generated_main_farseer_cpp_headers'],
           ['project_directories', 'external_headers',           'main_headers',           'test_headers',           'test_sources', 'generated_test_farseer_cpp_headers', 'generated_test_farseer_cpp_sources'],
           ['project_directories', 'external_headers',           'main_headers',           'test_headers',           'test_sources'],
       ],
       output=['test_objects'],
       has_progress_bar=True)
def compile_test_sources(arguments: StageArguments):
    resources = arguments.resources
    compiler  = arguments.compiler
    cache     = arguments.cache

    progress_bar_supplier = arguments.progress_bar_supplier

    headers = []
    headers.extend(resources['external_headers'])

    sources = []

    if 'formatted_main_headers' in resources:
        headers.extend(resources['formatted_main_headers'])
        headers.extend(resources['formatted_test_headers'])

        sources.extend(resources['formatted_test_sources'])
    else:
        headers.extend(resources['main_headers'])
        headers.extend(resources['test_headers'])

        sources.extend(resources['test_sources'])

    if 'generated_main_farseer_cpp_headers' in resources:
        headers.extend(resources['generated_main_farseer_cpp_headers'])

    if 'generated_test_farseer_cpp_headers' in resources:
        headers.extend(resources['generated_test_farseer_cpp_headers'])

        sources.extend(resources['generated_test_farseer_cpp_sources'])

    resources['test_objects'] = compiler.compile_sources_using_cache(headers, sources, cache, progress_bar_supplier, main_sources=False)
