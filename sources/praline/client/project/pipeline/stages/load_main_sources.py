from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common import ArtifactType
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, join
from typing import Any, Dict


main_executable_contents = """\
#include <iostream>

int main(int, char**)
{
    std::cout << "Hello, world!" << std::endl;
    return 0;
}
"""


class ExecutableFileWithLibraryError(Exception):
    pass


@stage(requirements=[['project_structure']], output=['main_sources', 'main_executable_source'])
def load_main_sources(file_system: FileSystem, 
                      resources: StageResources, 
                      cache: Dict[str, Any], 
                      program_arguments: Dict[str, Any], 
                      configuration: Dict[str, Any], 
                      remote_proxy: RemoteProxy,
                      progressBarSupplier: ProgressBarSupplier):
    artifact_manifest = configuration['artifact_manifest']
    project_structure = resources['project_structure']
    main_executable_source = join(project_structure.sources_root, 
                                  artifact_manifest.organization, 
                                  artifact_manifest.artifact, 
                                  'executable.cpp')

    if artifact_manifest.artifact_type == ArtifactType.executable:
        resources['main_executable_source'] = main_executable_source
        file_system.create_file_if_missing(main_executable_source, main_executable_contents)
    elif file_system.is_file(main_executable_source):
        raise ExecutableFileWithLibraryError(
            "artifact type is not set to executable but the project contains the executable.cpp file")
    else:
        resources['main_executable_source'] = None
    
    resources['main_sources'] = [
        f for f in file_system.files_in_directory(project_structure.sources_root) 
            if f.endswith('.cpp') and not f.endswith('.test.cpp')
    ]
