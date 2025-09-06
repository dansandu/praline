from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories', 'main_objects', 'test_objects', 
                      'external_libraries', 'external_libraries_interfaces']],
       output=['test_library', 'test_library_interface', 'test_library_symbols_table'],
       has_progress_bar=True)
def link_test_library(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache

    progress_bar_supplier = arguments.progress_bar_supplier

    executable_suffix = f'{artifact_manifest.organization}-{artifact_manifest.artifact}-executable.obj'
    main_objects = [source for source in resources['main_objects'] if not source.endswith(executable_suffix)]

    objects                       = main_objects + resources['test_objects']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']

    (resources['test_library'], 
     resources['test_library_interface'],
     resources['test_library_symbols_table']) = compiler.link_library_using_cache(
        objects, external_libraries, external_libraries_interfaces, cache, progress_bar_supplier, test_library=True)
