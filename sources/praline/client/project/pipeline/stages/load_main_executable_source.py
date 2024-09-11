from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments, StagePredicateResult, stage
from praline.common import ArtifactType
from praline.common.file_system import join


main_executable_source_contents = """\
#include <iostream>

int main(const int, const char* const* const)
{
    std::cout << "Hello, world!" << std::endl;
    return 0;
}
"""


def predicate(arguments: StagePredicateArguments):
    artifact_manifest = arguments.compiler.artifact_manifest
    if artifact_manifest.artifact_type == ArtifactType.executable:
        return StagePredicateResult.success()
    else:
        return StagePredicateResult.failure("artifact type is not executable")


@stage(requirements=[['project_directories']], output=['main_executable_source'], predicate=predicate)
def load_main_executable_source(arguments: StageArguments):
    file_system = arguments.file_system
    compiler    = arguments.compiler
    resources   = arguments.resources

    main_executable_source = join(compiler.project_structure.sources_root, 
                                  compiler.artifact_manifest.organization, 
                                  compiler.artifact_manifest.artifact, 
                                  'executable.cpp')

    resources['main_executable_source'] = main_executable_source

    file_system.create_file_if_missing(main_executable_source, main_executable_source_contents)
