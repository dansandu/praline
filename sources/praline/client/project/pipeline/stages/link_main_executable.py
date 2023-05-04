from praline.client.project.pipeline.stages.stage import StageArguments, StagePredicateArguments, stage
from praline.common import ArtifactType

from os.path import join


def has_executable(arguments: StagePredicateArguments):
    sources_root = join(arguments.file_system.get_working_directory(), 'sources')
    files        = arguments.file_system.files_in_directory(sources_root)
    return (arguments.artifact_manifest.artifact_type == ArtifactType.executable and 
            any(f.endswith('.cpp') and not f.endswith('.test.cpp') for f in files))


@stage(requirements=[['project_structure', 'main_objects', 'external_libraries', 'external_libraries_interfaces']],
       output=['main_executable', 'main_executable_symbols_table'], 
       predicate=has_executable, 
       cacheable=True)
def link_main_executable(arguments: StageArguments):
    artifact_manifest = arguments.artifact_manifest
    compiler          = arguments.compiler
    resources         = arguments.resources
    cache             = arguments.cache
    
    project_structure             = resources['project_structure']
    main_objects                  = resources['main_objects']
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
