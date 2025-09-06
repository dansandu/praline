from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[
            ['project_directories', 'external_headers', 'formatted_main_headers', 'formatted_main_executable_source', 'generated_main_farseer_cpp_headers'],
            ['project_directories', 'external_headers', 'formatted_main_headers', 'formatted_main_executable_source'],
            ['project_directories', 'external_headers',           'main_headers',           'main_executable_source', 'generated_main_farseer_cpp_headers'],
            ['project_directories', 'external_headers',           'main_headers',           'main_executable_source'],
        ],
        output=['main_executable_object'],
        has_progress_bar=True)
def compile_main_executable(arguments: StageArguments):
    resources = arguments.resources
    compiler  = arguments.compiler
    cache     = arguments.cache
    
    progress_bar_supplier = arguments.progress_bar_supplier

    headers = []
    headers.extend(resources['external_headers'])
    
    if 'formatted_main_headers' in resources:
        headers.extend(resources['formatted_main_headers'])

        executable_source = resources['formatted_main_executable_source']
    else:
        headers.extend(resources['main_headers'])
        
        executable_source = resources['main_executable_source']
    
    if 'generated_main_farseer_cpp_headers' in resources:
        headers.extend(resources['generated_main_farseer_cpp_headers'])
    
    objects = compiler.compile_sources_using_cache(headers, [executable_source], cache, progress_bar_supplier, main_sources=True)
    
    resources['main_executable_object'] = objects[0]
