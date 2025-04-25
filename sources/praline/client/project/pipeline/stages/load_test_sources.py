from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments, StagePredicateResult, stage
from praline.common import test_header_file_extension, test_source_file_extension
from praline.common.file_system import join


def predicate(arguments: StagePredicateArguments):
    file_system       = arguments.file_system
    project_structure = arguments.project_structure
    skip_unit_tests   = arguments.program_arguments['global']['skip_unit_tests']
    any_test_sources  = any(
        f.endswith(test_header_file_extension) or f.endswith(test_source_file_extension) 
            for f in file_system.files_in_directory(project_structure.test_sources_root) 
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

    resources['test_sources'] = [f for f in file_system.files_in_directory(project_structure.test_sources_root) if f.endswith(test_source_file_extension)]
