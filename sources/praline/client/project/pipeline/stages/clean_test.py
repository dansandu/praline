from os.path import normpath
from praline.client.project.pipeline.stages.clean import clean
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class CleanStageTest(TestCase):
    def test_clean_stage_with_target_folder(self):
        file_system = FileSystemMock({'my/project/target'})
        resources   = {'project_directory': 'my/project'}

        clean(file_system, resources, None, None, None, None)

        self.assertEqual(file_system.directories, {normpath('my/project')})

    def test_clean_stage_without_target_folder(self):
        file_system       = FileSystemMock({'my/project'})
        resources         = {'project_directory': 'my/project'}

        clean(file_system, resources, None, None, None, None)

        self.assertEqual(file_system.directories, {normpath('my/project')})
