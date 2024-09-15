from praline.client.project.pipeline.stages import StageArguments, stage


@stage(exposed=True, cacheable=False)
def clean(arguments: StageArguments):
    target_root = arguments.project_structure.target_root
    
    arguments.file_system.remove_directory_recursively_if_it_exists(target_root)
