from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['formatted_headers', 'formatted_main_sources', 'formatted_test_sources'],
                     ['formatted_headers', 'formatted_main_sources']], exposed=True)
def format(arguments: StageArguments):
    pass
