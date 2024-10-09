from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories', 'formatted_main_headers', 'formatted_main_executable_source', 'external_headers'],
                     ['project_directories',           'main_headers',           'main_executable_source', 'external_headers']],
       output=['main_executable_object'],
       has_progress_bar=True)
def compile_main_executable(arguments: StageArguments):
    resources = arguments.resources
    compiler  = arguments.compiler
    cache     = arguments.cache
    
    progress_bar_supplier = arguments.progress_bar_supplier
    
    if resources.activation == 0:
        headers           = resources['formatted_main_headers'] + resources['external_headers']
        executable_source = resources['formatted_main_executable_source']
    elif resources.activation == 1:
        headers           = resources['main_headers'] + resources['external_headers']
        executable_source = resources['main_executable_source']

    objects = compiler.compile_sources_using_cache(headers, [executable_source], cache, progress_bar_supplier, main_sources=True)
    
    resources['main_executable_object'] = objects[0]
