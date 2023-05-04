from praline.client.project.pipeline.stages.stage import StageArguments
from praline.client.project.pipeline.stages.load_clang_format import (
    clang_format_style_file_contents, ClangFormatConfigurationError, load_clang_format
)
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadClangFormatStageTest(TestCase):
    def test_load_clang_format_stage_with_client_configuration(self):
        normalized_executable_path = join('path', 'to', 'clang_format_executable')
        normalized_style_file_path = join('project', '.clang-format')

        file_system = FileSystemMock(
            directories={
                join('path', 'to'), 
                'project',
            }, 
            files={
                normalized_executable_path: b''
            },
            working_directory='project'
        )

        configuration = {
            'clang-format-executable-path': normalized_executable_path
        }

        resources = {}

        stage_arguments = StageArguments(file_system=file_system,
                                         configuration=configuration,
                                         resources=resources)
        
        load_clang_format(stage_arguments)

        self.assertEqual(resources['clang_format_executable'], normalized_executable_path)

        self.assertCountEqual(resources['clang_format_style_file'], normalized_style_file_path)

        self.assertEqual(file_system.files[normalized_style_file_path].decode('utf-8'), clang_format_style_file_contents)

    def test_load_clang_format_stage_with_file_configuration(self):
        normalized_executable_path = join('path', 'to', 'clang_format_executable')
        normalized_style_file_path = join('project', '.clang-format')

        file_system   = FileSystemMock(
            directories={
                join('path', 'to'), 
                'project',
            },
            files={normalized_executable_path: b''}, 
            on_which=lambda t: normalized_executable_path if t == 'clang-format' else None,
            working_directory='project'
        )

        resources = {}

        configuration = {}
        
        stage_arguments = StageArguments(file_system=file_system,
                                         configuration=configuration,
                                         resources=resources)
        
        load_clang_format(stage_arguments)

        self.assertEqual(resources['clang_format_executable'], normalized_executable_path)

        self.assertCountEqual(resources['clang_format_style_file'], normalized_style_file_path)

        self.assertEqual(file_system.files[normalized_style_file_path].decode('utf-8'), clang_format_style_file_contents)

    def test_load_clang_format_stage_with_user_supplied_style_file(self):
        normalized_executable_path = join('path', 'to', 'clang_format_executable')
        normalized_style_file_path = join('project', '.clang-format')

        file_system = FileSystemMock(
            directories={
                join('path', 'to'), 
                'project',
            }, 
            files={
                normalized_executable_path: b'', 
                normalized_style_file_path: b'IndentWidth: 8'
            },
            working_directory='project',
            on_which=lambda _: None,
        )

        resources = {}

        configuration = {
            'clang-format-executable-path': normalized_executable_path
        }
        
        stage_arguments = StageArguments(file_system=file_system,
                                         configuration=configuration,
                                         resources=resources)
        
        load_clang_format(stage_arguments)

        self.assertEqual(resources['clang_format_executable'], normalized_executable_path)

        self.assertEqual(resources['clang_format_style_file'], normalized_style_file_path)

        self.assertEqual(file_system.files[normalized_style_file_path], b'IndentWidth: 8')

    def test_load_clang_format_stage_with_no_configuration(self):
        file_system = FileSystemMock(
            directories={
                'project'
            },
            working_directory='project',
            on_which=lambda _: None,
        )

        resources = {}

        configuration = {}
        
        stage_arguments = StageArguments(file_system=file_system,
                                         configuration=configuration,
                                         resources=resources)

        self.assertRaises(ClangFormatConfigurationError, load_clang_format, stage_arguments)
