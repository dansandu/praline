from praline.client.project.pipeline.stages import StageArguments, stage


@stage(requirements=[['project_structure', 'formatted_headers', 'formatted_test_sources', 'external_headers'],
                     ['project_structure',           'headers',           'test_sources', 'external_headers']],
       output=['test_objects'],
       cacheable=True)
def compile_test_sources(arguments: StageArguments):
    resources = arguments.resources
    compiler  = arguments.compiler
    cache     = arguments.cache
    progress_bar_supplier = arguments.progress_bar_supplier

    if resources.activation == 0:
        headers           = resources['formatted_headers'] + resources['external_headers']
        sources           = resources['formatted_test_sources']
    elif resources.activation == 1:
        headers           = resources['headers'] + resources['external_headers']
        sources           = resources['test_sources']

    project_structure = resources['project_structure']

    resources['test_objects'] = compiler.compile_using_cache(project_structure,
                                                             headers,
                                                             sources,
                                                             cache,
                                                             progress_bar_supplier)
