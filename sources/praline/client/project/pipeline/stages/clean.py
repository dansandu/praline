from praline.client.project.pipeline.stages import StageArguments, stage


@stage(exposed=True, cacheable=False)
def clean(arguments: StageArguments):
    with arguments.progress_bar_supplier.create(resolution=0):
        arguments.file_system.remove_directory_recursively_if_it_exists(arguments.project_structure.target_root)
