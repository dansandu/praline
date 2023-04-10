from os.path import normpath
from praline.client.project.pipeline.stages.load_test_sources import load_test_sources, test_executable_contents
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class LoadTestSourcesTest(TestCase):
    def test_load_test_sources(self):
        file_system = FileSystemMock({'project/sources/org/art'}, {
            'project/sources/org/art/math.hpp': b'',
            'project/sources/org/art/math.cpp': b'',
            'project/sources/org/art/math.test.cpp': b''
        })

        resources = {
            'test_sources_root': 'project/sources',
            'pralinefile': {
                'organization': 'org',
                'artifact': 'art'
            }
        }

        load_test_sources(file_system, resources, None, None, None, None, None)

        expected_test_sources = {
            'project/sources/org/art/math.test.cpp',
            'project/sources/org/art/executable.test.cpp'
        }

        self.assertEqual({normpath(p) for p in resources['test_sources']}, {normpath(p) for p in expected_test_sources})

        expected_files = {
            'project/sources/org/art/math.hpp': b'',
            'project/sources/org/art/math.cpp': b'',
            'project/sources/org/art/math.test.cpp': b'',
            'project/sources/org/art/executable.test.cpp': test_executable_contents.encode('utf-8')
        }

        self.assertEqual(file_system.files, {normpath(p): d for p, d in expected_files.items()})
