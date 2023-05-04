from praline.client.project.pipeline.program_arguments import REMAINDER
from praline.client.project.pipeline.stages.stage import StageArguments, stage


program_arguments = [
    {
        'name': '--arguments',
        'action': 'store',
        'nargs': REMAINDER,
        'dest': 'arguments',
        'help': "Forward arguments to the underlying executable being run. Be warned that all proceeding arguments "
            "are forwarded and are no longer used by praline!",
        'default': []
    }
]


@stage(requirements=[['project_structure', 'test_executable']], 
       output=['test_results'],
       exposed=True, 
       program_arguments=program_arguments)
def test(arguments: StageArguments):
    file_system           = arguments.file_system
    resources             = arguments.resources
    progress_bar_supplier = arguments.progress_bar_supplier
    program_arguments     = arguments.program_arguments

    project_structure       = resources['project_structure']
    test_executable         = resources['test_executable']
    arguments               = program_arguments['byStage']['arguments']

    add_to_env = {'PRALINE_PROGRESS_BAR_HEADER_LENGTH': str(progress_bar_supplier.header_length)}

    file_system.execute_and_fail_on_bad_return([test_executable] + arguments,
                                               add_to_library_path=[project_structure.external_libraries_root],
                                               interactive=True,
                                               add_to_env=add_to_env)
    
    resources['test_results'] = 'success'
