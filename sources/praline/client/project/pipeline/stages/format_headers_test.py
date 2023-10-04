from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.format_headers import format_headers
from praline.client.project.pipeline.stages import StageArguments
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from os.path import join
from typing import Dict, List
from unittest import TestCase


class FormatHeadersStageTest(TestCase):
    def test_format_headers(self):
        root = join('project', 'sources', 'org', 'art')

        header_math    = join(root, 'math.hpp')
        header_vector  = join(root, 'vector.hpp')
        header_map     = join(root, 'map.hpp')
        header_request = join(root, 'request.hpp')

        files_to_format_checklist = [
            header_math,
            header_map,
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
                header_math: b'math-contents',
                header_vector: b'vector-contents',
                header_map: b'map-contents',
            }, 
            on_execute=on_execute
        )

        clang_format_executable = join('path', 'to', 'clang-format')

        cache = {
            header_vector: '2d5b04a0069bfadaadbce424db26c7a66c13afa3c621326ab0f1303c6a20ad82',
            header_math: 'stale',
            header_request: 'stale',
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=4)

        with StageResources(
            stage='format_headers',
            activation=0,
            resources={
                'clang_format_executable': clang_format_executable,
                'headers': [
                    header_math, 
                    header_vector,
                    header_map
                ],
            },
            constrained_output=['formatted_headers']
        ) as resources:
            stage_arguments = StageArguments(file_system=file_system,
                                             resources=resources,
                                             cache=cache,
                                             progress_bar_supplier=progress_bar_supplier)
            format_headers(stage_arguments)

        expected_formatted_headers = {
            header_math,
            header_map,
            header_vector,
        }

        self.assertCountEqual(resources['formatted_headers'], expected_formatted_headers)

        expected_cache = {
            header_math: '38527a9ac8d06095ec3a63b5409cdf92888fd8ee721a38628b7c83765f52e182',
            header_vector: '2d5b04a0069bfadaadbce424db26c7a66c13afa3c621326ab0f1303c6a20ad82',
            header_map: 'e886d8d60c513bebdc21c4fe27f14797be5a41471d25af89c087f8db7f98e3ec'
        }

        self.assertEqual(cache, expected_cache)

        self.assertEqual(len(files_to_format_checklist), 0)
