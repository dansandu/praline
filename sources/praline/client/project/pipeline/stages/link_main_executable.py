from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_libraries', 'external_libraries_interfaces',
        'main_library', 'main_library_interface', 'main_executable_object',
    ],
    output=['main_executable', 'main_executable_symbols_table']
)
def link_main_executable(arguments: StageArguments):
    resources = arguments.resources
    cache     = arguments.cache
    
    libraries            = []
    libraries_interfaces = []

    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']
    main_library                  = resources['main_library']
    main_library_interface        = resources['main_library_interface']
    main_executable_object        = resources['main_executable_object']

    if arguments.skipOrExceptionIf(
        main_executable_object == None, 
        "There is no main executable object to link"
    ):
        resources['main_executable'] = None
        resources['main_executable_symbols_table'] = None
        return

    libraries.extend(external_libraries)
    libraries_interfaces.extend(external_libraries_interfaces)
    
    if main_library != None:
        libraries.append(main_library)

    if main_library_interface != None:
        libraries_interfaces.append(main_library_interface)

    (resources['main_executable'], 
     resources['main_executable_symbols_table']) = arguments.compiler.link_executable_using_cache(
        [main_executable_object],
        libraries,
        libraries_interfaces,
        cache,
        arguments.progress_bar_supplier,
        main_executable=True)
