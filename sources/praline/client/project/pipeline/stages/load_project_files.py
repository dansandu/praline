from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common import (
    ArtifactType, executable_source_file_name, source_file_extension, farseer_file_extension,
    header_file_extension,
)
from praline.common.file_system import basename, join


main_executable_source_contents = """\
#include <iostream>

int main(const int, const char* const* const)
{
    std::cout << "Hello, world!" << std::endl;
    return 0;
}
"""


@stage(
    requirements=['project_directories'], 
    output=[
        'main_resources', 'main_headers', 'main_sources', 'main_farseer_sources', 'main_executable_source',
        'test_resources', 'test_headers', 'test_sources', 'test_farseer_sources', 'test_executable_source',
    ]
)
def load_project_files(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    project_structure = arguments.project_structure

    resources['main_resources'] = file_system.files_in_directory(project_structure.main_resources_domain_root)

    resources['main_headers'] = [
        f for f in file_system.files_in_directory(project_structure.main_sources_domain_root) 
            if f.endswith(header_file_extension)
    ]

    resources['main_sources'] = [
        f for f in file_system.files_in_directory(project_structure.main_sources_domain_root) 
            if f.endswith(source_file_extension) and basename(f) != executable_source_file_name
    ]

    resources['main_farseer_sources'] = [
        f for f in file_system.files_in_directory(project_structure.main_sources_domain_root) 
            if f.endswith(farseer_file_extension)
    ]

    if arguments.artifact_manifest.artifact_type == ArtifactType.executable:
        main_executable_source = join(project_structure.main_sources_domain_root, executable_source_file_name)
        file_system.create_file_if_missing(main_executable_source, main_executable_source_contents)
        resources['main_executable_source'] = main_executable_source
    else:
        resources['main_executable_source'] = None


    resources['test_resources'] = file_system.files_in_directory(project_structure.test_resources_domain_root)

    resources['test_headers'] = [
        f for f in file_system.files_in_directory(project_structure.test_sources_domain_root)
          if f.endswith(header_file_extension)
    ]

    resources['test_sources'] = [
        f for f in file_system.files_in_directory(project_structure.test_sources_domain_root) 
            if f.endswith(source_file_extension) and basename(f) != executable_source_file_name
    ]

    resources['test_farseer_sources'] = [
        f for f in file_system.files_in_directory(project_structure.test_sources_domain_root) 
            if f.endswith(farseer_file_extension)
    ]

    test_executable_source = join(project_structure.test_sources_domain_root, executable_source_file_name)
    
    if file_system.exists(test_executable_source):
        resources['test_executable_source'] = test_executable_source
    else:
        resources['test_executable_source'] = None
