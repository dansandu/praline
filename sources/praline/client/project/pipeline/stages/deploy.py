from praline.client.project.pipeline.stages.stage import StageArguments, stage


@stage(requirements=[['package']], exposed=True)
def deploy(arguments: StageArguments):
    arguments.remote_proxy.push_package(arguments.resources['package'])
