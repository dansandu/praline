from os.path import normpath
from praline.client.project.pipeline.stages.load_clang_format import (
    clang_format_style_file_contents, ClangFormatConfigurationError, load_clang_format
)
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class LoadClangFormatStageTest(TestCase):
    def test_load_clang_format_stage_with_client_configuration(self):
        normalized_executable_path = normpath('path/to/clang_format_executable')
        normalized_style_file_path = normpath('my/project/.clang-format')

        file_system = FileSystemMock(
            directories={
                'path/to', 
                'my/project'
            }, 
            files={
                normalized_executable_path: b''
            },
            working_directory='my/project'
        )

        configuration = {
            'clang-format-executable-path': normalized_executable_path
        }

        resources = {}
        
        load_clang_format(file_system, resources, None, None, configuration, None, None)

        self.assertEqual(resources['clang_format_executable'], normalized_executable_path)

        self.assertEqual(normpath(resources['clang_format_style_file']), normalized_style_file_path)

        self.assertEqual(file_system.files[normalized_style_file_path].decode('utf-8'), clang_format_style_file_contents)

    def test_load_clang_format_stage_with_file_configuration(self):
        normalized_executable_path = normpath('path/to/clang_format_executable')
        normalized_style_file_path = normpath('my/project/.clang-format')

        file_system   = FileSystemMock(
            directories={
                'path/to', 
                'my/project'
            },
            files={normalized_executable_path: b''}, 
            on_which=lambda t: normalized_executable_path if t == 'clang-format' else None,
            working_directory='my/project'
        )

        resources = {}

        configuration = {}
        
        load_clang_format(file_system, resources, None, None, configuration, None, None)

        self.assertEqual(resources['clang_format_executable'], normalized_executable_path)

        self.assertEqual(normpath(resources['clang_format_style_file']), normalized_style_file_path)

        self.assertEqual(file_system.files[normalized_style_file_path].decode('utf-8'), clang_format_style_file_contents)

    def test_load_clang_format_stage_with_user_supplied_style_file(self):
        normalized_executable_path = normpath('path/to/clang_format_executable')
        normalized_style_file_path = normpath('my/project/.clang-format')

        file_system = FileSystemMock(
            directories={
                'path/to', 
                'my/project'
            }, 
            files={
                normalized_executable_path: b'', 
                normalized_style_file_path: b'IndentWidth: 8'
            },
            working_directory='my/project',
            on_which=lambda _: None,
        )

        resources = {}

        configuration = {
            'clang-format-executable-path': normalized_executable_path
        }
        
        load_clang_format(file_system, resources, None, None, configuration, None, None)

        self.assertEqual(normpath(resources['clang_format_executable']), normalized_executable_path)

        self.assertEqual(normpath(resources['clang_format_style_file']), normalized_style_file_path)

        self.assertEqual(file_system.files[normalized_style_file_path], b'IndentWidth: 8')

    def test_load_clang_format_stage_with_no_configuration(self):
        file_system = FileSystemMock(
            directories={
                'my/project'
            },
            working_directory='my/project',
            on_which=lambda _: None,
        )

        resources = {}

        configuration = {}
        
        self.assertRaises(ClangFormatConfigurationError, 
                          load_clang_format, file_system, resources, None, None, configuration, None, None)
