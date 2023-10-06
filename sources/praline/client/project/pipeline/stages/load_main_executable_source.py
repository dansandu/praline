from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments, stage
from praline.common import ArtifactType
from praline.common.file_system import join


main_executable_source_contents = """\
#include <iostream>

int main(int, char**)
{
    std::cout << "Hello, world!" << std::endl;
    return 0;
}
"""


def is_executable(arguments: StagePredicateArguments):
    return arguments.artifact_manifest.artifact_type == ArtifactType.executable


@stage(requirements=[['project_structure']], output=['main_executable_source'], predicate=is_executable)
def load_main_executable_source(arguments: StageArguments):
    file_system       = arguments.file_system
    artifact_manifest = arguments.artifact_manifest
    resources         = arguments.resources

    project_structure = resources['project_structure']

    main_executable_source = join(project_structure.sources_root, 
                                  artifact_manifest.organization, 
                                  artifact_manifest.artifact, 
                                  'executable.cpp')

    resources['main_executable_source'] = main_executable_source

    file_system.create_file_if_missing(main_executable_source, main_executable_source_contents)
