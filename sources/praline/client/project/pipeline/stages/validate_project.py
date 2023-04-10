from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, join
from typing import Any, Dict


class IllformedProjectError(Exception):
    pass


def check_unique(file_system, root, organization, artifact):
    if len(file_system.list_directory(root)) != 1:
        raise IllformedProjectError(f"'{root}' directory must only contain the '{organization}' organization directory")
    if len(file_system.list_directory(join(root, organization))) != 1:
        raise IllformedProjectError(f"'{join(root, organization)}' directory must only contain the '{artifact}' artifact directory")


@stage(requirements=[['project_directory', 'pralinefile']], output=['resources_root', 'headers_root', 'main_sources_root', 'test_sources_root'])
def validate_project(file_system: FileSystem, 
                     resources: StageResources, 
                     cache: Dict[str, Any], 
                     program_arguments: Dict[str, Any], 
                     configuration: Dict[str, Any], 
                     remote_proxy: RemoteProxy,
                     progressBarSupplier: ProgressBarSupplier):
    project_directory              = resources['project_directory']
    resources['headers_root']      = join(project_directory, 'sources')
    resources['test_sources_root'] = join(project_directory, 'sources')
    resources['resources_root']    = resources_root    = join(project_directory, 'resources')
    resources['main_sources_root'] = main_sources_root = join(project_directory, 'sources')
    
    pralinefile  = resources['pralinefile']
    organization = pralinefile['organization']
    artifact     = pralinefile['artifact']
    
    file_system.create_directory_if_missing(join(resources_root, organization, artifact))
    file_system.create_directory_if_missing(join(main_sources_root, organization, artifact))
    check_unique(file_system, resources_root, organization, artifact)        
    check_unique(file_system, main_sources_root, organization, artifact)
