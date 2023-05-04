from praline.common import (Architecture, ArtifactManifest, ArtifactVersion, ArtifactType, ArtifactDependency, 
                            ArtifactLoggingLevel, Compiler, ExportedSymbols, Mode, DependencyScope, 
                            DependencyVersion, Platform)
from praline.common.package import (InvalidManifestFileError, get_matching_packages, read_artifact_manifest, 
                                    split_package_version, write_artifact_manifest, get_packages_from_directory,
                                    get_package_dependencies_from_archive)
from praline.common.testing.file_system_mock import ArchiveMock, FileSystemMock

import pickle
from os.path import join
from unittest import TestCase


class PackageTest(TestCase):
    def test_write_artifact_manifest(self):
        file_system = FileSystemMock(
            directories={
                'target'
            }
        )

        expected_artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('7.5.2'),
            mode=Mode.debug,
            architecture=Architecture.x64,
            platform=Platform.linux,
            compiler=Compiler.gcc,
            exported_symbols=ExportedSymbols.explicit,
            artifact_type=ArtifactType.library,
            artifact_logging_level=ArtifactLoggingLevel.debug,
            dependencies=[
                ArtifactDependency(organization='org2',
                                   artifact='art2',
                                   version=DependencyVersion.from_string('1.2.4.SNAPSHOT'),
                                   scope=DependencyScope.main)
            ]
        )

        manifest_file = join('target', '.manifest')

        write_artifact_manifest(file_system, manifest_file, expected_artifact_manifest)

        self.assertIn(manifest_file, file_system.files)

        artifact_manifest = pickle.loads(file_system.files[manifest_file])

        self.assertEqual(artifact_manifest, expected_artifact_manifest)

    def test_read_artifact_manifest(self):
        expected_artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('7.5.2'),
            mode=Mode.debug,
            architecture=Architecture.x64,
            platform=Platform.linux,
            compiler=Compiler.gcc,
            exported_symbols=ExportedSymbols.explicit,
            artifact_type=ArtifactType.library,
            artifact_logging_level=ArtifactLoggingLevel.debug,
            dependencies=[
                ArtifactDependency(organization='org2',
                                   artifact='art2',
                                   version=DependencyVersion.from_string('1.2.4.SNAPSHOT'),
                                   scope=DependencyScope.main)
            ]
        )

        package_path = join('target', expected_artifact_manifest.get_package_file_name())

        file_system = FileSystemMock(
            files={
                package_path: ArchiveMock({
                    '.manifest': pickle.dumps(expected_artifact_manifest)
                })
            },
            directories={
                'target'
            }
        )

        artifact_manifest = read_artifact_manifest(file_system, package_path)

        self.assertEqual(artifact_manifest, expected_artifact_manifest)

    def test_read_invalid_manifest_file(self):
        package_path = join('target', 'org-art-x64-windows-msvc-release-2.13.9.tar.gz')

        file_system = FileSystemMock(
            files={
                package_path: ArchiveMock({
                    '.manifest': pickle.dumps("Not a manifest file!")
                })
            },
            directories={
                'target'
            }
        )

        self.assertRaises(InvalidManifestFileError, read_artifact_manifest, file_system, package_path)

    def test_split_package_version(self):
        identifier, version = split_package_version(
            'org-art-x64-windows-msvc-release-12.4.0.SNAPSHOT20210125115010123456.tar.gz')

        self.assertEqual(identifier, 'org-art-x64-windows-msvc-release')
        self.assertEqual(version, '12.4.0.SNAPSHOT20210125115010123456')

    def test_get_matching_packages(self):
        dependency = 'org-art-x64-linux-gcc-debug-12.+4.+0.SNAPSHOT.tar.gz'

        candidates = [
            'org-art-x64-linux-gcc-debug-12.4.0.tar.gz',
            'org-art-x64-linux-gcc-debug-12.4.0.SNAPSHOT20230120115015000006.tar.gz',
            'org-art-x64-linux-gcc-debug-12.4.1.SNAPSHOT20230120115015000003.tar.gz',
            'org-art-x64-linux-gcc-debug-12.4.1.tar.gz',
            'or2-ar2-x64-linux-gcc-debug-12.4.0.SNAPSHOT20230120115015000005.tar.gz',
            'or2-ar2-x64-linux-gcc-debug-12.4.0.tar.gz',
            'org-art-x64-linux-gcc-debug-12.5.0.SNAPSHOT20230120115015000001.tar.gz',
            'org-art-x64-linux-gcc-debug-12.5.0.SNAPSHOT20230120115015000002.tar.gz',
            'org-art-x64-linux-gcc-debug-12.5.0.tar.gz',
            'org-art-x64-linux-gcc-debug-13.5.0.tar.gz',
        ]

        expected_matching_packages = [
            'org-art-x64-linux-gcc-debug-12.5.0.tar.gz',
            'org-art-x64-linux-gcc-debug-12.5.0.SNAPSHOT20230120115015000002.tar.gz',
            'org-art-x64-linux-gcc-debug-12.5.0.SNAPSHOT20230120115015000001.tar.gz',
            'org-art-x64-linux-gcc-debug-12.4.1.tar.gz',
            'org-art-x64-linux-gcc-debug-12.4.1.SNAPSHOT20230120115015000003.tar.gz',
            'org-art-x64-linux-gcc-debug-12.4.0.tar.gz',
            'org-art-x64-linux-gcc-debug-12.4.0.SNAPSHOT20230120115015000006.tar.gz',
        ]

        matching_packages = get_matching_packages(dependency, candidates)

        self.assertEqual(matching_packages, expected_matching_packages)

    def test_get_packages_from_directory(self):
        file_system = FileSystemMock(
            files={
                join('packages', 'org-art-x64-linux-gcc-debug-12.4.0.SNAPSHOT20230120115015000006.tar.gz'): b'',
                join('packages', 'org-art-x64-linux-gcc-debug-12.4.0.tar.gz'): b'',
                join('packages', 'not-a-package.tar.gz'): b'',
            },
            directories={'packages'}
        )

        packages = get_packages_from_directory(file_system, 'packages')

        expected_packages = {
            'org-art-x64-linux-gcc-debug-12.4.0.SNAPSHOT20230120115015000006.tar.gz',
            'org-art-x64-linux-gcc-debug-12.4.0.tar.gz'
        }

        self.assertCountEqual(packages, expected_packages)

    def test_get_package_dependencies_from_archive(self):
        artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('7.5.2'),
            mode=Mode.debug,
            architecture=Architecture.x64,
            platform=Platform.linux,
            compiler=Compiler.gcc,
            exported_symbols=ExportedSymbols.explicit,
            artifact_type=ArtifactType.library,
            artifact_logging_level=ArtifactLoggingLevel.debug,
            dependencies=[
                ArtifactDependency(organization='org2',
                                   artifact='art2',
                                   version=DependencyVersion.from_string('1.2.4.SNAPSHOT'),
                                   scope=DependencyScope.main),
                ArtifactDependency(organization='org3',
                                   artifact='art3',
                                   version=DependencyVersion.from_string('5.0.9'),
                                   scope=DependencyScope.test)
            ]
        )

        package_path = join('packages', 'org-art-x64-linux-gcc-debug-7.5.2.tar.gz')

        file_system = FileSystemMock(
            directories={
                'packages'
            }, 
            files={
                package_path: ArchiveMock({'.manifest': pickle.dumps(artifact_manifest)})
            }
        )

        package_dependencies = get_package_dependencies_from_archive(file_system, package_path)

        expected_package_dependencies = {
            "org2-art2-x64-linux-gcc-debug-1.2.4.SNAPSHOT.tar.gz",
            "org3-art3-x64-linux-gcc-debug-5.0.9.tar.gz",
        }

        self.assertCountEqual(package_dependencies, expected_package_dependencies)
