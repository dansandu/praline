from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.load_main_sources import load_main_sources
from praline.common.project_structure import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadMainSourcesStageTest(TestCase):
    def test_load_main_sources(self):
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
                main_resource_path('generated.cpp'): b'',
                main_source_path('math.hpp'):        b'',
                main_source_path('math.cpp'):        b'',
                test_source_path('math.test.cpp'):   b'',
            },
            working_directory=project_structure.project_directory,
        )

        with StageResources(stage='load_main_sources', 
                            activation=0, 
                            resources={'project_directories': True}, 
                            constrained_output=['main_sources']) as resources:
            stage_arguments = StageArguments(file_system=file_system, project_structure=project_structure, resources=resources)
            load_main_sources(stage_arguments)

        expected_main_sources = {
            main_source_path('math.cpp')
        }

        self.assertCountEqual(resources['main_sources'], expected_main_sources)
