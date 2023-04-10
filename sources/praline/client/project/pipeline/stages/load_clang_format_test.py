from os.path import normpath
from praline.client.project.pipeline.stages.load_clang_format import clang_format_style_file_contents, ClangFormatConfigurationError, load_clang_format
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class LoadClangFormatStageTest(TestCase):
    def test_load_clang_format_stage_with_client_configuration(self):
        normalized_executable_path = normpath('path/to/clang_format_executable')
        normalized_style_file_path = normpath('my/project/.clang-format')

        file_system   = FileSystemMock({'path/to', 'my/project'}, {normalized_executable_path: b''})
        resources     = {'project_directory': 'my/project'}
        configuration = {'clang-format-executable-path': normalized_executable_path}
        
        load_clang_format(file_system, resources, None, None, configuration, None, None)

        self.assertEqual(resources['clang_format_executable'], normalized_executable_path)

        self.assertEqual(normpath(resources['clang_format_style_file']), normalized_style_file_path)

        self.assertEqual(file_system.files[normalized_style_file_path].decode('utf-8'), clang_format_style_file_contents)

    def test_load_clang_format_stage_with_file_configuration(self):
        normalized_executable_path = normpath('path/to/clang_format_executable')
        normalized_style_file_path = normpath('my/project/.clang-format')

        file_system   = FileSystemMock({'path/to', 'my/project'}, {normalized_executable_path: b''}, on_which=lambda t: normalized_executable_path if t == 'clang-format' else None)
        resources     = {'project_directory': 'my/project'}
        configuration = {}
        
        load_clang_format(file_system, resources, None, None, configuration, None, None)

        self.assertEqual(resources['clang_format_executable'], normalized_executable_path)

        self.assertEqual(normpath(resources['clang_format_style_file']), normalized_style_file_path)

        self.assertEqual(file_system.files[normalized_style_file_path].decode('utf-8'), clang_format_style_file_contents)

    def test_load_clang_format_stage_with_user_supplied_style_file(self):
        normalized_executable_path = normpath('path/to/clang_format_executable')
        normalized_style_file_path = normpath('my/project/.clang-format')

        file_system = FileSystemMock({'path/to', 'my/project'}, {normalized_executable_path: b'', normalized_style_file_path: b'IndentWidth: 8'})

        resources     = {'project_directory': 'my/project'}
        configuration = {'clang-format-executable-path': normalized_executable_path}
        
        load_clang_format(file_system, resources, None, None, configuration, None, None)

        self.assertEqual(normpath(resources['clang_format_executable']), normalized_executable_path)

        self.assertEqual(normpath(resources['clang_format_style_file']), normalized_style_file_path)

        self.assertEqual(file_system.files[normalized_style_file_path], b'IndentWidth: 8')

    def test_load_clang_format_stage_with_no_configuration(self):
        file_system = FileSystemMock({'my/project'})
        resources = {
            'project_directory': 'my/project'
        }
        configuration = {}
        
        self.assertRaises(ClangFormatConfigurationError, load_clang_format, file_system, resources, None, None, configuration, None, None)
