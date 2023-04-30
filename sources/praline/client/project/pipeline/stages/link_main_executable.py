from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common import ArtifactType
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.compiling.compiler import link_executable_using_cache
from praline.common.file_system import FileSystem
from typing import Any, Dict


def has_executable(file_system: FileSystem, program_arguments: Dict[str, Any], configuration: Dict[str, Any]):
    return configuration['artifact_manifest'].artifact_type == ArtifactType.executable


@stage(requirements=[['project_structure', 'main_objects', 'external_libraries', 'external_libraries_interfaces']],
       output=['main_executable', 'main_executable_symbols_table'], 
       predicate=has_executable, 
       cacheable=True)
def link_main_executable(file_system: FileSystem, 
                         resources: StageResources, 
                         cache: Dict[str, Any], 
                         program_arguments: Dict[str, Any], 
                         configuration: Dict[str, Any], 
                         remote_proxy: RemoteProxy,
                         progressBarSupplier: ProgressBarSupplier):
    artifact_manifest             = configuration['artifact_manifest']
    compiler                      = configuration['compiler']
    project_structure             = resources['project_structure']
    main_objects                  = resources['main_objects']
    external_libraries            = resources['external_libraries']
    external_libraries_interfaces = resources['external_libraries_interfaces']
    artifact_identifier           = artifact_manifest.get_artifact_identifier()

    (resources['main_executable'], 
     resources['main_executable_symbols_table']) = link_executable_using_cache(file_system,
                                                                               project_structure,
                                                                               compiler,
                                                                               artifact_identifier,
                                                                               main_objects,
                                                                               external_libraries,
                                                                               external_libraries_interfaces,
                                                                               cache)
