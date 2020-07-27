from os.path import normpath
from praline.client.project.pipeline.stages.load_headers import load_headers
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class LoadHeadersTest(TestCase):
    def test_load_headers_stage(self):
        file_system = FileSystemMock({
            'project/resources/org/art/',
            'project/sources/org/art'
        }, {
            'project/resources/org/art/precomp.hpp': b'',
            'project/sources/org/art/main.hpp': b'',
            'project/sources/org/art/inc.hpp': b'',
            'project/sources/org/art/main.cpp': b''
        })

        resources = {'headers_root': 'project/sources'}

        load_headers(file_system, resources, None, None, None, None)

        expected_headers = {
            'project/sources/org/art/main.hpp',
            'project/sources/org/art/inc.hpp'
        }

        self.assertEqual({normpath(p) for p in resources['headers']}, {normpath(p) for p in expected_headers})
