from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.load_main_headers import load_main_headers
from praline.client.project.pipeline.stages import StageArguments
from praline.common import executable_source_file_name
from praline.common.project_structure import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadMainHeadersStageTest(TestCase):
    def test_load_main_headers_stage(self):
        project_structure = ProjectStructure('project', 'org', 'art')

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
                main_source_path('a.hpp'): b'',
                main_source_path('a.cpp'): b'',
                main_source_path('b.hpp'): b'',
                main_source_path('b.cpp'): b'',
                main_source_path(executable_source_file_name): b'',
                test_source_path('c.test.hpp'): b'',
            }
        )

        with StageResources(stage='load_main_headers', 
                            activation=0, 
                            resources={'project_directories': True}, 
                            constrained_output=['main_headers']) as resources:
            stage_arguments = StageArguments(file_system=file_system, project_structure=project_structure, resources=resources)
            load_main_headers(stage_arguments)

        expected_headers = {
            main_source_path('a.hpp'): b'',
            main_source_path('b.hpp'): b'',
        }

        self.assertCountEqual(resources['main_headers'], expected_headers)
