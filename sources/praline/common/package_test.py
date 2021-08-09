import logging
from os.path import dirname, normpath
from praline.common.package import (clean_up_package, get_matching_packages, get_package,
                                    get_package_dependencies_from_archive,
                                    get_package_dependencies_from_pralinefile, get_package_dependencies_recursively,
                                    get_package_extracted_contents, get_package_metadata,
                                    get_packages_from_directory, get_version, get_wildcard,
                                    InvalidPackageContentsError, InvalidPackageNameError, pack, packages_match, 
                                    split_package, unpack)
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase
import pickle


class PackageTest(TestCase):
    def test_get_package(self):
        package = get_package('my_organization', 'my_artifact', 'x32', 'windows', 'msvc', 'debug', '1.0.0')

        self.assertEqual(package, 'my_organization-my_artifact-x32-windows-msvc-debug-1.0.0.tar.gz')

    def test_get_package_metadata(self):
        package = get_package_metadata('path/my_organization-my_artifact-x32-windows-msvc-debug-1.0.0.tar.gz')

        self.assertEqual(package['name'], 'my_organization-my_artifact-x32-windows-msvc-debug-1.0.0.tar.gz')
        self.assertEqual(package['organization'], 'my_organization')
        self.assertEqual(package['artifact'], 'my_artifact')
        self.assertEqual(package['architecture'], 'x32')
        self.assertEqual(package['platform'], 'windows')
        self.assertEqual(package['compiler'], 'msvc')
        self.assertEqual(package['mode'], 'debug')
        self.assertEqual(package['version'], (1, 0, 0))

    def test_get_package_metadata_invalid_name(self):
        package = 'my_organization-my_artifact34-x32-windows-msvc-debug-1.0.0.tar.gz'

        self.assertRaises(InvalidPackageNameError, get_package_metadata, package)

        metadata = get_package_metadata(package, none_on_error=True)

        self.assertIsNone(metadata)

    def test_get_package_dependencies_from_pralinefile(self):
        pralinefile = {
            'organization': 'my_org',
            'artifact': 'my_art',
            'version': '1.0.0',
            'dependencies': [
                {
                    'organization': 'other_org',
                    'artifact': 'other_art',
                    'version': '2.3.4'
                },
                {
                    'organization': 'another_org',
                    'artifact': 'another_art',
                    'version': '6.32.1',
                    'scope': 'test'
                }
            ]
        }
        architecture          = 'x32'
        platform              = 'windows'
        compiler              = 'msvc'
        mode                  = 'debug'
    
        dependencies = get_package_dependencies_from_pralinefile(pralinefile, architecture, platform, compiler, mode)

        expected_dependencies = ['other_org-other_art-x32-windows-msvc-debug-2.3.4.tar.gz', 'another_org-another_art-x32-windows-msvc-debug-6.32.1.tar.gz']

        self.assertEqual(dependencies, expected_dependencies)

    def test_pack(self):
        file_system = FileSystemMock({'path/to'}, {
            'a.txt': b'a-contents',
            'b.txt': b'b-contents',
            'c.txt': b'c-contents'
        })
        package_path  = 'path/to/package.tar.gz'
        package_files = [('a.txt', 'a.txt'), ('b.txt', 'other/b.txt')]
        cache         = {}

        pack(file_system, package_path, package_files, cache)

        expected_files = {
            'a.txt': b'a-contents',
            'b.txt': b'b-contents',
            'c.txt': b'c-contents',
            'path/to/package.tar.gz': pickle.dumps({'a.txt': b'a-contents', 'other/b.txt': b'b-contents'})
        }

        self.assertEqual(file_system.files, {normpath(p): d for p, d in expected_files.items()})

        self.assertEqual(file_system.directories, {normpath('path/to')})

        expected_cache = {
            'a.txt': 'b3bc691c7cf43c01885b2e0ee2cf34b2dc7e482d9074de78bf4950344aade4be',
            'b.txt': 'eb214d6536a9bbba4599c5bb566c609fc35e02a1d7c71cccfb5ebaa4575e2288'
        }

        self.assertEqual(cache, expected_cache)

    def test_unpack(self):
        archive = pickle.dumps({
            'resources/org/art/app.config': b'app-config',
            'headers/org/art/inc.hpp': b'inc-hpp',
            'libraries/org-art-x32-windows-msvc-debug-1.0.0.dll': b'library-dll',
            'libraries_interfaces/org-art-x32-windows-msvc-debug-1.0.0.lib': b'library-interface-lib',
            'symbols_tables/org-art-x32-windows-msvc-debug-1.0.0.pdb': b'symbols-tables-pdb',
            'executables/org-art-x32-windows-msvc-debug-1.0.0.exe': b'executable-exe'
        })
        package_path = 'org-art-x32-windows-msvc-debug-1.0.0.tar.gz'
        extraction_path = 'external'
        file_system = FileSystemMock({extraction_path}, {package_path: archive})
        
        contents = unpack(file_system, package_path, extraction_path)

        expected_contents = {
            'resources': ['external/resources/org/art/app.config'],
            'headers': ['external/headers/org/art/inc.hpp'],
            'libraries': ['external/libraries/org-art-x32-windows-msvc-debug-1.0.0.dll'],
            'libraries_interfaces': ['external/libraries_interfaces/org-art-x32-windows-msvc-debug-1.0.0.lib'],
            'symbols_tables': ['external/symbols_tables/org-art-x32-windows-msvc-debug-1.0.0.pdb'],
            'executables': ['external/executables/org-art-x32-windows-msvc-debug-1.0.0.exe']
        }

        self.assertEqual({root: [normpath(p) for p in files] for root, files in contents.items()},
                         {root: [normpath(p) for p in files] for root, files in expected_contents.items()})

        expected_files = {
            'org-art-x32-windows-msvc-debug-1.0.0.tar.gz': archive,
            'external/resources/org/art/app.config': b'app-config',
            'external/headers/org/art/inc.hpp': b'inc-hpp',
            'external/libraries/org-art-x32-windows-msvc-debug-1.0.0.dll': b'library-dll',
            'external/libraries_interfaces/org-art-x32-windows-msvc-debug-1.0.0.lib': b'library-interface-lib',
            'external/symbols_tables/org-art-x32-windows-msvc-debug-1.0.0.pdb': b'symbols-tables-pdb',
            'external/executables/org-art-x32-windows-msvc-debug-1.0.0.exe': b'executable-exe'
        }

        self.assertEqual(file_system.files, {normpath(p): d for p, d in expected_files.items()})

        expected_directories = {
            'external/resources/org/art',
            'external/headers/org/art',
            'external/libraries',
            'external/libraries_interfaces',
            'external/symbols_tables',
            'external/executables'
        }

        self.assertEqual(file_system.directories, {normpath(p) for p in expected_directories})

    def test_clean_up_package(self):
        archive = pickle.dumps({
            'resources/org/art/app.config': b'app-config',
            'headers/org/art/inc.hpp': b'inc-hpp',
            'libraries/org-art-x32-windows-msvc-debug-1.0.0.dll': b'library-dll',
            'libraries_interfaces/org-art-x32-windows-msvc-debug-1.0.0.lib': b'library-interface-lib',
            'symbols_tables/org-art-x32-windows-msvc-debug-1.0.0.pdb': b'symbols-tables-pdb',
            'executables/org-art-x32-windows-msvc-debug-1.0.0.exe': b'executable-exe'
        })
        package_path = 'org-art-x32-windows-msvc-debug-1.0.0.tar.gz'
        file_system = FileSystemMock({
            'external/resources/org/other_art',
            'external/resources/org/art',
            'external/headers/org/art',
            'external/libraries',
            'external/libraries_interfaces',
            'external/symbols_tables',
            'external/executables'
        }, {
            package_path: archive,
            'external/resources/org/other_art/app.config': b'app-config',
            'external/resources/org/art/app.config': b'app-config',
            'external/headers/org/art/inc.hpp': b'inc-hpp',
            'external/libraries/org-art-x32-windows-msvc-debug-1.0.0.dll': b'library-dll',
            'external/libraries_interfaces/org-art-x32-windows-msvc-debug-1.0.0.lib': b'library-interface-lib',
            'external/symbols_tables/org-art-x32-windows-msvc-debug-1.0.0.pdb': b'symbols-tables-pdb',
            'external/executables/org-art-x32-windows-msvc-debug-1.0.0.exe': b'executable-exe'
        })
        extraction_path = 'external'

        logging_level = 4

        clean_up_package(file_system, package_path, extraction_path, logging_level)

        expected_files = {
            'external/resources/org/other_art/app.config': b'app-config'
        }

        self.assertEqual(file_system.files, {normpath(p): d for p, d in expected_files.items()})

        expected_directories = {
            'external/resources/org/other_art',
            'external/headers/org',
            'external/libraries',
            'external/libraries_interfaces',
            'external/symbols_tables',
            'external/executables'
        }

        self.assertEqual(file_system.directories, {normpath(p) for p in expected_directories})

    def test_get_package_extracted_contents(self):
        package_path    = 'workspace/juice/target/external/packages/org-art-x32-windows-msvc-debug-1.0.0.tar.gz'
        extraction_path = 'workspace/juice/target/external'
        archive = pickle.dumps({
            'resources/org/art/app.config': b'app-config',
            'headers/org/art/inc.hpp': b'inc-hpp',
            'libraries/org-art-x32-windows-msvc-debug-1.0.0.dll': b'library-dll',
            'libraries_interfaces/org-art-x32-windows-msvc-debug-1.0.0.lib': b'library-interface-lib',
            'symbols_tables/org-art-x32-windows-msvc-debug-1.0.0.pdb': b'symbols-tables-pdb',
            'executables/org-art-x32-windows-msvc-debug-1.0.0.exe': b'executable-exe'
        })
        file_system = FileSystemMock({dirname(package_path)}, {package_path: archive})

        contents = get_package_extracted_contents(file_system, package_path, extraction_path)

        expected_contents = {
            'resources': ['workspace/juice/target/external/resources/org/art/app.config'],
            'headers': ['workspace/juice/target/external/headers/org/art/inc.hpp'],
            'libraries': ['workspace/juice/target/external/libraries/org-art-x32-windows-msvc-debug-1.0.0.dll'],
            'libraries_interfaces': ['workspace/juice/target/external/libraries_interfaces/org-art-x32-windows-msvc-debug-1.0.0.lib'],
            'symbols_tables': ['workspace/juice/target/external/symbols_tables/org-art-x32-windows-msvc-debug-1.0.0.pdb'],
            'executables': ['workspace/juice/target/external/executables/org-art-x32-windows-msvc-debug-1.0.0.exe']
        }

        self.assertEqual({root: [normpath(p) for p in files] for root, files in contents.items()},
                         {root: [normpath(p) for p in files] for root, files in expected_contents.items()})

    def test_split_package(self):
        package = 'other_org-other_art-x64-linux-gcc-release-5.2.2.tar.gz'

        identifier, version = split_package(package)

        self.assertEqual(identifier, 'other_org-other_art-x64-linux-gcc-release')

        self.assertEqual(version, '5.2.2')

    def test_get_version(self):
        self.assertEqual(get_version('234.1.120'), (234, 1, 120))

        self.assertEqual(get_version('2.+4.+5'), (2, 4, 5))

        self.assertEqual(get_version('1.5.+2'), (1, 5, 2))

    def test_get_wildcard(self):
        self.assertEqual(get_wildcard('5.0.0'), (False, False, False))

        self.assertEqual(get_wildcard('7.+6.+3'), (False, True, True))

        self.assertEqual(get_wildcard('8.4.+0'), (False, False, True))

    def test_packages_match(self):
        self.assertTrue(packages_match('org-art-x32-windows-msvc-debug-1.0.0.tar.gz',
                                       'org-art-x32-windows-msvc-debug-1.0.0.tar.gz'))

        self.assertTrue(packages_match('org-art-x32-windows-msvc-debug-1.22.5.tar.gz',
                                       'org-art-x32-windows-msvc-debug-1.+0.+0.tar.gz'))

        self.assertTrue(packages_match('org-art-x32-windows-msvc-debug-1.0.12.tar.gz',
                                       'org-art-x32-windows-msvc-debug-1.0.+0.tar.gz'))

        self.assertFalse(packages_match('org-art-x32-windows-msvc-debug-2.0.0.tar.gz',
                                        'org-art-x32-windows-msvc-debug-1.+0.+0.tar.gz'))

        self.assertFalse(packages_match('org-art-x32-windows-msvc-debug-1.2.0.tar.gz',
                                        'org-art-x32-windows-msvc-debug-1.0.+0.tar.gz'))

        self.assertFalse(packages_match('other_art-art-x32-windows-msvc-debug-1.0.0.tar.gz',
                                        'org-art-x32-windows-msvc-debug-1.0.0.tar.gz'))

        self.assertFalse(packages_match('org-art-x32-windows-msvc-release-1.22.5.tar.gz',
                                        'org-art-x32-windows-msvc-debug-1.+0.+0.tar.gz'))

    def test_get_packages_from_directory(self):
        directory   = 'packages'
        file_system = FileSystemMock({directory}, {
            f'{directory}/org-art-x32-windows-msvc-debug-1.0.0.tar.gz': b'',
            f'{directory}/other_org-other_art-x64-linux-gcc-release-5.2.2.tar.gz': b'',
            f'{directory}/some_other_file.txt': b'',
            'another_org-another_art-x32-darwin-clang-debug-2.1.0.tar.gz': b''
        })

        packages = get_packages_from_directory(file_system, directory)

        expected_packages = [
            'org-art-x32-windows-msvc-debug-1.0.0.tar.gz',
            'other_org-other_art-x64-linux-gcc-release-5.2.2.tar.gz'
        ]

        self.assertEqual(packages, expected_packages)

    def test_get_package_dependencies_from_archive(self):
        archive = pickle.dumps({
            'Pralinefile': b"""\
            organization: my_org
            artifact: my_art
            version: 1.0.0
            dependencies:
            - organization: some_org
              artifact: some_art
              version: 7.0.1
            - organization: test_org
              artifact: test_art
              version: 2.2.2
              scope: test
            - organization: another_org
              artifact: another_art
              version: 1.2.3
            """
        })
        directory    = 'packages'
        package_path = f'{directory}/my_org-my_art-x32-windows-msvc-debug-1.0.0.tar.gz'
        file_system  = FileSystemMock({directory}, {package_path: archive})
        scope        = 'main'

        dependencies = get_package_dependencies_from_archive(file_system, package_path, scope)

        expected_dependencies = [
            'some_org-some_art-x32-windows-msvc-debug-7.0.1.tar.gz',
            'another_org-another_art-x32-windows-msvc-debug-1.2.3.tar.gz'
        ]

        self.assertEqual(dependencies, expected_dependencies)

    def test_get_matching_packages(self):
        package = 'org-art-x32-windows-msvc-debug-1.+1.+0.tar.gz'

        candidates = [
            'org-art-x32-windows-msvc-debug-1.0.1.tar.gz',
            'some_org-some_art-x32-windows-msvc-debug-7.0.1.tar.gz',
            'org-art-x32-windows-msvc-debug-1.1.4.tar.gz',
            'org-art-x32-windows-msvc-debug-1.2.4.tar.gz',
            'another_org-another_art-x32-windows-msvc-debug-1.2.3.tar.gz',
            'org-art-x32-windows-msvc-debug-1.2.5.tar.gz'
        ]
        
        packages = get_matching_packages(package, candidates)

        expected_packages = [
            'org-art-x32-windows-msvc-debug-1.2.5.tar.gz',
            'org-art-x32-windows-msvc-debug-1.2.4.tar.gz',
            'org-art-x32-windows-msvc-debug-1.1.4.tar.gz'
        ]

        self.assertEqual(packages, expected_packages)

    def test_get_package_dependencies_recursively(self):
        chocolate_archive = pickle.dumps({
            'Pralinefile': b"""\
            organization: candyorg
            artifact: chocolate
            version: 1.0.0
            dependencies:
            - organization: candyorg
              artifact: popsicle
              version: 1.+0.+0
            - organization: testorg
              artifact: testing
              version: 2.5.0
              scope: test
            """
        })

        chocolate_package = 'candyorg-chocolate-x32-windows-msvc-debug-1.0.0.tar.gz'

        chocolate_dependencies = [
            'candyorg-popsicle-x32-windows-msvc-debug-1.+0.+0.tar.gz',
            'testorg-testing-x32-windows-msvc-debug-2.5.0.tar.gz'
        ]

        popsicle_1_0_0_archive = pickle.dumps({
            'Pralinefile': b"""\
            organization: candyorg
            artifact: popsicle
            version: 1.0.0
            """
        })

        popsicle_1_1_0_archive = pickle.dumps({
            'Pralinefile': b"""\
            organization: candyorg
            artifact: popsicle
            version: 1.1.0
            dependencies:
            - organization: candyorg
              artifact: icecream
              version: 1.0.0
            - organization: testorg
              artifact: testing
              version: 2.4.0
              scope: test
            """
        })

        icecream_archive = pickle.dumps({
            'Pralinefile': b"""\
            organization: candyorg
            artifact: popsicle
            version: 1.0.0
            dependencies:
            - organization: testorg
              artifact: testing
              version: 2.4.0
              scope: test
            """
        })

        testing_2_5_0_archive = pickle.dumps({
            'Pralinefile': b"""\
            organization: testorg
            artifact: testing
            version: 2.5.0
            """
        })

        testing_2_4_0_archive = pickle.dumps({
            'Pralinefile': b"""\
            organization: testorg
            artifact: testing
            version: 2.4.0
            """
        })

        repository    = 'packages'
        file_system  = FileSystemMock({repository}, {
            f'{repository}/candyorg-chocolate-x32-windows-msvc-debug-1.0.0.tar.gz': chocolate_archive,
            f'{repository}/candyorg-popsicle-x32-windows-msvc-debug-1.0.0.tar.gz': popsicle_1_0_0_archive,
            f'{repository}/candyorg-popsicle-x32-windows-msvc-debug-1.1.0.tar.gz': popsicle_1_1_0_archive,
            f'{repository}/candyorg-icecream-x32-windows-msvc-debug-1.0.0.tar.gz': icecream_archive,
            f'{repository}/testorg-testing-x32-windows-msvc-debug-2.5.0.tar.gz': testing_2_5_0_archive,
            f'{repository}/testorg-testing-x32-windows-msvc-debug-2.4.0.tar.gz': testing_2_4_0_archive
        })

        dependencies = get_package_dependencies_recursively(file_system, chocolate_package, chocolate_dependencies, repository)

        expected_dependencies = {
            'candyorg-popsicle-x32-windows-msvc-debug-1.1.0.tar.gz',
            'candyorg-icecream-x32-windows-msvc-debug-1.0.0.tar.gz',
            'testorg-testing-x32-windows-msvc-debug-2.5.0.tar.gz'
        }

        self.assertEqual(set(dependencies), expected_dependencies)
