from praline.client.project.pipeline.stages import stage
from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments, StagePredicateResult, stage
from praline.common import ArtifactType, source_file_extension, test_source_file_extension


def predicate(arguments: StagePredicateArguments):
    main_sources_root = arguments.project_structure.main_sources_root
    files             = arguments.file_system.files_in_directory(main_sources_root)
    is_library        = arguments.artifact_manifest.artifact_type == ArtifactType.library
    has_sources       = any(f.endswith(source_file_extension) and not f.endswith(test_source_file_extension) for f in files)

    if is_library and has_sources:
        return StagePredicateResult.success()
    elif is_library:
        return StagePredicateResult.failure("there are no source files to link")
    elif has_sources:
        return StagePredicateResult.failure("artifact type is not a library")
    else:
        return StagePredicateResult.failure("artifact type is not a library and there are no source files to link")


@stage(requirements=[['project_directories', 'main_objects', 'external_libraries', 'external_libraries_interfaces']],
       output=['main_library', 'main_library_interface', 'main_library_symbols_table'],
       predicate=predicate)
def link_main_library(arguments: StageArguments):
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache

    main_objects                  = resources['main_objects']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']

    (resources['main_library'],
     resources['main_library_interface'],
     resources['main_library_symbols_table']) = compiler.link_library_using_cache(main_objects,
                                                                                  external_libraries,
                                                                                  external_libraries_interfaces,
                                                                                  cache)
