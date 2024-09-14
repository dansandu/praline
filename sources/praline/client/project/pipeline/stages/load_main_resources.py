from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories']], output=['main_resources'])
def load_main_resources(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    project_structure = arguments.project_structure
    
    resources['main_resources'] = file_system.files_in_directory(project_structure.main_resources_root)
