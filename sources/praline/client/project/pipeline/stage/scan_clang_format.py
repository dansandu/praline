from praline.client.project.pipeline.stage.base import stage
from praline.common.file_system import create_file_if_missing, join, which, is_file
from praline.client.configuration import configuration

clang_format_file_contents = """Language: Cpp
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


@stage(produces=['clang_format_style', 'clang_format_executable'])
def scan_clang_format(working_directory, data, cache, arguments):
    if 'clang-format' in configuration:
        clang_format_executable = configuration['clang-format']
        if not is_file(clang_format_executable):
            raise RuntimeError(f"user supplied clang-format '{clang_format_executable}' is not a file")
    else:
        clang_format_executable = which('clang-format')
        if clang_format_executable is None:
            raise RuntimeError("coudn't find clang-format in path -- either supply it in the praline-client.config file or add it to the path")
    
    data['clang_format_executable'] = clang_format_executable
    data['clang_format_style'] = clang_format_style = join(working_directory, '.clang-format')
    create_file_if_missing(clang_format_style, clang_format_file_contents)
