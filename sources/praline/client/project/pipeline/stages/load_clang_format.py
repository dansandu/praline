from praline.client.project.pipeline.stages import StageArguments, stage
from praline.common.exception import ClangFormatConfigurationException
from praline.common.file_system import join


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


@stage(output=['clang_format_executable'])
def load_clang_format(arguments: StageArguments):
    project_structure = arguments.project_structure
    file_system       = arguments.file_system
    configuration     = arguments.configuration
    resources         = arguments.resources

    if arguments.skipOrExceptionIf(
        arguments.program_arguments['global']['skip_formatting'],
        "Cannot run tests because the skip-formatting flag was used"
    ):
        resources['clang_format_executable'] = None
        return
    
    if 'clang-format-executable-path' in configuration:
        clang_format_executable = configuration['clang-format-executable-path']
        if not file_system.is_file(clang_format_executable):
            raise ClangFormatConfigurationException(
                f"User supplied clang-format '{clang_format_executable}' is not a file")
    else:
        clang_format_executable = file_system.which('clang-format')
        if clang_format_executable is None:
            raise ClangFormatConfigurationException(
                "Coudn't find clang-format in path -- either supply it in the praline-client.config file or add it "
                "to the path environment variable")

    clang_format_style_file = join(project_structure.project_directory, '.clang-format')

    file_system.create_file_if_missing(clang_format_style_file, clang_format_style_file_contents)

    resources['clang_format_executable'] = clang_format_executable
