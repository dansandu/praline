from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories']], output=['test_resources'])
def load_test_resources(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    project_structure = arguments.project_structure
    
    resources['test_resources'] = file_system.files_in_directory(project_structure.test_resources_root)
