from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_headers', 
        'main_headers', 'main_farseer_cpp_headers', 
        'test_headers', 'test_farseer_cpp_headers', 
        'test_executable_source', 'formatted_sources',
    ],
    output=['test_executable_object']
)
def compile_test_executable(arguments: StageArguments):
    resources = arguments.resources

    headers = []
    headers.extend(resources['external_headers'])
    headers.extend(resources['main_farseer_cpp_headers'])
    headers.extend(resources['test_farseer_cpp_headers'])
    headers.extend(resources['main_headers'])
    headers.extend(resources['test_headers'])

    test_executable_source = resources['test_executable_source']

    if arguments.skipOrExceptionIf(
        test_executable_source == None, 
        "There is no test executable source to compile"
    ):
        resources['test_executable_object'] = None
        return

    objects = arguments.compiler.compile_sources_using_cache(
        headers, [test_executable_source], arguments.cache, 
        arguments.progress_bar_supplier, main_sources=False)

    resources['test_executable_object'] = objects[0]
