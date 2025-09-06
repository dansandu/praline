from praline.common import farseer_file_extension
from praline.client.project.pipeline.stages import StageArguments, StagePredicateArguments, StagePredicateResult, stage


def predicate(arguments: StagePredicateArguments):
    file_system       = arguments.file_system
    project_structure = arguments.project_structure
    any_farseer_sources = any(
        f.endswith(farseer_file_extension)
            for f in file_system.files_in_directory(project_structure.main_sources_domain_root) 
    )
    if any_farseer_sources:
        return StagePredicateResult.success()
    else:
        return StagePredicateResult.failure("there are no main farseer sources")


@stage(requirements=[['project_directories']], output=['main_farseer_sources'], predicate=predicate)
def load_main_farseer_sources(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    project_structure = arguments.project_structure
    
    resources['main_farseer_sources'] = [
        f for f in file_system.files_in_directory(project_structure.main_sources_root) 
            if f.endswith(farseer_file_extension)
    ]
