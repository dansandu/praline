from os.path import normpath
from praline.client.project.pipeline.stages.validate_project import validate_project, IllformedProjectError
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class ValidateProjectStageTest(TestCase):
    def test_validate_project(self):
        file_system = FileSystemMock({
            'my/project/resources/my_organization/my_artifact',
            'my/project/sources/my_organization/my_artifact'
        })

        resources = {
            'project_directory': 'my/project',
            'pralinefile': {
                'organization': 'my_organization',
                'artifact': 'my_artifact'
            }
        }

        validate_project(file_system, resources, None, None, None, None)

        expected_directories = {
            'my/project/resources/my_organization/my_artifact',
            'my/project/sources/my_organization/my_artifact'
        }

        self.assertEqual(file_system.directories, {normpath(p) for p in expected_directories})

        self.assertEqual(len(file_system.files), 0)

    def test_invalid_resources_project(self):        
        file_system = FileSystemMock({
            'my/project',
            'my/project/resources/my_organization/my_artifact',
            'my/project/sources/my_organization/my_artifact'
        }, {'my/project/resources/my_organization/somefile': b''})

        resources = {
            'project_directory': 'my/project',
            'pralinefile': {
                'organization': 'my_organization',
                'artifact': 'my_artifact'
            }
        }

        self.assertRaises(IllformedProjectError, validate_project, file_system, resources, None, None, None, None)

    def test_invalid_sources_project(self):
        file_system = FileSystemMock({
            'my/project/resources/my_organization/my_artifact',
            'my/project/sources/my_organization/my_artifact'
        }, {'my/project/sources/somefile': b''})

        resources = {
            'project_directory': 'my/project',
            'pralinefile': {
                'organization': 'my_organization',
                'artifact': 'my_artifact'
            }
        }

        self.assertRaises(IllformedProjectError, validate_project, file_system, resources, None, None, None, None)

    def test_valid_project_with_hidden_file(self):
        file_system = FileSystemMock({
            'my/project',
            'my/project/resources/my_organization/my_artifact',
            'my/project/sources/my_organization/my_artifact'
        }, {'my/project/sources/.hidden': b''})

        resources = {
            'project_directory': 'my/project',
            'pralinefile': {
                'organization': 'my_organization',
                'artifact': 'my_artifact'
            }
        }

        validate_project(file_system, resources, None, None, None, None)
