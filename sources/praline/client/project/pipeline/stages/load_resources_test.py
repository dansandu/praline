from os.path import normpath
from praline.client.project.pipeline.stages.load_resources import load_resources
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class LoadResourcesTest(TestCase):
    def test_load_resources_stage(self):
        file_system = FileSystemMock({
            'project/resources/org/art',
            'project/sources/org/art'
        }, {
            'project/resources/org/art/app.config': b'',
            'project/resources/org/art/locale.rsx': b'',
            'project/sources/org/art/main.cpp': b'',
        })

        resources = {'resources_root': 'project/resources'}

        load_resources(file_system, resources, None, None, None, None)

        expected_resources = {
            'project/resources/org/art/app.config',
            'project/resources/org/art/locale.rsx'
        }

        self.assertEqual({normpath(p) for p in resources['resources']}, {normpath(p) for p in expected_resources})
