from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem, join
from typing import Any, Dict


test_executable_contents = """\
#define CATCH_CONFIG_RUNNER
#include "catchorg/catch/catch.hpp"
#include "dansandu/ballotin/logging.hpp"

using dansandu::ballotin::logging::Level;
using dansandu::ballotin::logging::Logger;
using dansandu::ballotin::logging::UnitTestsHandler;

int main(const int argumentsCount, const char* const* const arguments)
{
    auto& logger = Logger::globalInstance();
    logger.setLevel(Level::debug);
    logger.addHandler("UnitTests", Level::debug, UnitTestsHandler{"unit_tests.log"});

    const auto catchResult = Catch::Session().run(argumentsCount, arguments);

    return catchResult;
}
"""


def no_unit_tests_skip(file_system: FileSystem, program_arguments: Dict[str, Any], configuration: Dict[str, Any]):
    return not program_arguments['global']['skip_unit_tests']


@stage(requirements=[['pralinefile', 'test_sources_root']], output=['test_sources'], predicate=no_unit_tests_skip)
def load_test_sources(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    pralinefile            = resources['pralinefile']
    test_sources_root      = resources['test_sources_root']
    test_executable_source = join(test_sources_root, pralinefile['organization'], pralinefile['artifact'], 'executable.test.cpp')
    file_system.create_file_if_missing(test_executable_source, test_executable_contents)

    resources['test_sources'] = [f for f in file_system.files_in_directory(test_sources_root) if f.endswith('.test.cpp')]
