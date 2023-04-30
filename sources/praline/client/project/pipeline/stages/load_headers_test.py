from os.path import normpath
from unittest import TestCase

from praline.client.project.pipeline.stages.load_headers import load_headers
from praline.common import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock


class LoadHeadersStageTest(TestCase):
    def test_load_headers_stage(self):
        file_system = FileSystemMock(
            directories={
                'project/resources/org/art/',
                'project/sources/org/art',
            },
            files={
                'project/resources/org/art/precomp.hpp': b'',
                'project/sources/org/art/a.hpp': b'',
                'project/sources/org/art/a.cpp': b'',
                'project/sources/org/art/b.hpp': b'',
                'project/sources/org/art/b.cpp': b'',
                'project/sources/org/art/executable.cpp': b'',
            }
        )

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

        load_headers(file_system, resources, None, None, None, None, None)

        expected_headers = {
            'project/sources/org/art/a.hpp',
            'project/sources/org/art/b.hpp'
        }

        self.assertEqual({normpath(p) for p in resources['headers']}, {normpath(p) for p in expected_headers})
