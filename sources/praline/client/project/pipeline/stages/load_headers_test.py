from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.load_headers import load_headers
from praline.client.project.pipeline.stages import StageArguments
from praline.common.project_structure import get_project_structure, ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class CompilerMock:
    def __init__(self, project_structure: ProjectStructure):
        self.project_structure = project_structure
    

class LoadHeadersStageTest(TestCase):
    def test_load_headers_stage(self):
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
                resource_path('precomp.hpp'): b'',
                source_path('a.hpp'): b'',
                source_path('a.cpp'): b'',
                source_path('b.hpp'): b'',
                source_path('b.cpp'): b'',
                source_path('executable.cpp'): b'',
            }
        )

        with StageResources(stage='load_headers', 
                            activation=0, 
                            resources={'project_directories': True}, 
                            constrained_output=['headers']) as resources:
            stage_arguments = StageArguments(file_system=file_system, compiler=compiler, resources=resources)
            load_headers(stage_arguments)

        expected_headers = {
            source_path('a.hpp'): b'',
            source_path('b.hpp'): b'',
        }

        self.assertCountEqual(resources['headers'], expected_headers)
