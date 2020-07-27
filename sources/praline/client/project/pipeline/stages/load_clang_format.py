from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.stage import stage
from praline.client.repository.remote_proxy import RemoteProxy
from praline.common.file_system import FileSystem, join
from typing import Any, Dict


clang_format_style_file_contents = """\
Language: Cpp
AccessModifierOffset: -4
AlignTrailingComments: true
AllowShortBlocksOnASingleLine: false
AllowShortFunctionsOnASingleLine: None
AlwaysBreakTemplateDeclarations: true
BreakBeforeBraces: Allman
ColumnLimit: 120
ConstructorInitializerAllOnOneLineOrOnePerLine: true
FixNamespaceComments: false
IndentWidth: 4
PointerAlignment: Left
ReflowComments: true
SortIncludes: true
SortUsingDeclarations: true
SpaceAfterTemplateKeyword: false
SpacesInAngles: false
UseTab: Never
"""


class ClangFormatConfigurationError(Exception):
    pass


def predicate(file_system: FileSystem, program_arguments: Dict[str, Any], configuration: Dict[str, Any]):
    return not program_arguments['global']['skip_formatting']


@stage(requirements=[['project_directory']],
       output=['clang_format_style_file', 'clang_format_executable'],
       predicate=predicate)
def load_clang_format(file_system: FileSystem, resources: StageResources, cache: Dict[str, Any], program_arguments: Dict[str, Any], configuration: Dict[str, Any], remote_proxy: RemoteProxy):
    if 'clang-format-executable-path' in configuration:
        clang_format_executable = configuration['clang-format-executable-path']
        if not file_system.is_file(clang_format_executable):
            raise ClangFormatConfigurationError(f"user supplied clang-format '{clang_format_executable}' is not a file")
    else:
        clang_format_executable = file_system.which('clang-format')
        if clang_format_executable is None:
            raise ClangFormatConfigurationError("coudn't find clang-format in path -- either supply it in the praline-client.config file or add it to the path environment variable")
    
    project_directory = resources['project_directory']
    resources['clang_format_executable'] = clang_format_executable
    resources['clang_format_style_file'] = clang_format_style_file = join(project_directory, '.clang-format')
    file_system.create_file_if_missing(clang_format_style_file, clang_format_style_file_contents)
