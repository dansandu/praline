from praline.client.project.pipeline.stages.clean import clean
from praline.client.project.pipeline.stages import StageArguments
from praline.common.project_structure import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from os.path import join
from unittest import TestCase


class CleanStageTest(TestCase):
    def test_clean_stage_with_target_folder(self):
        project_structure = ProjectStructure('project', 'org', 'art')

        file_system = FileSystemMock(
            directories={
                project_structure.target_root, 
                project_structure.temporary_root
            },
            files={
                join(project_structure.temporary_root, 'file.txt'): b'some text',
            },
            working_directory=project_structure.project_directory,
        )

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=0)

        stage_arguments = StageArguments(
            file_system=file_system, 
            project_structure=project_structure,
            progress_bar_supplier=progress_bar_supplier
        )

        clean(stage_arguments)

        self.assertEqual(file_system.directories, {project_structure.project_directory})

        self.assertEqual(len(file_system.files), 0)

    def test_clean_stage_without_target_folder(self):
        project_structure = ProjectStructure('project', 'org', 'art')

        file_system = FileSystemMock(
            directories={
                project_structure.project_directory
            },
            working_directory=project_structure.project_directory,
        )

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=0)

        stage_arguments = StageArguments(
            file_system=file_system, 
            project_structure=project_structure,
            progress_bar_supplier=progress_bar_supplier
        )

        clean(stage_arguments)

        self.assertEqual(file_system.directories, {project_structure.project_directory})

        self.assertEqual(len(file_system.files), 0)
