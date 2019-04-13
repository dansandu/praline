from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import files_in_directory


@stage(consumes=['resources_root'], produces=['resources'])
def scan_resources(working_directory, data, cache, arguments):
    data['resources'] = [f for f in files_in_directory(data['resources_root'])]
