from praline.client.project.pipeline.stages import StageArguments, stage
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


@stage(output=['project_directories'])
def setup_project(arguments: StageArguments):
    file_system       = arguments.file_system
    project_structure = arguments.project_structure
    artifact_manifest = arguments.artifact_manifest
    resources         = arguments.resources

    for directory in vars(project_structure).values():
        file_system.create_directory_if_missing(directory)

    organization = artifact_manifest.organization
    artifact     = artifact_manifest.artifact

    check_unique(file_system, project_structure.main_resources_root, organization, artifact)
    check_unique(file_system, project_structure.main_sources_root, organization, artifact)
    
    check_unique(file_system, project_structure.test_resources_root, organization, artifact)
    check_unique(file_system, project_structure.test_sources_root, organization, artifact)

    resources['project_directories'] = True
