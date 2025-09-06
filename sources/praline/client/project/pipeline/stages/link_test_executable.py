from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[
        ['project_directories', 'test_executable_object', 'external_libraries', 'external_libraries_interfaces', 'main_library', 'main_library_interface', 'test_library', 'test_library_interface'],
        ['project_directories', 'test_executable_object', 'external_libraries', 'external_libraries_interfaces', 'main_library', 'main_library_interface'],
        ['project_directories', 'test_executable_object', 'external_libraries', 'external_libraries_interfaces', 'test_library', 'test_library_interface'],
        ['project_directories', 'test_executable_object', 'external_libraries', 'external_libraries_interfaces'],
    ],
    output=['test_executable', 'test_executable_symbols_table'],
    has_progress_bar=True)
def link_test_executable(arguments: StageArguments):
    compiler  = arguments.compiler
    resources = arguments.resources
    cache     = arguments.cache
    
    progress_bar_supplier = arguments.progress_bar_supplier

    test_objects                  = [resources['test_executable_object']]
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']

    if 'main_library' in resources:
        external_libraries.append(resources['main_library'])
        external_libraries_interfaces.append(resources['main_library_interface'])

    if 'test_library' in resources:
        external_libraries.append(resources['test_library'])
        external_libraries_interfaces.append(resources['test_library_interface'])

    (resources['test_executable'], 
     resources['test_executable_symbols_table']) = compiler.link_executable_using_cache(
        test_objects,
        external_libraries,
        external_libraries_interfaces,
        cache,
        progress_bar_supplier,
        main_executable=False)
