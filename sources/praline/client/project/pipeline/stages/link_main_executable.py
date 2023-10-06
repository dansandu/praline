from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_structure', 'main_objects', 'main_executable_object', 'external_libraries', 'external_libraries_interfaces']],
       output=['main_executable', 'main_executable_symbols_table'], 
       cacheable=True)
def link_main_executable(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache
    
    project_structure             = resources['project_structure']
    main_objects                  = resources['main_objects'] + [resources['main_executable_object']]
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']
    artifact_identifier           = artifact_manifest.get_artifact_identifier()

    (resources['main_executable'], 
     resources['main_executable_symbols_table']) = compiler.link_executable_using_cache(project_structure,
                                                                                        artifact_identifier,
                                                                                        main_objects,
                                                                                        external_libraries,
                                                                                        external_libraries_interfaces,
                                                                                        cache)
