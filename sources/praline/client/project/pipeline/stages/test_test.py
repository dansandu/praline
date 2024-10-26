from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.test import test
from praline.client.project.pipeline.stages import StageArguments
from praline.common.project_structure import get_project_structure
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from os.path import join
from typing import Dict, List
from unittest import TestCase


class TestStageTest(TestCase):
    def test_main(self):
        project_structure = get_project_structure('project', 'org', 'art')

        test_executable        = join(project_structure.executables_root, 'test.exe')
        test_program_arguments = ['test', 'program', 'arguments']

        expected_env = {
            'PRALINE_PROGRESS_BAR_STAGE_INDEX': '1',
            'PRALINE_PROGRESS_BAR_STAGE_COUNT': '5',
        }

        def on_execute(command: List[str], 
                       add_to_library_path: List[str], 
                       interactive: bool, 
                       add_to_env: Dict[str, str]):
            self.assertEqual(command, [test_executable] + test_program_arguments)
            self.assertEqual(add_to_library_path, [project_structure.external_libraries_root])
            self.assertTrue(interactive)
            self.assertEqual(add_to_env, expected_env)
            return True

        file_system = FileSystemMock(
            directories={
                project_structure.executables_root,
                project_structure.external_libraries_root,
            }, 
            files={
                test_executable: b''
            },
            on_execute=on_execute
        )

        program_arguments = {
            'byStage': {
                'arguments': test_program_arguments
            }
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, 
                                                        expected_resolution=0, 
                                                        stage_index=1, 
                                                        stage_count=5)

        with StageResources(stage='test', 
                            activation=0, 
                            resources={
                                'project_directories': True,
                                'test_executable': test_executable
                            }, 
                            constrained_output=['tests_passed']) as resources:
            stage_arguments = StageArguments(file_system=file_system,
                                             project_structure=project_structure,
                                             resources=resources,
                                             program_arguments=program_arguments, 
                                             progress_bar_supplier=progress_bar_supplier)
            test(stage_arguments)

        self.assertEqual(resources['tests_passed'], 'success')
 