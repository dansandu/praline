from praline.client.project.pipeline.program_arguments import REMAINDER
from praline.client.project.pipeline.stages.stage import StageArguments, stage


program_arguments = [
    {
        'name': '--arguments',
        'action': 'store',
        'nargs': REMAINDER,
        'dest': 'arguments',
        'help': "Forward arguments to the underlying executable being run. All proceeding arguments are forwarded "
            "and no longer used by praline!",
        'default': []
    }
]


@stage(requirements=[['main_executable', 'test_results'], ['main_executable']],
       exposed=True, 
       program_arguments=program_arguments)
def main(arguments: StageArguments):
    file_system       = arguments.file_system 
    resources         = arguments.resources
    program_arguments = arguments.program_arguments['byStage']['arguments']

    main_executable         = resources['main_executable']
    project_structure       = resources['project_structure']
    external_libraries_root = project_structure.external_libraries_root
    resources_root          = project_structure.resources_root
    
    file_system.execute_and_fail_on_bad_return([main_executable] + program_arguments,
                                               add_to_library_path=[external_libraries_root, resources_root],
                                               interactive=True)
