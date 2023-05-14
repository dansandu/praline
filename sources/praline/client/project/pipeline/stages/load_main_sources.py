from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common import ArtifactType
from praline.common.file_system import join


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
def load_main_sources(arguments: StageArguments):
    file_system       = arguments.file_system
    artifact_manifest = arguments.artifact_manifest
    resources         = arguments.resources

    
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
