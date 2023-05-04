from praline.client.project.pipeline.stages.format_test_sources import format_test_sources
from praline.client.project.pipeline.stages.stage import StageArguments
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from os.path import join
from typing import Dict, List
from unittest import TestCase


class FormatTestSourcesStageTest(TestCase):
    def test_format_test_sources(self):
        root = join('project', 'sources', 'org', 'art')

        source_math    = join(root, 'math.test.cpp')
        source_vector  = join(root, 'vector.test.cpp')
        source_map     = join(root, 'map.test.cpp')
        source_request = join(root, 'request.test.cpp')

        files_to_format_checklist = [
            source_math,
            source_map,
        ]

        def on_execute(command: List[str], 
                       add_to_library_path: List[str], 
                       interactive: bool, 
                       add_to_env: Dict[str, str]):
            matches = [file for file in files_to_format_checklist if file in command]
            self.assertEqual(len(matches), 1)
            files_to_format_checklist.remove(matches[0])
            return True

        file_system = FileSystemMock(
            directories={
                root
            },
            files={
                source_math: b'math-contents',
                source_vector: b'vector-contents',
                source_map: b'map-contents',
            }, 
            on_execute=on_execute
        )

        clang_format_executable = join('path', 'to', 'clang-format')

        resources = {
            'clang_format_executable': clang_format_executable,
            'test_sources': file_system.files.keys()
        }

        cache = {
            source_vector: '2d5b04a0069bfadaadbce424db26c7a66c13afa3c621326ab0f1303c6a20ad82',
            source_map: 'stale',
            source_request: 'stale',
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=4)

        stage_arguments = StageArguments(file_system=file_system,
                                         resources=resources,
                                         cache=cache,
                                         progress_bar_supplier=progress_bar_supplier)

        format_test_sources(stage_arguments)

        expected_formatted_test_sources = {
            source_math,
            source_vector,
            source_map,
        }

        self.assertCountEqual(resources['formatted_test_sources'], expected_formatted_test_sources)

        expected_cache = {
            source_math: '38527a9ac8d06095ec3a63b5409cdf92888fd8ee721a38628b7c83765f52e182',
            source_vector: '2d5b04a0069bfadaadbce424db26c7a66c13afa3c621326ab0f1303c6a20ad82',
            source_map: 'e886d8d60c513bebdc21c4fe27f14797be5a41471d25af89c087f8db7f98e3ec'
        }

        self.assertEqual(cache, expected_cache)
