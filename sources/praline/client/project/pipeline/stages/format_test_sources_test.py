from os.path import normpath
from praline.client.project.pipeline.stages.format_test_sources import format_test_sources
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from typing import Dict, List
from unittest import TestCase


class FormatTestSourcesStageTest(TestCase):
    def test_format_test_sources(self):
        def on_execute(command: List[str], 
                       add_to_library_path: List[str], 
                       interactive: bool, 
                       add_to_env: Dict[str, str]):
            return True

        file_system = FileSystemMock({'project/sources/org/art'}, {
            'project/sources/org/art/math.test.cpp': b'math-contents',
            'project/sources/org/art/vector.test.cpp': b'vector-contents',
            'project/sources/org/art/map.test.cpp': b'map-contents'
        }, on_execute=on_execute)

        clang_format_executable = 'path/to/clang-format'

        resources = {
            'clang_format_executable': clang_format_executable,
            'test_sources': file_system.files.keys()
        }

        cache = {normpath(p): d for p, d in {
            'project/sources/org/art/vector.test.cpp': '2d5b04a0069bfadaadbce424db26c7a66c13afa3c621326ab0f1303c6a20ad82',
            'project/sources/org/art/map.test.cpp': 'stale',
            'project/sources/org/art/request.test.cpp': 'stale'
        }.items()}

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=4)

        format_test_sources(file_system, resources, cache, None, None, None, progress_bar_supplier)

        expected_formatted_test_sources = {
            'project/sources/org/art/math.test.cpp',
            'project/sources/org/art/vector.test.cpp',
            'project/sources/org/art/map.test.cpp'
        }

        self.assertEqual({normpath(p) for p in resources['formatted_test_sources']},
                         {normpath(p) for p in expected_formatted_test_sources})

        expected_cache = {
            'project/sources/org/art/math.test.cpp': '38527a9ac8d06095ec3a63b5409cdf92888fd8ee721a38628b7c83765f52e182',
            'project/sources/org/art/vector.test.cpp': '2d5b04a0069bfadaadbce424db26c7a66c13afa3c621326ab0f1303c6a20ad82',
            'project/sources/org/art/map.test.cpp': 'e886d8d60c513bebdc21c4fe27f14797be5a41471d25af89c087f8db7f98e3ec'
        }

        self.assertEqual(cache, {normpath(p): d for p, d in expected_cache.items()})
