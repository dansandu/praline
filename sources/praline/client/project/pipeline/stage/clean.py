from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import remove_directory_recursively, exists, join


@stage(exposed=True)
def clean(working_directory, data, cache, arguments):
    target = join(working_directory, 'target')
    if exists(target):
        remove_directory_recursively(target)
