from praline.client.project.pipeline.stages.test import test
from praline.client.project.pipeline.stages import StageArguments
from praline.common.testing import project_structure_dummy
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from os.path import join
from typing import Dict, List
from unittest import TestCase


class TestStageTest(TestCase):
    def test_main(self):
        executables_root        = join('project', 'target', 'executables')
        external_libraries_root = join('project', 'target', 'external', 'libraries')
        test_executable         = join('project', 'target', 'executables', 'test.exe')
        test_program_arguments  = ['test', 'program', 'arguments']

        header_length = 101

        def on_execute(command: List[str], 
                       add_to_library_path: List[str], 
                       interactive: bool, 
                       add_to_env: Dict[str, str]):
            self.assertEqual(command, [test_executable] + test_program_arguments)
            self.assertEqual(add_to_library_path, [external_libraries_root])
            self.assertTrue(interactive)
            self.assertEqual(add_to_env, {'PRALINE_PROGRESS_BAR_HEADER_LENGTH': str(header_length)})
            return True

        file_system = FileSystemMock(
            directories={
                executables_root,
                external_libraries_root,
            }, 
            files={
                test_executable: b''
            },
            on_execute=on_execute
        )

        resources = {
            'project_structure': project_structure_dummy,
            'test_executable': test_executable
        }

        program_arguments = {
            'byStage': {
                'arguments': test_program_arguments
            }
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, 0, header_length)

        stage_arguments = StageArguments(file_system=file_system, 
                                         program_arguments=program_arguments, 
                                         resources=resources,
                                         progress_bar_supplier=progress_bar_supplier)
        
        test(stage_arguments)

        self.assertEqual(resources['test_results'], 'success')
 