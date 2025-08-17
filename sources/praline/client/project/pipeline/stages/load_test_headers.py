from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common import header_file_extension

@stage(requirements=[['project_directories']], output=['test_headers'])
def load_test_headers(arguments: StageArguments):
    file_system       = arguments.file_system
    resources         = arguments.resources
    project_structure = arguments.project_structure
    
    test_sources_root = project_structure.test_sources_root
    resources['test_headers'] = [f for f in file_system.files_in_directory(test_sources_root) if f.endswith(header_file_extension)]
