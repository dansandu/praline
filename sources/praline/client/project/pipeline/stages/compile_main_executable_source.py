from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_structure', 'formatted_headers', 'formatted_main_executable_source', 'external_headers'],
                     ['project_structure', 'headers', 'main_executable_source', 'external_headers']],
       output=['main_executable_object'],
       cacheable=True)
def compile_main_executable_source(arguments: StageArguments):
    resources = arguments.resources
    compiler  = arguments.compiler
    cache     = arguments.cache
    progress_bar_supplier = arguments.progress_bar_supplier
    
    if resources.activation == 0:
        headers           = resources['formatted_headers'] + resources['external_headers']
        executable_source = resources['formatted_main_executable_source']
    elif resources.activation == 1:
        headers           = resources['headers'] + resources['external_headers']
        executable_source = resources['main_executable_source']

    project_structure = resources['project_structure']
    
    resources['main_executable_object'] = compiler.compile_using_cache(project_structure,
                                                                       headers,
                                                                       [executable_source],
                                                                       cache,
                                                                       progress_bar_supplier)[0]
