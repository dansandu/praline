import argparse


pass_remainder_arguments = argparse.REMAINDER

def get_arguments(stages):
    schema = {
        'global': [
            {
                'name': '--skip-unit-tests',
                'action': 'store_true',
                'dest': 'skip_unit_tests',
                'help': 'Skip unit testing. Not recommended!'
            },
            {
                'name': '--skip-formatting',
                'action': 'store_true',
                'dest': 'skip_formatting',
                'help': 'Skip code formatting. Not recommended!'
            },
            {
                'name': '--executable',
                'action': 'store_true',
                'dest': 'executable',
                'help': 'Make the project an executable by adding the executable.cpp to the sources directory.'
            }
        ],
        'byStage': {name : stage.parameters for name, stage in stages.items() if stage.exposed}
    }
    
    parser = argparse.ArgumentParser(description="A simple way to build and manage C++ dependencies.")
    
    for argument in schema['global']:
        parser.add_argument(argument['name'], **{k : v for k, v in argument.items() if k != 'name' and k != 'key'})
    
    stage_subparser = parser.add_subparsers(title='stage', dest='stage', required=True)
    
    for name, stage in stages.items():
        if stage.exposed:
            stage_parser = stage_subparser.add_parser(name)
            for argument in schema['byStage'][name]:
                stage_parser.add_argument(argument['name'], **{k : v for k, v in argument.items() if k != 'name'})

    parsed_arguments = parser.parse_args().__dict__
    arguments = {
        'global': {argument['dest'] : parsed_arguments[argument['dest']] for argument in schema['global']},
        'byStage': {}
    }
    arguments['global']['stage'] = running_stage = parsed_arguments['stage']
    for stage, argument in schema['byStage'].items():
        if stage == running_stage:
            arguments['byStage'][stage] = {a['dest'] : parsed_arguments[a['dest']] for a in schema['byStage'][stage]}
        else:
            arguments['byStage'][stage] = {a['dest'] : a['default'] for a in schema['byStage'][stage]}

    return arguments
