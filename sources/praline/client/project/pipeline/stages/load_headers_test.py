from praline.client.project.pipeline.stages.load_headers import load_headers
from praline.client.project.pipeline.stages import StageArguments
from praline.common.testing import project_structure_dummy
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadHeadersStageTest(TestCase):
    def test_load_headers_stage(self):
        file_system = FileSystemMock(
            directories={
                join('project', 'resources', 'org', 'art'),
                join('project', 'sources', 'org', 'art'),
            },
            files={
                join('project', 'resources', 'org', 'art', 'precomp.hpp'): b'',
                join('project', 'sources', 'org', 'art', 'a.hpp'): b'',
                join('project', 'sources', 'org', 'art', 'a.cpp'): b'',
                join('project', 'sources', 'org', 'art', 'b.hpp'): b'',
                join('project', 'sources', 'org', 'art', 'b.cpp'): b'',
                join('project', 'sources', 'org', 'art', 'executable.cpp'): b'',
            }
        )

        resources = {
            'project_structure': project_structure_dummy
        }

        stage_arguments = StageArguments(file_system=file_system,
                                         resources=resources)

        load_headers(stage_arguments)

        expected_headers = {
            join('project', 'sources', 'org', 'art', 'a.hpp'): b'',
            join('project', 'sources', 'org', 'art', 'b.hpp'): b'',
        }

        self.assertCountEqual(resources['headers'], expected_headers)
