from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments, StagePredicateResult, stage
from praline.common import test_header_file_extension, test_source_file_extension
from praline.common.file_system import join


test_executable_contents = """\
#include "dansandu/radiance/progress_bar_console_reporter.hpp"
#include "dansandu/radiance/test_case_registry.hpp"
#include "dansandu/radiance/utility.hpp"

#include <string>

using dansandu::radiance::progress_bar_console_reporter::ProgressBarConsoleReporter;
using dansandu::radiance::test_case_registry::TestCaseRegistry;
using dansandu::radiance::utility::getEnvironmentVariable;

int main(const int, const char* const* const)
{
    const auto stageIndexString = getEnvironmentVariable("PRALINE_PROGRESS_BAR_STAGE_INDEX");
    const auto stageIndex = stageIndexString.has_value() ? std::stoi(stageIndexString.value()) : 0;

    const auto stageCountString = getEnvironmentVariable("PRALINE_PROGRESS_BAR_STAGE_COUNT");
    const auto stageCount = stageCountString.has_value() ? std::stoi(stageCountString.value()) : 0;

    auto reporter = ProgressBarConsoleReporter{stageIndex, stageCount};

    const auto testSuiteResult = TestCaseRegistry::instance().runAllTestCases(reporter);

    return !testSuiteResult.testSuiteSuccess;
}
"""


def predicate(arguments: StagePredicateArguments):
    file_system       = arguments.file_system
    project_structure = arguments.project_structure
    skip_unit_tests   = arguments.program_arguments['global']['skip_unit_tests']
    any_test_sources  = any(
        f for f in file_system.files_in_directory(project_structure.test_sources_root) 
            if f.endswith(test_header_file_extension) or f.endswith(test_source_file_extension)
    )
    
    if not skip_unit_tests and any_test_sources:
        return StagePredicateResult.success()
    elif not skip_unit_tests:
        return StagePredicateResult.failure("there are no test sources")
    elif any_test_sources:
        return StagePredicateResult.failure("the skip_unit_tests flag was used")
    else:
        return StagePredicateResult.failure("there are no test sources and the skip_unit_tests flag was used")


@stage(requirements=[['project_directories']], output=['test_sources'], predicate=predicate)
def load_test_sources(arguments: StageArguments):
    file_system       = arguments.file_system
    project_structure = arguments.project_structure
    resources         = arguments.resources

    test_executable_source = join(project_structure.test_sources_domain_root, 'executable.test.cpp')
        
    file_system.create_file_if_missing(test_executable_source, test_executable_contents)

    resources['test_sources'] = [f for f in file_system.files_in_directory(project_structure.test_sources_root) if f.endswith(test_source_file_extension)]
