from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.load_test_headers import load_test_headers
from praline.client.project.pipeline.stages import StageArguments
from praline.common.project_structure import get_project_structure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadTestHeadersStageTest(TestCase):
    def test_load_test_headers_stage(self):
        project_structure = get_project_structure('project', 'org', 'art')

        main_resource_path = lambda resource: join(project_structure.main_resources_domain_root, resource)

        main_source_path = lambda source: join(project_structure.main_sources_domain_root, source)

        test_source_path = lambda source: join(project_structure.test_sources_domain_root, source)

        file_system = FileSystemMock(
            directories={
                project_structure.main_resources_domain_root,
                project_structure.main_sources_domain_root,
                project_structure.test_sources_domain_root,
            },
            files={
                main_resource_path('precomp.hpp'): b'',
                test_source_path('a.test.hpp'): b'',
                test_source_path('a.test.cpp'): b'',
                test_source_path('b.test.hpp'): b'',
                test_source_path('b.test.cpp'): b'',
                test_source_path('executable.test.cpp'): b'',
                main_source_path('c.hpp'): b'',
            }
        )

        with StageResources(stage='load_test_headers', 
                            activation=0, 
                            resources={'project_directories': True}, 
                            constrained_output=['test_headers']) as resources:
            stage_arguments = StageArguments(file_system=file_system, project_structure=project_structure, resources=resources)
            load_test_headers(stage_arguments)

        expected_headers = {
            test_source_path('a.test.hpp'): b'',
            test_source_path('b.test.hpp'): b'',
        }

        self.assertCountEqual(resources['test_headers'], expected_headers)
