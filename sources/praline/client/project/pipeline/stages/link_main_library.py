from praline.client.project.pipeline.stages import stage
from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments, StagePredicateResult, stage
from praline.common import ArtifactType
from praline.common.file_system import join


def predicate(arguments: StagePredicateArguments):
    sources_root = join(arguments.file_system.get_working_directory(), 'sources')
    files        = arguments.file_system.files_in_directory(sources_root)
    is_library   = arguments.artifact_manifest.artifact_type == ArtifactType.library
    has_sources  = any(f.endswith('.cpp') and not f.endswith('.test.cpp') for f in files)

    if is_library and has_sources:
        return StagePredicateResult.success()
    elif is_library:
        return StagePredicateResult.failure("there are no source files to link")
    elif has_sources:
        return StagePredicateResult.failure("artifact type is not a library")
    else:
        return StagePredicateResult.failure("artifact type is not a library and there are no source files to link")


@stage(requirements=[['project_structure', 'main_objects', 'external_libraries', 'external_libraries_interfaces']],
       output=['main_library', 'main_library_interface', 'main_library_symbols_table'],
       predicate=predicate, cacheable=True)
def link_main_library(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache

    project_structure             = resources['project_structure']
    main_objects                  = resources['main_objects']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']
    artifact_identifier           = artifact_manifest.get_artifact_identifier()

    (resources['main_library'],
     resources['main_library_interface'],
     resources['main_library_symbols_table']) = compiler.link_library_using_cache(project_structure,
                                                                                  artifact_identifier,
                                                                                  main_objects,
                                                                                  external_libraries,
                                                                                  external_libraries_interfaces,
                                                                                  cache)
