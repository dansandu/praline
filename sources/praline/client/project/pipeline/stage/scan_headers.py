from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import files_in_directory


@stage(consumes=['headers_root'], produces=['headers'])
def scan_headers(working_directory, data, cache, arguments):
    data['headers'] = [f for f in files_in_directory(data['headers_root']) if f.endswith('.hpp')]
