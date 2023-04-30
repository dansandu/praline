from argparse import ArgumentParser, REMAINDER
from praline.client.project.pipeline.stages.stage import Stage
from praline.common import Architecture, ArtifactLoggingLevel, ArtifactType, Compiler, ExportedSymbols, Mode, Platform
from typing import Any, Dict


def get_program_arguments(stages: Dict[str, Stage]) -> Dict[str, Any]:
    schema = {
        'global': [
            {
                'name'  : '--skip-unit-tests',
                'dest'  : 'skip_unit_tests',
                'action': 'store_true',
                'help'  : 'Skip unit testing. Not recommended!'
            },
            {
                'name'  : '--skip-formatting',
                'dest'  : 'skip_formatting',
                'action': 'store_true',
                'help'  : 'Skip code formatting. Not recommended!'
            },
            {
                'name'   : '--artifact-type',
                'dest'   : 'artifact_type',
                'type'   : ArtifactType,
                'choices': list(ArtifactType),
                'help'  : "The artifact type can be either an executable or a shared library. In case of an " +
                    "executable, the main function entry point is supplied by the executable.cpp file. Overrides " +
                    "Pralinefile artifact_type."
            },
            {
                'name'   : '--mode',
                'dest'   : 'mode',
                'type'   : Mode,
                'choices': list(Mode),
                'help'  : "The debug mode generates debug symbols but doesn't optimize the code. The release mode " +
                    "doesn't generate debug symbols but does optimize the code. Overrides Pralinefile mode."
            },
            {
                'name'   : '--architecture',
                'dest'   : 'architecture',
                'type'   : Architecture,
                'choices': list(Architecture),
                'help'  : "Sets the target architecture for the artifact. Overrides Pralinefile architecture."
            },
            {
                'name'   : '--platform',
                'dest'   : 'platform',
                'type'   : Platform,
                'choices': list(Platform),
                'help'  : "Sets the target platform for the artifact. Overrides Pralinefile platform."
            },
            {
                'name'   : '--compiler',
                'dest'   : 'compiler',
                'type'   : Compiler,
                'choices': list(Compiler),
                'help'  : "Sets the target compiler for the artifact. Overrides Pralinefile compiler. If multiple" +
                    "compilers are set then the best match is chosen for the platform (e.g. gcc for linux, msvc " +
                    "for windows, etc.)."
            },
            {
                'name'   : '--exported-symbols',
                'dest'   : 'exported_symbols',
                'type'   : ExportedSymbols,
                'choices': list(ExportedSymbols),
                'help'   : "If set to explicit only symbols marked by the PRALINE_EXPORT macro will be exported " +
                    "otherwise all symbols are exported. Overrides Pralinefile exported_symbols."
            },
            {
                'name'   : '--artifact-logging-level',
                'dest'   : 'artifact_logging_level',
                'type'   : ArtifactLoggingLevel,
                'choices': list(ArtifactLoggingLevel),
                'default': ArtifactLoggingLevel.debug,
                'help'   : "Log macros with the log level above the specified value are ignored during compilation. " +
                    "Non-macro log statements are not affected by this flag. Ensure that the same value is used for " +
                    "all builds otherwise the ABI will be broken. It's recommended to leave this flag to debug to " +
                    "compile all log statements and instead use the logger object interface to set the level."
            },
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
