from praline.client.project.pipeline.program_arguments import REMAINDER
from praline.client.project.pipeline.stages import StageArguments, stage


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


@stage(requirements=[['project_directories', 'test_executable']], 
       output=['tests_passed'],
       exposed=True, 
       program_arguments=program_arguments,
       has_progress_bar=True)
def test(arguments: StageArguments):
    file_system           = arguments.file_system
    resources             = arguments.resources
    project_structure     = arguments.project_structure
    progress_bar_supplier = arguments.progress_bar_supplier
    program_arguments     = arguments.program_arguments

    test_executable         = resources['test_executable']
    arguments               = program_arguments['byStage']['arguments']
    external_libraries_root = project_structure.external_libraries_root

    file_system.execute_and_fail_on_bad_return(
        [test_executable] + arguments,
        add_to_library_path=[external_libraries_root],
        interactive=True,
        add_to_env={
            'PRALINE_PROGRESS_BAR_STAGE_INDEX': str(progress_bar_supplier.stage_index),
            'PRALINE_PROGRESS_BAR_STAGE_COUNT': str(progress_bar_supplier.stage_count),
            'PRALINE_PROGRESS_BAR_STAGE_NAME': progress_bar_supplier.stage_name,
        })
    
    resources['tests_passed'] = 'success'
