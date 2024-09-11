from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories', 'main_objects', 'test_objects', 'external_libraries', 'external_libraries_interfaces']],
       output=['test_executable', 'test_executable_symbols_table'], 
       cacheable=True)
def link_test_executable(arguments: StageArguments):
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache

    artifact_manifest = compiler.artifact_manifest
    executable_suffix = f'{artifact_manifest.organization}-{artifact_manifest.artifact}-executable.obj'
    main_objects = [source for source in resources['main_objects'] if not source.endswith(executable_suffix)]

    objects                       = main_objects + resources['test_objects']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']

    (resources['test_executable'], 
     resources['test_executable_symbols_table']) = compiler.link_executable_using_cache(is_test_executable=True,
                                                                                        objects=objects,
                                                                                        external_libraries=external_libraries,
                                                                                        external_libraries_interfaces=external_libraries_interfaces,
                                                                                        cache=cache)
