from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.load_main_sources import load_main_sources
from praline.common.project_structure import get_project_structure, ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class CompilerMock:
    def __init__(self, project_structure: ProjectStructure):
        self.project_structure = project_structure


class LoadMainSourcesStageTest(TestCase):
    def test_load_main_sources(self):
        project_structure = get_project_structure('project', 'org', 'art')

        compiler = CompilerMock(project_structure)

        resource_path = lambda resource: join(project_structure.resources_domain_root, resource)

        source_path = lambda source: join(project_structure.sources_domain_root, source)

        file_system = FileSystemMock(
            directories={
                project_structure.resources_domain_root,
                project_structure.sources_domain_root,
            }, 
            files={
                resource_path('generated.cpp'): b'',
                source_path('math.hpp'):        b'',
                source_path('math.cpp'):        b'',
                source_path('math.test.cpp'):   b'',
            },
            working_directory='project',
        )

        project_structure = get_project_structure('project', 'org', 'art')

        compiler = CompilerMock(project_structure)

        with StageResources(stage='load_main_sources', 
                            activation=0, 
                            resources={'project_directories': True}, 
                            constrained_output=['main_sources']) as resources:
            stage_arguments = StageArguments(file_system=file_system, compiler=compiler, resources=resources)
            load_main_sources(stage_arguments)

        expected_main_sources = {
            join('project', 'sources', 'org', 'art', 'math.cpp')
        }

        self.assertCountEqual(resources['main_sources'], expected_main_sources)
