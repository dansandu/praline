from praline.client.project.pipeline.stages.stage import StageArguments, stage


@stage(requirements=[['project_structure', 'main_executable_object', 'main_objects', 'test_objects', 
                      'external_libraries', 'external_libraries_interfaces']],
       output=['test_executable', 'test_executable_symbols_table'], 
       cacheable=True)
def link_test_executable(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache

    project_structure             = resources['project_structure']
    objects                       = resources['main_objects'] + resources['test_objects']
    main_executable_object        = resources['main_executable_object']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']
    artifact_identifier           = artifact_manifest.get_artifact_identifier() + '.test'

    if main_executable_object and main_executable_object in objects:
        objects.remove(main_executable_object)

    (resources['test_executable'], 
     resources['test_executable_symbols_table']) = compiler.link_executable_using_cache(project_structure,
                                                                                        artifact_identifier,
                                                                                        objects,
                                                                                        external_libraries,
                                                                                        external_libraries_interfaces,
                                                                                        cache)
