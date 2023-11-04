from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_structure', 'main_objects', 'test_objects', 'external_libraries', 'external_libraries_interfaces']],
       output=['test_executable', 'test_executable_symbols_table'], 
       cacheable=True)
def link_test_executable(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache

    executable_suffix = f'{artifact_manifest.organization}-{artifact_manifest.artifact}-executable.obj'
    main_objects = [source for source in resources['main_objects'] if not source.endswith(executable_suffix)]

    project_structure             = resources['project_structure']
    objects                       = main_objects + resources['test_objects']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']
    artifact_identifier           = artifact_manifest.get_artifact_identifier() + '.test'

    (resources['test_executable'], 
     resources['test_executable_symbols_table']) = compiler.link_executable_using_cache(project_structure,
                                                                                        artifact_identifier,
                                                                                        objects,
                                                                                        external_libraries,
                                                                                        external_libraries_interfaces,
                                                                                        cache)
