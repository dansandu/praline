from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.load_test_resources import load_test_resources
from praline.client.project.pipeline.stages import StageArguments
from praline.common.project_structure import get_project_structure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadTestResourcesStageTest(TestCase):
    def test_load_test_resources_stage(self):
        project_structure = get_project_structure('project', 'org', 'art')
        
        main_resource_path = lambda resource: join(project_structure.main_resources_domain_root, resource)

        test_resource_path = lambda resource: join(project_structure.test_resources_domain_root, resource)

        main_source_path = lambda source: join(project_structure.main_sources_domain_root, source)

        app_config = main_resource_path('app.config')
        locale     = main_resource_path('locale.rsx')
        math       = main_source_path('math.cpp')
        image      = test_resource_path('image.png')

        file_system = FileSystemMock(
            directories={
                project_structure.main_resources_domain_root,
                project_structure.main_sources_domain_root,
                project_structure.test_resources_domain_root,
            }, 
            files={
                app_config: b'',
                locale:     b'',
                math:       b'',
                image:      b'',
            },
            working_directory=project_structure.project_directory,
        )

        with StageResources(stage='load_test_resources', 
                            activation=0, 
                            resources={'project_directories': True}, 
                            constrained_output=['test_resources']) as resources:
            stage_arguments = StageArguments(file_system=file_system, project_structure=project_structure, resources=resources)
            load_test_resources(stage_arguments)

        expected_resources = {
            image,
        }

        self.assertCountEqual(resources['test_resources'], expected_resources)
