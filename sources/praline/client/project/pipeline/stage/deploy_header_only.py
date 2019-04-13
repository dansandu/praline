from praline.client.project.pipeline.stage.base import stage
from praline.client.repository.remote_proxy import push_package


@stage(consumes=['header_only_package'], produces=['deployed_header_only'])
def deploy_header_only(working_directory, data, cache, arguments):
    push_package(data['header_only_package'])
    data['deployed_header_only'] = 'done'
