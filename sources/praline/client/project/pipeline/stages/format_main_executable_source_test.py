from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.format_main_executable_source import format_main_executable_source
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from os.path import join
from typing import Dict, List
from unittest import TestCase


class FormatMainExecutableSourceStageTest(TestCase):
    def test_format_main_executable_source_stale(self):
        root = join('project', 'sources', 'org', 'art')

        source_math = join(root, 'math.cpp')
        source_exe  = join(root, 'executable.cpp')

        calls = [source_exe]

        def on_execute(command: List[str], 
                       add_to_library_path: List[str], 
                       interactive: bool, 
                       add_to_env: Dict[str, str]):
            calls.remove(source_exe)
            return True

        file_system = FileSystemMock(
            directories={
                root
            }, 
            files={
                source_math: b'math-contents',
                source_exe: b'executable-contents',
            }, 
            on_execute=on_execute
        )

        clang_format_executable = join('path', 'to', 'clang-format')

        resources = {
            'clang_format_executable': clang_format_executable,
            'main_executable_source': source_exe,
        }

        cache = {
            source_exe: 'stale'
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=1)

        with StageResources(stage='load_main_executable_source', 
                            activation=0, 
                            resources={'clang_format_executable': clang_format_executable, 'main_executable_source': source_exe},
                            constrained_output=['formatted_main_executable_source']) as resources:
            stage_arguments = StageArguments(file_system=file_system,
                                             resources=resources,
                                             cache=cache,
                                             progress_bar_supplier=progress_bar_supplier)
            format_main_executable_source(stage_arguments)

        self.assertEqual(len(calls), 0)

        self.assertCountEqual(resources['formatted_main_executable_source'], source_exe)

        expected_cache = {
            source_exe: '4b682f8b1c7ba55135e48e51ecff0f72301d182e0a10e556fc4a277eddab874c'
        }

        self.assertEqual(cache, expected_cache)

    def test_format_main_executable_source_fresh(self):
        root = join('project', 'sources', 'org', 'art')

        source_map    = join(root, 'map.cpp')
        source_exe    = join(root, 'executable.cpp')

        calls = []

        def on_execute(command: List[str], 
                       add_to_library_path: List[str], 
                       interactive: bool, 
                       add_to_env: Dict[str, str]):
            calls.remove(source_exe)
            return True

        file_system = FileSystemMock(
            directories={
                root
            }, 
            files={
                source_map: b'map-contents',
                source_exe: b'executable-contents',
            }, 
            on_execute=on_execute
        )

        clang_format_executable = join('path', 'to', 'clang-format')

        cache = {
            source_exe: '4b682f8b1c7ba55135e48e51ecff0f72301d182e0a10e556fc4a277eddab874c'
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=1)

        with StageResources(stage='load_main_executable_source', 
                            activation=0, 
                            resources={'clang_format_executable': clang_format_executable, 'main_executable_source': source_exe},
                            constrained_output=['formatted_main_executable_source']) as resources:
            stage_arguments = StageArguments(file_system=file_system,
                                             resources=resources,
                                             cache=cache,
                                             progress_bar_supplier=progress_bar_supplier)
            format_main_executable_source(stage_arguments)

        self.assertEqual(len(calls), 0)

        self.assertCountEqual(resources['formatted_main_executable_source'], source_exe)

        expected_cache = {
            source_exe: '4b682f8b1c7ba55135e48e51ecff0f72301d182e0a10e556fc4a277eddab874c'
        }

        self.assertEqual(cache, expected_cache)
