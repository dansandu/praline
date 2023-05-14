from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_structure', 'formatted_headers', 'formatted_main_sources', 
                      'formatted_main_executable_source', 'external_headers'],
                     ['project_structure', 'headers', 'main_sources', 'main_executable_source', 'external_headers']],
       output=['main_objects', 'main_executable_object'],
       cacheable=True)
def compile_main_sources(arguments: StageArguments):
    resources = arguments.resources
    compiler  = arguments.compiler
    cache     = arguments.cache
    progress_bar_supplier = arguments.progress_bar_supplier
    
    if resources.activation == 0:
        headers           = resources['formatted_headers'] + resources['external_headers']
        sources           = resources['formatted_main_sources']
        executable_source = resources['formatted_main_executable_source']
    elif resources.activation == 1:
        headers           = resources['headers'] + resources['external_headers']
        sources           = resources['main_sources']
        executable_source = resources['main_executable_source']

    project_structure = resources['project_structure']
    

    resources['main_objects'] = compiler.compile_using_cache(project_structure,
                                                             headers,
                                                             sources,
                                                             cache,
                                                             progress_bar_supplier)

    if executable_source:
        yield_descriptor = compiler.get_yield_descriptor()
        resources['main_executable_object'] = yield_descriptor.get_object(project_structure.sources_root, 
                                                                          project_structure.objects_root,
                                                                          executable_source)
    else:
        resources['main_executable_object'] = None
