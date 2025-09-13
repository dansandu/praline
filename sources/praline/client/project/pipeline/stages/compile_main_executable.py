from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_headers', 'main_farseer_cpp_headers', 'main_headers', 
        'main_executable_source', 'formatted_sources',
    ],
    output=['main_executable_object']
)
def compile_main_executable(arguments: StageArguments):
    resources = arguments.resources

    headers = []
    headers.extend(resources['external_headers'])
    headers.extend(resources['main_farseer_cpp_headers'])
    headers.extend(resources['main_headers'])

    main_executable_source = resources['main_executable_source']

    if arguments.skipOrExceptionIf(
        main_executable_source == None, 
        "There is no main executable source to compile"
    ):
        resources['main_executable_object'] = None
        return
    
    objects = arguments.compiler.compile_sources_using_cache(
        headers, [main_executable_source], arguments.cache, 
        arguments.progress_bar_supplier, main_sources=True)
    
    resources['main_executable_object'] = objects[0]
