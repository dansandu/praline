from praline.client.project.pipeline.stages.clean import clean
from praline.client.project.pipeline.stages import StageArguments
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class CleanStageTest(TestCase):
    def test_clean_stage_with_target_folder(self):
        file_system = FileSystemMock(
            directories={
                join('project', 'target'), 
            },
            working_directory='project',
        )

        stage_arguments = StageArguments(file_system=file_system)

        clean(stage_arguments)

        self.assertEqual(file_system.directories, {'project'})

    def test_clean_stage_without_target_folder(self):
        file_system = FileSystemMock(
            directories={
                'project'
            },
            working_directory='project',
        )

        stage_arguments = StageArguments(file_system=file_system)

        clean(stage_arguments)

        self.assertEqual(file_system.directories, {'project'})
