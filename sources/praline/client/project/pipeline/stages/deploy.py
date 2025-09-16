from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=['package'], exposed=True)
def deploy(arguments: StageArguments):
    package = arguments.resources['package']
    
    with arguments.progress_bar_supplier.create(resolution=0) as progress_bar:
        progress_bar.update_description(package)
        arguments.remote_proxy.push_package(package)
