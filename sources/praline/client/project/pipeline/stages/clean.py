from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common.file_system import join


@stage(exposed=True)
def clean(arguments: StageArguments):
    target = join(arguments.file_system.get_working_directory(), 'target')
    arguments.file_system.remove_directory_recursively_if_it_exists(target)
