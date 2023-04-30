from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common import ProjectStructure
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, join
from typing import Any, Dict


class IllformedProjectError(Exception):
    pass


def check_unique(file_system: FileSystem, root: str, organization: str, artifact: str):
    if len(file_system.list_directory(root)) != 1:
        raise IllformedProjectError(f"'{root}' directory must only contain the '{organization}' organization directory")
    if len(file_system.list_directory(join(root, organization))) != 1:
        raise IllformedProjectError(f"'{join(root, organization)}' directory must only contain the '{artifact}' artifact directory")


@stage(output=['project_structure'])
def setup_project(file_system: FileSystem, 
                  resources: StageResources, 
                  cache: Dict[str, Any], 
                  program_arguments: Dict[str, Any], 
                  configuration: Dict[str, Any], 
                  remote_proxy: RemoteProxy,
                  progressBarSupplier: ProgressBarSupplier):
    
    project_directory = file_system.get_working_directory()
    target_root       = join(project_directory, 'target')
    external_root     = join(target_root, 'external')

    artifact_manifest = configuration['artifact_manifest']
    organization      = artifact_manifest.organization
    artifact          = artifact_manifest.artifact

    resources_root = join(project_directory, 'resources')
    sources_root   = join(project_directory, 'sources')

    directories = {
        'resources_root'            : resources_root,
        'sources_root'              : sources_root,
        'target_root'               : target_root,
        'objects_root'              : join(target_root, 'objects'),
        'executables_root'          : join(target_root, 'executables'),
        'libraries_root'            : join(target_root, 'libraries'),
        'libraries_interfaces_root' : join(target_root, 'libraries_interfaces'),
        'symbols_tables_root'       : join(target_root, 'symbols_tables'),
        'external_root'                      : external_root,
        'external_packages_root'             : join(external_root, 'packages'),
        'external_headers_root'              : join(external_root, 'headers'),
        'external_executables_root'          : join(external_root, 'executables'),
        'external_libraries_root'            : join(external_root, 'libraries'),
        'external_libraries_interfaces_root' : join(external_root, 'libraries_interfaces'),
        'external_symbols_tables_root'       : join(external_root, 'symbols_tables'),
    }
    
    for directory in directories.values():
        file_system.create_directory_if_missing(directory)

    file_system.create_directory_if_missing(join(resources_root, organization, artifact))
    file_system.create_directory_if_missing(join(sources_root, organization, artifact))

    check_unique(file_system, resources_root, organization, artifact)
    check_unique(file_system, sources_root, organization, artifact)

    directories['project_directory'] = project_directory

    resources['project_structure'] = ProjectStructure(**directories)
