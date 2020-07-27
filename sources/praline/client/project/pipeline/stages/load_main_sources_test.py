from os.path import normpath
from praline.client.project.pipeline.stages.load_main_sources import load_main_sources, main_executable_contents
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class LoadMainSourcesTest(TestCase):
    def test_load_main_sources(self):
        file_system = FileSystemMock({
            'project/resources/org/art',
            'project/sources/org/art'
        }, {
            'project/resources/org/art/generated.cpp': b'',
            'project/sources/org/art/math.hpp': b'',
            'project/sources/org/art/math.cpp': b'',
            'project/sources/org/art/math.test.cpp': b''
        })

        resources = {
            'main_sources_root': 'project/sources',
            'pralinefile': {
                'organization': 'org',
                'artifact': 'art'
            }
        }

        program_arguments = {
            'global': {'executable': False}
        }

        load_main_sources(file_system, resources, None, program_arguments, None, None)

        expected_main_sources = {
            'project/sources/org/art/math.cpp'
        }

        self.assertEqual({normpath(p) for p in resources['main_sources']},
                         {normpath(p) for p in expected_main_sources})

    def test_load_main_sources_with_executable(self):
        file_system = FileSystemMock({'project/sources/org/art'})

        resources = {
            'main_sources_root': 'project/sources',
            'pralinefile': {
                'organization': 'org',
                'artifact': 'art'
            }
        }

        program_arguments = {
            'global': {'executable': True}
        }

        load_main_sources(file_system, resources, None, program_arguments, None, None)

        expected_files = {
            'project/sources/org/art/executable.cpp': main_executable_contents.encode('utf-8')
        }

        self.assertEqual(file_system.files, {normpath(p): d for p, d in expected_files.items()})

        self.assertEqual(normpath(resources['main_executable_source']),
                         normpath('project/sources/org/art/executable.cpp'))

        expected_main_sources = {
            'project/sources/org/art/executable.cpp'
        }

        self.assertEqual({normpath(p) for p in resources['main_sources']},
                         {normpath(p) for p in expected_main_sources})
