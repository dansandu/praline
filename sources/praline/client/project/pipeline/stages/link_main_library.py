from praline.client.project.pipeline.stages import stage
from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments, StagePredicateResult, stage
from praline.common import executable_source_file_name, source_file_extension
from praline.common.file_system import basename


def predicate(arguments: StagePredicateArguments):
    main_sources_root = arguments.project_structure.main_sources_root
    files             = arguments.file_system.files_in_directory(main_sources_root)
    has_nonexecutable_main_sources = any(basename(f) != executable_source_file_name and f.endswith(source_file_extension) for f in files)

    if has_nonexecutable_main_sources:
        return StagePredicateResult.success()
    else:
        return StagePredicateResult.failure("there are no nonexecutable main source files to link")


@stage(requirements=[['project_directories', 'main_objects', 'external_libraries', 'external_libraries_interfaces']],
       output=['main_library', 'main_library_interface', 'main_library_symbols_table'],
       predicate=predicate,
       has_progress_bar=True)
def link_main_library(arguments: StageArguments):
    compiler  = arguments.compiler
    resources = arguments.resources
    cache     = arguments.cache

    progress_bar_supplier = arguments.progress_bar_supplier

    main_objects                  = resources['main_objects']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']

    (resources['main_library'],
     resources['main_library_interface'],
     resources['main_library_symbols_table']) = compiler.link_library_using_cache(main_objects,
                                                                                  external_libraries,
                                                                                  external_libraries_interfaces,
                                                                                  cache,
                                                                                  progress_bar_supplier)
