from os.path import normpath
from praline.client.project.pipeline.stages.format_headers import format_headers
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock
from unittest import TestCase


class FormatHeadersTest(TestCase):
    def test_format_headers(self):
        def on_execute(command, add_to_library_path):
            return True

        file_system = FileSystemMock(
            directories={
                'project/sources/org/art'
            }, 
            files={
                'project/sources/org/art/math.hpp': b'math-contents',
                'project/sources/org/art/vector.hpp': b'vector-contents',
                'project/sources/org/art/map.hpp': b'map-contents',
            }, 
            on_execute=on_execute
        )

        clang_format_executable = 'path/to/clang-format'

        resources = {
            'clang_format_executable': clang_format_executable,
            'headers': file_system.files.keys()
        }

        cache = {normpath(p): d for p, d in {
            'project/sources/org/art/vector.hpp': '2d5b04a0069bfadaadbce424db26c7a66c13afa3c621326ab0f1303c6a20ad82',
            'project/sources/org/art/map.hpp': 'stale',
            'project/sources/org/art/request.hpp': 'stale'
        }.items()}

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=4)

        format_headers(file_system, resources, cache, None, None, None, progress_bar_supplier)

        expected_formatted_headers = {
            'project/sources/org/art/math.hpp',
            'project/sources/org/art/vector.hpp',
            'project/sources/org/art/map.hpp'
        }

        self.assertEqual({normpath(p) for p in resources['formatted_headers']},
                         {normpath(p) for p in expected_formatted_headers})

        expected_cache = {
            'project/sources/org/art/math.hpp': '38527a9ac8d06095ec3a63b5409cdf92888fd8ee721a38628b7c83765f52e182',
            'project/sources/org/art/vector.hpp': '2d5b04a0069bfadaadbce424db26c7a66c13afa3c621326ab0f1303c6a20ad82',
            'project/sources/org/art/map.hpp': 'e886d8d60c513bebdc21c4fe27f14797be5a41471d25af89c087f8db7f98e3ec'
        }

        self.assertEqual(cache, {normpath(p): d for p, d in expected_cache.items()})
