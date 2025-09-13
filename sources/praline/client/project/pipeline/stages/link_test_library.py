from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_libraries', 'external_libraries_interfaces',
        'main_objects', 'test_objects',
    ],
    output=['test_library', 'test_library_interface', 'test_library_symbols_table']
)
def link_test_library(arguments: StageArguments):
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache

    main_objects                  = resources['main_objects']
    test_objects                  = resources['test_objects']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']

    if arguments.skipOrExceptionIf(
        len(test_objects) == 0, 
        "There are no main object files to link into a library"
    ):
        resources['test_library'] = None
        resources['test_library_interface'] = None
        resources['test_library_symbols_table'] = None
        return

    objects = main_objects + test_objects

    (resources['test_library'], 
     resources['test_library_interface'],
     resources['test_library_symbols_table']) = compiler.link_library_using_cache(
        objects, external_libraries, external_libraries_interfaces, cache, 
        arguments.progress_bar_supplier, test_library=True)
