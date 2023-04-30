from os.path import normpath
from praline.client.project.pipeline.stages.load_resources import load_resources
from praline.common import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


class LoadResourcesStageTest(TestCase):
    def test_load_resources_stage(self):
        file_system = FileSystemMock({
            'project/resources/org/art',
            'project/sources/org/art'
        }, {
            'project/resources/org/art/app.config': b'',
            'project/resources/org/art/locale.rsx': b'',
            'project/sources/org/art/main.cpp': b'',
        })

        resources = {
            'project_structure': ProjectStructure(
                project_directory='project',
                resources_root='project/resources',
                sources_root='project/sources',
                target_root='project/target',
                objects_root='project/target/objects',
                executables_root='project/target/executables',
                libraries_root='project/target/libraries',
                libraries_interfaces_root='project/target/libraries_interfaces',
                symbols_tables_root='project/target/symbols_tables',
                external_root='project/target/external',
                external_packages_root='project/target/external/packages',
                external_headers_root='project/target/external/headers',
                external_executables_root='project/target/external/executables',
                external_libraries_root='project/target/external/libraries',
                external_libraries_interfaces_root='project/target/external/libraries_interfaces',
                external_symbols_tables_root='project/target/external/symbols_tables'
            )
        }

        load_resources(file_system, resources, None, None, None, None, None)

        expected_resources = {
            'project/resources/org/art/app.config',
            'project/resources/org/art/locale.rsx'
        }

        self.assertEqual({normpath(p) for p in resources['resources']}, {normpath(p) for p in expected_resources})
