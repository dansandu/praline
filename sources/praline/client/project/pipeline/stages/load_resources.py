from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_directories']], output=['resources'])
def load_resources(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    project_structure = arguments.compiler.project_structure
    
    resources['resources'] = file_system.files_in_directory(project_structure.resources_root)
