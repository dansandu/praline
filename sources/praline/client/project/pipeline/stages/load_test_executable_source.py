from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments, StagePredicateResult, stage
from praline.common import test_executable_source_file_name
from praline.common.file_system import basename, join, relative_path


def predicate(arguments: StagePredicateArguments):
    file_system = arguments.file_system
    project_structure = arguments.project_structure
    test_executable_sources = [
        f for f in file_system.files_in_directory(project_structure.test_sources_domain_root)
            if f.endswith(test_executable_source_file_name)
    ]
    if len(test_executable_sources) == 1:
        file = test_executable_sources[0]
        if relative_path(file, project_structure.test_sources_domain_root) == basename(file):
            return StagePredicateResult.success()
        else:
            return StagePredicateResult.failure("Executable must be in root test sources domain directory")
    elif len(test_executable_sources) > 1:
        return StagePredicateResult.failure(
            f"multiple executables named '{test_executable_source_file_name}' in the test sources directory")
    elif len(test_executable_sources) == 0:
        return StagePredicateResult.failure(
            f"there is no test executable named '{test_executable_source_file_name}' in the test sources directory")


@stage(requirements=[['project_directories']], output=['test_executable_source'], predicate=predicate)
def load_test_executable_source(arguments: StageArguments):
    project_structure = arguments.project_structure
    resources         = arguments.resources

    resources['test_executable_source'] = join(
        project_structure.test_sources_domain_root, 
        test_executable_source_file_name)
