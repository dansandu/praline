from praline.client.project.pipeline.stages.stage import StageArguments, stage
from praline.common import ProjectStructure
from praline.common.file_system import FileSystem, join


class IllformedProjectError(Exception):
    pass


def check_unique(file_system: FileSystem, root: str, organization: str, artifact: str):
    if len(file_system.list_directory(root)) != 1:
        raise IllformedProjectError(
            f"'{root}' directory must only contain the '{organization}' organization directory")
    if len(file_system.list_directory(join(root, organization))) != 1:
        raise IllformedProjectError(
            f"'{join(root, organization)}' directory must only contain the '{artifact}'  artifact directory")


@stage(output=['project_structure'])
def setup_project(arguments: StageArguments):
    file_system       = arguments.file_system
    artifact_manifest = arguments.artifact_manifest
    resources         = arguments.resources

    project_directory = file_system.get_working_directory()
    target_root       = join(project_directory, 'target')
    external_root     = join(target_root, 'external')

    organization      = artifact_manifest.organization
    artifact          = artifact_manifest.artifact

    resources_root = join(project_directory, 'resources')
    sources_root   = join(project_directory, 'sources')

    directories = {
        'project_directory'         : project_directory,
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

    resources['project_structure'] = ProjectStructure(**directories)
