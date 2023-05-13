from praline.client.project.pipeline.stages.stage import StageArguments, stage


@stage(requirements=[['project_structure']], output=['resources'])
def load_resources(arguments: StageArguments):
    file_system = arguments.file_system
    resources   = arguments.resources
    
    resources['resources'] = file_system.files_in_directory(resources['project_structure'].resources_root)
