from praline.client.project.pipeline.stage_resources import DeclaredResourceNotSuppliedError, StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.load_clang_format import (
    clang_format_style_file_contents, load_clang_format,
)
from praline.common.exception import ClangFormatConfigurationException
from praline.common.project_structure import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadClangFormatStageTest(TestCase):
    def test_load_clang_format_stage_with_client_configuration(self):
        executable_path = join('path', 'to', 'clang_format_executable')
        style_file_path = join('project', '.clang-format')

        project_structure = ProjectStructure('project', 'org', 'art')

        file_system = FileSystemMock(
            directories={
                join('path', 'to'), 
                project_structure.project_directory,
            }, 
            files={
                executable_path: b''
            },
            working_directory=project_structure.project_directory
        )

        configuration = {
            'clang-format-executable-path': executable_path
        }

        program_arguments = {
            'global': {
                'skip_formatting': False
            }
        }

        with StageResources(
            stage='load_clang_format', 
            resources={}, 
            constrained_output=['clang_format_executable']
        ) as resources:
            stage_arguments = StageArguments(
                file_system=file_system, 
                configuration=configuration, 
                resources=resources,
                program_arguments=program_arguments,
                project_structure=project_structure
            )
            load_clang_format(stage_arguments)

        self.assertEqual(resources['clang_format_executable'], executable_path)

        self.assertEqual(file_system.files[style_file_path].decode('utf-8'), clang_format_style_file_contents)

    def test_load_clang_format_stage_with_file_configuration(self):
        executable_path = join('path', 'to', 'clang_format_executable')
        style_file_path = join('project', '.clang-format')

        project_structure = ProjectStructure('project', 'org', 'art')

        file_system = FileSystemMock(
            directories={
                join('path', 'to'), 
                project_structure.project_directory,
            }, 
            files={
                executable_path: b''
            },
            working_directory=project_structure.project_directory,
            on_which=lambda t: executable_path if t == 'clang-format' else None
        )

        configuration = {}

        program_arguments = {
            'global': {
                'skip_formatting': False
            }
        }

        with StageResources(
            stage='load_clang_format', 
            resources={}, 
            constrained_output=['clang_format_executable']
        ) as resources:
            stage_arguments = StageArguments(
                file_system=file_system,
                configuration=configuration,
                resources=resources,
                program_arguments=program_arguments,
                project_structure=project_structure
            )
            load_clang_format(stage_arguments)

        self.assertEqual(resources['clang_format_executable'], executable_path)

        self.assertEqual(file_system.files[style_file_path].decode('utf-8'), clang_format_style_file_contents)

    def test_load_clang_format_stage_with_user_supplied_style_file(self):
        executable_path = join('path', 'to', 'clang_format_executable')
        style_file_path = join('project', '.clang-format')

        project_structure = ProjectStructure('project', 'org', 'art')

        file_system = FileSystemMock(
            directories={
                join('path', 'to'), 
                project_structure.project_directory,
            }, 
            files={
                executable_path: b'', 
                style_file_path: b'IndentWidth: 8'
            },
            working_directory=project_structure.project_directory,
            on_which=lambda _: None,
        )

        configuration = {
            'clang-format-executable-path': executable_path
        }

        program_arguments = {
            'global': {
                'skip_formatting': False
            }
        }
        
        with StageResources(
            stage='load_clang_format', 
            resources={}, 
            constrained_output=['clang_format_executable']
        ) as resources:
            stage_arguments = StageArguments(
                file_system=file_system,
                configuration=configuration,
                resources=resources,
                program_arguments=program_arguments,
                project_structure=project_structure
            )
            load_clang_format(stage_arguments)

        self.assertEqual(resources['clang_format_executable'], executable_path)

        self.assertEqual(file_system.files[style_file_path], b'IndentWidth: 8')

    def test_load_clang_format_stage_with_no_configuration(self):
        project_structure = ProjectStructure('project', 'org', 'art')

        file_system = FileSystemMock(
            directories={
                project_structure.project_directory,
            },
            working_directory=project_structure.project_directory,
            on_which=lambda _: None,
        )

        configuration = {}

        program_arguments = {
            'global': {
                'skip_formatting': False
            }
        }
        
        try:
            with StageResources(
                stage='load_clang_format',
                resources={}, 
                constrained_output=['clang_format_executable']
            ) as resources:
                stage_arguments = StageArguments(
                    file_system=file_system,
                    configuration=configuration,
                    resources=resources,
                    project_structure=project_structure,
                    program_arguments=program_arguments
                )
                self.assertRaises(ClangFormatConfigurationException, load_clang_format, stage_arguments)
        except DeclaredResourceNotSuppliedError:
            pass

    def test_load_clang_format_stage_predicate_with_skip_format_flag(self):
        project_structure = ProjectStructure('project', 'org', 'art')

        file_system = FileSystemMock(
            directories={
                project_structure.project_directory,
            },
            working_directory=project_structure.project_directory,
        )

        configuration = {}

        program_arguments = {
            'global': {
                'skip_formatting': True
            }
        }

        with StageResources(
            stage='load_clang_format', 
            resources={}, 
            constrained_output=['clang_format_executable']
        ) as resources:
            stage_arguments = StageArguments(
                file_system=file_system,
                configuration=configuration,
                resources=resources,
                program_arguments=program_arguments,
                project_structure=project_structure
            )
            load_clang_format(stage_arguments)

        self.assertIsNone(resources['clang_format_executable'])
