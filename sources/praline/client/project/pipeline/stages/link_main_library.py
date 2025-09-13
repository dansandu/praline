from praline.client.project.pipeline.stages import stage
from praline.client.project.pipeline.stages import StageArguments, stage


@stage(
    requirements=[
        'project_directories', 'external_libraries', 'external_libraries_interfaces', 'main_objects',
    ],
    output=['main_library', 'main_library_interface', 'main_library_symbols_table']
)
def link_main_library(arguments: StageArguments):
    resources = arguments.resources

    main_objects                  = resources['main_objects']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']

    if arguments.skipOrExceptionIf(
        len(main_objects) == 0, 
        "There are no main object files to link into a library"
    ):
        resources['main_library'] = None
        resources['main_library_interface'] = None
        resources['main_library_symbols_table'] = None
        return

    (resources['main_library'],
     resources['main_library_interface'],
     resources['main_library_symbols_table']) = arguments.compiler.link_library_using_cache(
         main_objects,
         external_libraries,
         external_libraries_interfaces,
         arguments.cache,
         arguments.progress_bar_supplier)
