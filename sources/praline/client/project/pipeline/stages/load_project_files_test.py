from praline.client.project.pipeline.stage_resources import StageResources
from praline.client.project.pipeline.stages import StageArguments
from praline.client.project.pipeline.stages.load_project_files import load_project_files, main_executable_source_contents
from praline.common import (Architecture, ArtifactManifest, ArtifactType, ArtifactVersion, 
                            CompilerType, ExportedSymbols, Mode, Platform, executable_source_file_name)
from praline.common.project_structure import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock

from os.path import join
from unittest import TestCase


class LoadMainSourcesStageTest(TestCase):
    def test_load_project_files(self):
        artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('0.0.0.SNAPSHOT'),
            mode=Mode.debug,
            architecture=Architecture.arm,
            platform=Platform.linux,
            compiler=CompilerType.gcc,
            exported_symbols=ExportedSymbols.explicit,
            artifact_type=ArtifactType.executable,
            main_service=None,
            test_service=None,
            dependencies=[]
        )

        project_structure = ProjectStructure('project', artifact_manifest.organization, artifact_manifest.artifact)

        main_resource_path = lambda resource: join(project_structure.main_resources_domain_root, resource)
        
        main_source_path = lambda source: join(project_structure.main_sources_domain_root, source)

        test_resource_path = lambda resource: join(project_structure.test_resources_domain_root, resource)

        test_source_path = lambda source: join(project_structure.test_sources_domain_root, source)

        file_system = FileSystemMock(
            directories={
                project_structure.main_resources_domain_root,
                project_structure.main_sources_domain_root,
                project_structure.test_resources_domain_root,
                project_structure.test_sources_domain_root,
            }, 
            files={
                main_resource_path('app.config'): b'',
                main_source_path(executable_source_file_name): b'',
                main_source_path('math.hpp'): b'',
                main_source_path('math.cpp'): b'',
                main_source_path('generated.seer'): b'',
                test_resource_path('locale.rsx'):   b'',
                test_source_path('common.hpp'):     b'',
                test_source_path('math.test.cpp'):  b'',
                test_source_path('far.seer'):       b'',
                test_source_path(executable_source_file_name): b'',
            },
            working_directory=project_structure.project_directory,
        )

        with StageResources(
            stage='load_project_files', 
            resources={
                'project_directories': True
            }, 
            constrained_output=[
                'main_resources', 'main_headers', 'main_sources', 'main_farseer_sources', 'main_executable_source',
                'test_resources', 'test_headers', 'test_sources', 'test_farseer_sources', 'test_executable_source',
            ]
        ) as resources:
            stage_arguments = StageArguments(
                file_system=file_system, 
                project_structure=project_structure, 
                resources=resources,
                artifact_manifest=artifact_manifest
            )
            load_project_files(stage_arguments)

        self.assertCountEqual(resources['main_resources'], [main_resource_path('app.config')])

        self.assertCountEqual(resources['main_headers'], [main_source_path('math.hpp')])

        self.assertCountEqual(resources['main_sources'], [main_source_path('math.cpp')])

        self.assertCountEqual(resources['main_farseer_sources'], [main_source_path('generated.seer')])

        self.assertCountEqual(resources['main_executable_source'], main_source_path(executable_source_file_name))

        self.assertCountEqual(resources['test_resources'], [test_resource_path('locale.rsx')])

        self.assertCountEqual(resources['test_headers'], [test_source_path('common.hpp')])

        self.assertCountEqual(resources['test_sources'], [test_source_path('math.test.cpp')])

        self.assertCountEqual(resources['test_farseer_sources'], [test_source_path('far.seer')])

        self.assertCountEqual(resources['test_executable_source'], test_source_path(executable_source_file_name))


    def test_load_project_files_noexecutable(self):
        artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('0.0.0.SNAPSHOT'),
            mode=Mode.debug,
            architecture=Architecture.arm,
            platform=Platform.linux,
            compiler=CompilerType.gcc,
            exported_symbols=ExportedSymbols.explicit,
            artifact_type=ArtifactType.executable,
            main_service=None,
            test_service=None,
            dependencies=[]
        )

        project_structure = ProjectStructure('project', artifact_manifest.organization, artifact_manifest.artifact)

        main_source_path = lambda source: join(project_structure.main_sources_domain_root, source)

        file_system = FileSystemMock(
            directories={
                project_structure.main_resources_domain_root,
                project_structure.main_sources_domain_root,
                project_structure.test_resources_domain_root,
                project_structure.test_sources_domain_root,
            }, 
            working_directory=project_structure.project_directory,
        )

        with StageResources(
            stage='load_project_files', 
            resources={
                'project_directories': True
            }, 
            constrained_output=[
                'main_resources', 'main_headers', 'main_sources', 'main_farseer_sources', 'main_executable_source',
                'test_resources', 'test_headers', 'test_sources', 'test_farseer_sources', 'test_executable_source',
            ]
        ) as resources:
            stage_arguments = StageArguments(
                file_system=file_system, 
                project_structure=project_structure, 
                resources=resources,
                artifact_manifest=artifact_manifest
            )
            load_project_files(stage_arguments)

        self.assertCountEqual(resources['main_resources'], [])

        self.assertCountEqual(resources['main_headers'], [])

        self.assertCountEqual(resources['main_sources'], [])

        self.assertCountEqual(resources['main_farseer_sources'], [])

        self.assertCountEqual(resources['main_executable_source'], main_source_path(executable_source_file_name))

        self.assertIn(main_source_path(executable_source_file_name), file_system.files)

        self.assertEqual(
            file_system.files[main_source_path(executable_source_file_name)].decode('utf-8'), 
            main_executable_source_contents)

        self.assertCountEqual(resources['test_resources'], [])

        self.assertCountEqual(resources['test_headers'], [])

        self.assertCountEqual(resources['test_sources'], [])

        self.assertCountEqual(resources['test_farseer_sources'], [])

        self.assertIsNone(resources['test_executable_source'])
