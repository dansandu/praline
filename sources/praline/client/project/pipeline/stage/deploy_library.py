from praline.client.project.pipeline.stage.base import stage
from praline.client.repository.remote_proxy import push_package


@stage(consumes=['library_package'], produces=['deployed_library'])
def deploy_library(working_directory, data, cache, arguments):
    push_package(data['library_package'])
    data['deployed_library'] = 'done'
