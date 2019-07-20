from praline.client.project.pipeline.arguments import pass_remainder_arguments
from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import execute_and_fail_on_bad_return


parameters = [
    {
        'name': '--arguments',
        'action': 'store',
        'nargs': pass_remainder_arguments,
        'dest': 'arguments',
        'help': 'Forward arguments to the underlying executable being run. Be warned that all proceeding arguments are forwarded and no longer used by praline!',
        'default': []
    }
]

@stage(consumes=['external_libraries_root', 'main_executable', 'resources_root'], exposed=True, parameters=parameters)
def run_main(working_directory, data, cache, arguments):
    execute_and_fail_on_bad_return([data['main_executable']] + arguments['arguments'], add_to_path=[data['external_libraries_root']])
