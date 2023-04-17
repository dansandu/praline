from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, join
from typing import Any, Dict


test_executable_contents = """\
#define CATCH_CONFIG_RUNNER
#include "catchorg/catch/catch.hpp"
#include "dansandu/ballotin/environment.hpp"
#include "dansandu/ballotin/logging.hpp"
#include "dansandu/ballotin/progress_bar.hpp"

#include <iostream>

using dansandu::ballotin::environment::getEnvironmentVariable;
using dansandu::ballotin::logging::Level;
using dansandu::ballotin::logging::Logger;
using dansandu::ballotin::logging::UnitTestsHandler;
using dansandu::ballotin::progress_bar::ProgressBar;

class ProgressBarListener : public Catch::TestEventListenerBase
{
public:
    ProgressBarListener(Catch::ReporterConfig const& _config) : TestEventListenerBase(_config)
    {
        std::set<Catch::TestCase const*> tests;
        const auto& allTestCases = getAllTestCasesSorted(*m_config);
        Catch::TestSpec::Matches matches = _config.fullConfig()->testSpec().matchesByFilter(allTestCases, *m_config);
        const auto& invalidArgs = _config.fullConfig()->testSpec().getInvalidArgs();

        if (matches.empty() && invalidArgs.empty())
        {
            for (auto const& test : allTestCases)
                if (!test.isHidden())
                    tests.emplace(&test);
        }
        else
        {
            for (auto const& match : matches)
                tests.insert(match.tests.begin(), match.tests.end());
        }

        const auto header = std::string{"test"};
        const auto headerSize = getEnvironmentVariable("PRALINE_PROGRESS_BAR_HEADER_LENGTH");

        progressBar_ = std::make_unique<ProgressBar>(
            header, headerSize.has_value() ? std::stoi(headerSize.value()) : header.size(), tests.size(),
            [](const auto& text)
            {
                std::cout << text;
                std::cout.flush();
            });
    }

    void testCaseStarting(Catch::TestCaseInfo const& testInfo) override
    {
        progressBar_->updateSummary(testInfo.name);
    }

    void testCaseEnded(Catch::TestCaseStats const& testCaseStats) override
    {
        progressBar_->advance();
    }

    void testGroupEnded(Catch::TestGroupStats const& testGroupStats) override
    {
        progressBar_.reset();
    }

private:
    std::unique_ptr<ProgressBar> progressBar_;
};

CATCH_REGISTER_LISTENER(ProgressBarListener);

int main(const int argumentsCount, const char* const* const arguments)
{
    auto& logger = Logger::globalInstance();
    logger.setLevel(Level::debug);
    logger.addHandler("UnitTests", Level::debug, UnitTestsHandler{"unit_tests.log"});

    const auto catchResult = Catch::Session().run(argumentsCount, arguments);

    return catchResult;
}
"""


def can_run_unit_tests(file_system: FileSystem, program_arguments: Dict[str, Any], configuration: Dict[str, Any]):
    return not program_arguments['global']['skip_unit_tests'] and any(f for f in file_system.files_in_directory('sources') if f.endswith('.test.cpp'))


@stage(requirements=[['pralinefile', 'test_sources_root']], output=['test_sources'], predicate=can_run_unit_tests)
def load_test_sources(file_system: FileSystem, 
                      resources: StageResources, 
                      cache: Dict[str, Any], 
                      program_arguments: Dict[str, Any], 
                      configuration: Dict[str, Any], 
                      remote_proxy: RemoteProxy,
                      progressBarSupplier: ProgressBarSupplier):
    pralinefile            = resources['pralinefile']
    test_sources_root      = resources['test_sources_root']
    test_executable_source = join(test_sources_root, pralinefile['organization'], pralinefile['artifact'], 'executable.test.cpp')
    file_system.create_file_if_missing(test_executable_source, test_executable_contents)

    resources['test_sources'] = [f for f in file_system.files_in_directory(test_sources_root) if f.endswith('.test.cpp')]
