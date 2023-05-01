from praline.client.project.pipeline.stages.test import test
from praline.common import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from typing import Dict, List
from unittest import TestCase


class TestStageTest(TestCase):
    def test_main(self):
        executables_root        = 'project/target/executables'
        external_libraries_root = 'project/target/external/libraries'

        test_executable        = 'project/target/executables/test.exe'
        test_program_arguments = ['test', 'program', 'arguments']

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
            'project_structure': ProjectStructure(
                project_directory='project',
                resources_root='project/resources',
                sources_root='project/sources',
                target_root='project/target',
                objects_root='project/target/objects',
                executables_root=executables_root,
                libraries_root='project/target/libraries',
                libraries_interfaces_root='project/target/libraries_interfaces',
                symbols_tables_root='project/target/symbols_tables',
                external_root='project/target/external',
                external_packages_root='project/target/external/packages',
                external_headers_root='project/target/external/headers',
                external_executables_root='project/target/external/executables',
                external_libraries_root=external_libraries_root,
                external_libraries_interfaces_root='project/target/external/libraries_interfaces',
                external_symbols_tables_root='project/target/external/symbols_tables'
            ),
            'test_executable': test_executable
        }

        program_arguments = {
            'byStage': {
                'arguments': test_program_arguments
            }
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, 0, header_length)

        test(file_system, resources, None, program_arguments, None, None, progress_bar_supplier)

        self.assertIn('test_results', resources)
