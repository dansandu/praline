from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import create_directory_if_missing, create_file_if_missing, files_in_directory, join


test_executable_contents = """#define CATCH_CONFIG_MAIN
#include "catchorg/catch/catch.hpp"
"""


@stage(consumes=['pralinefile', 'test_sources_root'], produces=['test_sources'])
def scan_test_sources(working_directory, data, cache, arguments):
    test_sources_root = data['test_sources_root']
    test_sources = [f for f in files_in_directory(test_sources_root) if f.endswith('.test.cpp')]
    if test_sources:
        pralinefile = data['pralinefile']
        test_executable_source = join(test_sources_root, pralinefile['organization'], pralinefile['artifact'], 'executable.test.cpp')
        create_file_if_missing(test_executable_source, test_executable_contents)
        if test_executable_source not in test_sources:
            test_sources.append(test_executable_source)
    data['test_sources'] = test_sources
