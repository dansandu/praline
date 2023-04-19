from os.path import basename, normpath
from praline.client.project.pipeline.stages.pull_dependencies import pull_dependencies
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock
from typing import Any, Dict
from unittest import TestCase
import pickle


class CompilerMock:
    def get_name(self):
        return 'clang'

    def get_architecture(self):
        return 'x64'

    def get_platform(self):
        return 'darwin'

    def get_mode(self):
        return 'release'


class RemoteProxyMock:
    def __init__(self, client_file_system):
        self.client_file_system = client_file_system
        self.packages           = {
            'fruit-apple-x64-darwin-clang-release-1.0.0.tar.gz': pickle.dumps({
                'headers/fruit/apple/apple.hpp': b'fruit-apple-hpp',
                'libraries/libfruit-apple-x64-darwin-clang-release-1.0.0.dylib': b'fruit-apple-dylib'
            }),
            'fruit-grapes-x64-darwin-clang-release-1.0.0.tar.gz': pickle.dumps({
                'headers/fruit/grapes/grapes.hpp': b'new-fruit-grapes-hpp',
                'libraries/libfruit-grapes-x64-darwin-clang-release-1.0.0.dylib': b'new-fruit-grapes-dylib'
            }),
            'fruit-waterlemon-x64-darwin-clang-release-1.0.0.tar.gz': pickle.dumps({
                'headers/fruit/waterlemon/waterlemon.hpp': b'fruit-waterlemon-hpp',
                'libraries/libfruit-waterlemon-x64-darwin-clang-release-1.0.0.dylib': b'fruit-waterlemon-dylib'
            })
        }

    def pull_package(self, package_path: str) -> None:
        package_name = basename(package_path)
        with self.client_file_system.open_file(package_path, 'wb') as f:
            f.write(self.packages[package_name])

    def push_package(self, package_path: str) -> None:
        package_name = basename(package_path)
        with self.client_file_system.open_file(package_path, 'rb') as f:
            self.packages[package_name] = f.read()

    def solve_dependencies(self, pralinefile: Dict[str, Any], architecture: str, platform: str, compiler: str, mode: str) -> Dict[str, str]:
        return {
            'fruit-apple-x64-darwin-clang-release-1.0.0.tar.gz': 'apple-hash',
            'fruit-grapes-x64-darwin-clang-release-1.0.0.tar.gz': 'new-grapes-hash',
            'fruit-waterlemon-x64-darwin-clang-release-1.0.0.tar.gz': 'waterlemon-hash'
        }


class PullDependenciesStageTest(TestCase):
    def test_pull_dependencies(self):
        pralinefile = b"""\
            organization: fruit
            artifact: banana
            version: 1.0.0
            dependencies:
            - organization: fruit
              artifact: apple
              version: 1.0.0
            """
        
        file_system = FileSystemMock(
            directories={
                'project/target/external/headers/fruit/grapes',
                'project/target/external/headers/fruit/waterlemon',
                'project/target/external/headers/fruit/raspberry',
                'project/target/external/libraries',
                'project/target/external/packages'
            }, 
            files={
                'project/target/external/headers/fruit/grapes/grapes.hpp': b'fruit-grapes-hpp',
                'project/target/external/headers/fruit/waterlemon/waterlemon.hpp': b'fruit-waterlemon-hpp',
                'project/target/external/headers/fruit/raspberry/raspberry.hpp': b'fruit-raspberry-hpp',
                'project/target/external/libraries/libfruit-grapes-x64-darwin-clang-release-1.0.0.dylib': b'fruit-grapes-dylib',
                'project/target/external/libraries/libfruit-waterlemon-x64-darwin-clang-release-1.0.0.dylib': b'fruit-waterlemon-dylib',
                'project/target/external/libraries/libfruit-raspberry-x64-darwin-clang-release-1.0.0.dylib': b'fruit-raspberry-dylib',
                'project/target/external/packages/fruit-grapes-x64-darwin-clang-release-1.0.0.tar.gz': pickle.dumps({
                    'headers/fruit/grapes/grapes.hpp': b'fruit-grapes-hpp',
                    'libraries/libfruit-grapes-x64-darwin-clang-release-1.0.0.dylib': b'fruit-grapes-dylib'
                }),
                'project/target/external/packages/fruit-waterlemon-x64-darwin-clang-release-1.0.0.tar.gz': pickle.dumps({
                    'headers/fruit/waterlemon/waterlemon.hpp': b'fruit-waterlemon-hpp',
                    'libraries/libfruit-waterlemon-x64-darwin-clang-release-1.0.0.dylib': b'fruit-waterlemon-dylib'
                }),
                'project/target/external/packages/fruit-raspberry-x64-darwin-clang-release-1.0.0.tar.gz': pickle.dumps({
                    'headers/fruit/raspberry/raspberry.hpp': b'fruit-raspberry-hpp',
                    'libraries/libfruit-raspberry-x64-darwin-clang-release-1.0.0.dylib': b'fruit-raspberry-dylib'
                })
            }
        )

        resources = {
            'project_directory': 'project',
            'pralinefile': pralinefile,
            'architecture': 'x64',
            'platform': 'darwin',
            'mode': 'release',
            'compiler': CompilerMock()
        }

        cache = {
            'fruit-grapes-x64-darwin-clang-release-1.0.0.tar.gz': 'grapes-hash',
            'fruit-waterlemon-x64-darwin-clang-release-1.0.0.tar.gz': 'waterlemon-hash',
            'fruit-raspberry-x64-darwin-clang-release-1.0.0.tar.gz': 'raspberry-hash'
        }

        program_arguments = {
            'global': {
                'logging_level': 'default',
                'exported_symbols': 'explicit'
            }
        }

        remote_proxy = RemoteProxyMock(file_system)

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=4)

        pull_dependencies(file_system, resources, cache, program_arguments, None, remote_proxy, progress_bar_supplier)

        expected_files = {
            'project/target/external/headers/fruit/apple/apple.hpp': b'fruit-apple-hpp',
            'project/target/external/headers/fruit/grapes/grapes.hpp': b'new-fruit-grapes-hpp',
            'project/target/external/headers/fruit/waterlemon/waterlemon.hpp': b'fruit-waterlemon-hpp',
            'project/target/external/libraries/libfruit-apple-x64-darwin-clang-release-1.0.0.dylib': b'fruit-apple-dylib',
            'project/target/external/libraries/libfruit-grapes-x64-darwin-clang-release-1.0.0.dylib': b'new-fruit-grapes-dylib',
            'project/target/external/libraries/libfruit-waterlemon-x64-darwin-clang-release-1.0.0.dylib': b'fruit-waterlemon-dylib',
            'project/target/external/packages/fruit-apple-x64-darwin-clang-release-1.0.0.tar.gz': pickle.dumps({
                'headers/fruit/apple/apple.hpp': b'fruit-apple-hpp',
                'libraries/libfruit-apple-x64-darwin-clang-release-1.0.0.dylib': b'fruit-apple-dylib'
            }),
            'project/target/external/packages/fruit-grapes-x64-darwin-clang-release-1.0.0.tar.gz': pickle.dumps({
                'headers/fruit/grapes/grapes.hpp': b'new-fruit-grapes-hpp',
                'libraries/libfruit-grapes-x64-darwin-clang-release-1.0.0.dylib': b'new-fruit-grapes-dylib'
            }),
            'project/target/external/packages/fruit-waterlemon-x64-darwin-clang-release-1.0.0.tar.gz': pickle.dumps({
                'headers/fruit/waterlemon/waterlemon.hpp': b'fruit-waterlemon-hpp',
                'libraries/libfruit-waterlemon-x64-darwin-clang-release-1.0.0.dylib': b'fruit-waterlemon-dylib'
            })
        }

        self.assertEqual(file_system.files, {normpath(p): d for p, d in expected_files.items()})

        expected_directories = {
            'project/target/external/packages',
            'project/target/external/resources',
            'project/target/external/headers/fruit/apple',
            'project/target/external/headers/fruit/grapes',
            'project/target/external/headers/fruit/waterlemon',
            'project/target/external/libraries',
            'project/target/external/libraries_interfaces',
            'project/target/external/symbols_tables',
            'project/target/external/executables'
        }

        self.assertEqual(file_system.directories, {normpath(p) for p in expected_directories})

        self.assertEqual(resources['external_resources_root'], normpath('project/target/external/resources'))
        
        self.assertEqual(resources['external_headers_root'], normpath('project/target/external/headers'))

        self.assertEqual(resources['external_libraries_root'], normpath('project/target/external/libraries'))

        self.assertEqual(resources['external_libraries_interfaces_root'], normpath('project/target/external/libraries_interfaces'))

        self.assertEqual(resources['external_symbols_tables_root'], normpath('project/target/external/symbols_tables'))

        self.assertEqual(resources['external_executables_root'], normpath('project/target/external/executables'))

        self.assertEqual(resources['external_resources'], [])

        expected_headers = {
            'project/target/external/headers/fruit/apple/apple.hpp',
            'project/target/external/headers/fruit/grapes/grapes.hpp',
            'project/target/external/headers/fruit/waterlemon/waterlemon.hpp'
        }

        self.assertEqual({normpath(p) for p in resources['external_headers']}, {normpath(p) for p in expected_headers})

        expected_libraries = {
            'project/target/external/libraries/libfruit-apple-x64-darwin-clang-release-1.0.0.dylib',
            'project/target/external/libraries/libfruit-grapes-x64-darwin-clang-release-1.0.0.dylib',
            'project/target/external/libraries/libfruit-waterlemon-x64-darwin-clang-release-1.0.0.dylib'
        }

        self.assertEqual({normpath(p) for p in resources['external_libraries']}, {normpath(p) for p in expected_libraries})

        self.assertEqual(resources['external_libraries_interfaces'], [])

        self.assertEqual(resources['external_symbols_tables'], [])

        self.assertEqual(resources['external_executables'], [])
