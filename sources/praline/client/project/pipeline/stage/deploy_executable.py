from praline.client.project.pipeline.stage.base import stage
from praline.client.repository.remote_proxy import push_package


@stage(consumes=['executable_package'], produces=['deployed_executable'])
def deploy_executable(working_directory, data, cache, arguments):
    push_package(data['executable_package'])
    data['deployed_executable'] = 'done'
