from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_libraries', 'external_libraries_interfaces',
        'main_library', 'main_library_interface', 'test_library', 'test_library_interface',
        'test_executable_object', 
    ],
    output=['test_executable', 'test_executable_symbols_table']
)
def link_test_executable(arguments: StageArguments):
    compiler  = arguments.compiler
    resources = arguments.resources
    cache     = arguments.cache

    libraries            = []
    libraries_interfaces = []

    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']
    main_library                  = resources['main_library']
    main_library_interface        = resources['main_library_interface']
    test_library                  = resources['test_library']
    test_library_interface        = resources['test_library_interface']
    test_executable_object        = resources['test_executable_object']

    if arguments.skipOrExceptionIf(
        test_executable_object == None, 
        "There is no test executable object to link"
    ):
        resources['test_executable'] = None
        resources['test_executable_symbols_table'] = None
        return

    libraries.extend(external_libraries)
    libraries_interfaces.extend(external_libraries_interfaces)

    if main_library != None:
        libraries.append(main_library)

    if main_library_interface != None:
        libraries_interfaces.append(main_library_interface)

    if test_library != None:
        libraries.append(test_library)

    if test_library_interface != None:
        libraries_interfaces.append(test_library_interface)

    (resources['test_executable'], 
     resources['test_executable_symbols_table']) = compiler.link_executable_using_cache(
        [test_executable_object],
        libraries,
        libraries_interfaces,
        cache,
        arguments.progress_bar_supplier,
        main_executable=False)
