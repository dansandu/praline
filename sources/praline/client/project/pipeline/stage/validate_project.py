from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import create_directory_if_missing, create_file_if_missing, join, top_level_entries_in_directory

main_executable_contents = """#include <iostream>

int main(int, char**) {
    std::cout << "Hello, world!";
    return 0;
}
"""


def check_unique(root, organization, artifact):
    if len([e for e in top_level_entries_in_directory(root) if not e.name.startswith('.')]) != 1:
        raise RuntimeError(f"'{root}' directory must only contain the '{organization}' organization directory")

    if len([e for e in top_level_entries_in_directory(join(root, organization)) if not e.name.startswith('.')]) != 1:
        raise RuntimeError(f"'{join(root, organization)}' directory must only contain the '{artifact}' artifact directory")


@stage(consumes=['pralinefile'], produces=['resources_root', 'headers_root', 'main_sources_root', 'test_sources_root'])
def validate_project(working_directory, data, cache, arguments):
    data['resources_root']  = resources_root = join(working_directory, 'resources')
    data['headers_root'] = join(working_directory, 'sources')
    data['main_sources_root'] = main_sources_root = join(working_directory, 'sources')
    data['test_sources_root'] = join(working_directory, 'sources')
    
    pralinefile = data['pralinefile']
    organization = pralinefile['organization']
    artifact = pralinefile['artifact']
    
    create_directory_if_missing(join(resources_root, organization, artifact))
    check_unique(resources_root, organization, artifact)
    if arguments['executable']:
        create_file_if_missing(join(main_sources_root, organization, artifact, 'executable.cpp'), main_executable_contents)
    else:
        create_directory_if_missing(join(main_sources_root, organization, artifact))
    check_unique(main_sources_root, organization, artifact)
