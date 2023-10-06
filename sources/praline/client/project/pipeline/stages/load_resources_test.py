from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.load_resources import load_resources
from praline.client.project.pipeline.stages import StageArguments
from praline.common.testing import project_structure_dummy
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadResourcesStageTest(TestCase):
    def test_load_resources_stage(self):
        app_config = join('project', 'resources', 'org', 'art', 'app.config')
        locale     = join('project', 'resources', 'org', 'art', 'locale.rsx')

        file_system = FileSystemMock(
            directories={
                join('project', 'resources', 'org', 'art'),
                join('project', 'sources', 'org', 'art'),
            }, 
            files={
                app_config: b'',
                locale: b'',
                join('project', 'sources', 'org', 'art', 'math.cpp'): b'',
            },
            working_directory='project',
        )

        with StageResources(stage='load_resources', 
                            activation=0, 
                            resources={'project_structure': project_structure_dummy}, 
                            constrained_output=['resources']) as resources:
            stage_arguments = StageArguments(file_system=file_system, resources=resources)
            load_resources(stage_arguments)

        expected_resources = {
            app_config,
            locale,
        }

        self.assertCountEqual(resources['resources'], expected_resources)
