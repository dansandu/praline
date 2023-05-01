from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, normalized_path
from typing import Any, Dict


@stage(requirements=[['project_structure', 'main_executable_object', 'main_objects', 'test_objects', 
                      'external_libraries', 'external_libraries_interfaces']],
       output=['test_executable', 'test_executable_symbols_table'], 
       cacheable=True)
def link_test_executable(file_system: FileSystem, 
                         resources: StageResources, 
                         cache: Dict[str, Any], 
                         program_arguments: Dict[str, Any], 
                         configuration: Dict[str, Any], 
                         remote_proxy: RemoteProxy,
                         progressBarSupplier: ProgressBarSupplier):
    artifact_manifest             = configuration['artifact_manifest']
    compiler                      = configuration['compiler']
    project_structure             = resources['project_structure']
    objects                       = resources['main_objects'] + resources['test_objects']
    main_executable_object        = resources['main_executable_object']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']
    artifact_identifier           = artifact_manifest.get_artifact_identifier() + '.test'

    objects = [normalized_path(o) for o in objects]
    if main_executable_object and normalized_path(main_executable_object) in objects:
        objects.remove(normalized_path(main_executable_object))

    (resources['test_executable'], 
     resources['test_executable_symbols_table']) = compiler.link_executable_using_cache(project_structure,
                                                                                        artifact_identifier,
                                                                                        objects,
                                                                                        external_libraries,
                                                                                        external_libraries_interfaces,
                                                                                        cache)
