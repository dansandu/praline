from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories', 'main_objects', 'main_executable_object', 'external_libraries', 'external_libraries_interfaces']],
       output=['main_executable', 'main_executable_symbols_table'])
def link_main_executable(arguments: StageArguments):
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache
    
    main_objects                  = resources['main_objects'] + [resources['main_executable_object']]
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']

    (resources['main_executable'], 
     resources['main_executable_symbols_table']) = compiler.link_executable_using_cache(main_objects,
                                                                                        external_libraries,
                                                                                        external_libraries_interfaces,
                                                                                        cache,
                                                                                        main_executable=True)
