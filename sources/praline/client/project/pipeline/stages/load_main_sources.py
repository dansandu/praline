from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common import source_file_extension, test_source_file_extension


@stage(requirements=[['project_directories']], output=['main_sources'])
def load_main_sources(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    project_structure = arguments.project_structure

    resources['main_sources'] = [
        f for f in file_system.files_in_directory(project_structure.main_sources_root) 
            if f.endswith(source_file_extension) and not f.endswith(test_source_file_extension)
    ]
