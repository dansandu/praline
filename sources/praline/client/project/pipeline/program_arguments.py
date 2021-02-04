from argparse import ArgumentParser, REMAINDER
from praline.client.project.pipeline.stages.stage import Stage
from typing import Any, Dict


def get_program_arguments(stages: Dict[str, Stage]) -> Dict[str, Any]:
    schema = {
        'global': [
            {
                'name'  : '--skip-unit-tests',
                'action': 'store_true',
                'dest'  : 'skip_unit_tests',
                'help'  : 'Skip unit testing. Not recommended!'
            },
            {
                'name'  : '--skip-formatting',
                'action': 'store_true',
                'dest'  : 'skip_formatting',
                'help'  : 'Skip code formatting. Not recommended!'
            },
            {
                'name'  : '--executable',
                'action': 'store_true',
                'dest'  : 'executable',
                'help'  : 'Make the project an executable by adding the executable.cpp to the sources directory.'
            },
            {
                'name'  : '--release',
                'action': 'store_true',
                'dest'  : 'release',
                'help'  : 'Do not include debug symbols and optimize compiled code. Omit this flag to generate debug symbols.'
            }
        ],
        'byStage': {name : stage.program_arguments for name, stage in stages.items() if stage.exposed}
    }
    
    parser = ArgumentParser(description="A simple way to build and manage C++ dependencies.")
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
    arguments['global']['running_stage'] = running_stage = parsed_arguments['stage']
    for stage, argument in schema['byStage'].items():
        if stage == running_stage:
            arguments['byStage'][stage] = {a['dest'] : parsed_arguments[a['dest']] for a in schema['byStage'][stage]}
        else:
            arguments['byStage'][stage] = {a['dest'] : a['default'] for a in schema['byStage'][stage]}

    return arguments
