from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages.load_test_sources import load_test_sources, test_executable_contents
from praline.client.project.pipeline.stages import StageArguments
from praline.common import (Architecture, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            CompilerType, ExportedSymbols, Mode, Platform)
from praline.common.project_structure import get_project_structure, ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class CompilerMock:
    def __init__(self, project_structure: ProjectStructure,  artifact_manifest: ArtifactManifest):
        self.project_structure = project_structure
        self.artifact_manifest = artifact_manifest


class LoadTestSourcesStageTest(TestCase):
    def test_load_test_sources(self):
        project_structure = get_project_structure('project', 'org', 'art')

        source_path = lambda source: join(project_structure.sources_domain_root, source)

        artifact_manifest = ArtifactManifest(organization='org',
                                             artifact='art',
                                             version=ArtifactVersion.from_string('5.35.5.SNAPSHOT'),
                                             mode=Mode.debug,
                                             architecture=Architecture.arm,
                                             platform=Platform.linux,
                                             compiler=CompilerType.gcc,
                                             exported_symbols=ExportedSymbols.explicit,
                                             artifact_type=ArtifactType.library,
                                             dependencies=[])
        
        compiler = CompilerMock(project_structure, artifact_manifest)

        header_math = source_path('math.hpp')
        source_math = source_path('math.cpp')
        test_math   = source_path('math.test.cpp')
        test_main   = source_path('executable.test.cpp')

        file_system = FileSystemMock(
            directories={
                project_structure.sources_domain_root,
            },
            files={
                header_math: b'',
                source_math: b'',
                test_math: b'',
            },
            working_directory=project_structure.project_directory,
        )
        
        with StageResources(stage='load_test_sources', 
                            activation=0, 
                            resources={'project_directories': True}, 
                            constrained_output=['test_sources']) as resources:
            stage_arguments = StageArguments(file_system=file_system, compiler=compiler, resources=resources)
            load_test_sources(stage_arguments)

        expected_test_sources = {
            test_math,
            test_main,
        }

        self.assertCountEqual(resources['test_sources'], expected_test_sources)

        expected_files = {
            header_math: b'',
            source_math: b'',
            test_math: b'',
            test_main: test_executable_contents.encode('utf-8')
        }

        self.assertEqual(file_system.files, expected_files)
