from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.load_resources import load_resources
from praline.client.project.pipeline.stages import StageArguments
from praline.common.project_structure import get_project_structure, ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class CompilerMock:
    def __init__(self, project_structure: ProjectStructure):
        self.project_structure = project_structure


class LoadResourcesStageTest(TestCase):
    def test_load_resources_stage(self):
        project_structure = get_project_structure('project', 'org', 'art')
        
        compiler = CompilerMock(project_structure)

        resource_path = lambda resource: join(project_structure.resources_domain_root, resource)

        source_path = lambda source: join(project_structure.sources_domain_root, source)

        app_config = resource_path('app.config')
        locale     = resource_path('locale.rsx')

        file_system = FileSystemMock(
            directories={
                project_structure.resources_domain_root,
                project_structure.sources_domain_root,
            }, 
            files={
                app_config: b'',
                locale: b'',
                source_path('math.cpp'): b'',
            },
            working_directory=project_structure.project_directory,
        )

        with StageResources(stage='load_resources', 
                            activation=0, 
                            resources={'project_directories': True}, 
                            constrained_output=['resources']) as resources:
            stage_arguments = StageArguments(file_system=file_system, compiler=compiler, resources=resources)
            load_resources(stage_arguments)

        expected_resources = {
            app_config,
            locale,
        }

        self.assertCountEqual(resources['resources'], expected_resources)
