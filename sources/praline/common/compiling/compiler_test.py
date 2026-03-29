from praline.common import (Architecture, ArtifactManifest, ArtifactPrefix, ArtifactType, ArtifactVersion,
                            CompilerType, ExportedSymbols, Mode, Platform)
from praline.common.compiling.compiler import ICompilingStrategy, IYieldDescriptor, Compiler
from praline.common.file_system import join
from praline.common.project_structure import ProjectStructure
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from typing import List
from unittest import TestCase


class YieldDescriptorMock(IYieldDescriptor):
    def get_object(self, source_relative_path: str) -> str:
        return super().get_object(source_relative_path) + '.obj'

    def get_executable_and_symbols_table(self, artifact_identifier: str) -> str:
        return artifact_identifier + '.exe', artifact_identifier + '.exe.pdb'

    def get_library_and_symbols_table(self, artifact_identifier: str) -> str:
        return artifact_identifier + '.dll', artifact_identifier + '.dll.pdb'

    def get_library_interface(self, artifact_identifier: str) -> str:
        return artifact_identifier + '.lib'

    def get_executable_prefix(self, artifact_prefix: ArtifactPrefix) -> ArtifactPrefix:
        return artifact_prefix

    def get_library_prefix(self, artifact_prefix: ArtifactPrefix) -> ArtifactPrefix:
        return artifact_prefix


class CompilingStrategyMock(ICompilingStrategy):
    def __init__(self, file_system):
        self.file_system = file_system

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return YieldDescriptorMock()

    def preprocess(self, headers: List[str], source_path: str, main_source: bool) -> bytes:
        headers = [h for h in headers if source_path[:-4] == h[:-4]]
        if headers:
            with self.file_system.open_file(headers[0], 'rb') as h:
                with self.file_system.open_file(source_path, 'rb') as s:
                    return h.read() + s.read()
        else:
            with self.file_system.open_file(source_path, 'rb') as s:
                return s.read()

    def compile(self, headers: List[str], source_path: str, object_path: str, main_source: bool) -> None:
        data = self.preprocess(headers, source_path, main_source)
        with self.file_system.open_file(object_path, 'wb') as o:
            o.write(data)

    def link_executable(self,
                        objects: List[str],
                        external_libraries: List[str],
                        external_libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str) -> None:
        data = b''
        for file_name in objects + external_libraries + external_libraries_interfaces:
            with self.file_system.open_file(file_name, 'rb') as o:
                data += o.read()
        with self.file_system.open_file(executable, 'wb') as e:
            e.write(data + b'exe')
        with self.file_system.open_file(symbols_table, 'wb') as s:
            s.write(data + b'pbd')

    def link_library(self,
                     objects: List[str],
                     external_libraries: List[str],
                     external_libraries_interfaces: List[str],
                     library: str,
                     library_interface: str,
                     symbols_table: str) -> None:
        data = b''
        for file_name in objects + external_libraries + external_libraries_interfaces:
            with self.file_system.open_file(file_name, 'rb') as o:
                data += o.read()
        with self.file_system.open_file(library, 'wb') as l:
            l.write(data + b'dll')
        with self.file_system.open_file(library_interface, 'wb') as li:
            li.write(data + b'lib')
        with self.file_system.open_file(symbols_table, 'wb') as s:
            s.write(data + b'pbd')


class CompilerTest(TestCase):
    def setUp(self):
        self.artifact_manifest = ArtifactManifest(
            organization='org',
            artifact='art',
            version=ArtifactVersion.from_string('1.0.0'),
            mode=Mode.debug,
            architecture=Architecture.x32,
            platform=Platform.windows,
            compiler=CompilerType.msvc,
            exported_symbols=ExportedSymbols.explicit,
            artifact_type=ArtifactType.library,
            main_service=None,
            test_service=None,
            dependencies=[]
        )

        self.artifact_identifier = self.artifact_manifest.get_artifact_identifier()

        self.project_structure = ProjectStructure('project', self.artifact_manifest.organization, self.artifact_manifest.artifact)

        self.main_source_path = lambda source: join(self.project_structure.main_sources_domain_root, source)

        self.test_source_path = lambda source: join(self.project_structure.test_sources_domain_root, source)
        
        self.main_object_path = lambda object: join(self.project_structure.main_objects_root, object)

        self.test_object_path = lambda object: join(self.project_structure.test_objects_root, object)
        
        self.library_path = join(self.project_structure.libraries_root, self.artifact_identifier + '.dll')

        self.interface_path = join(self.project_structure.libraries_interfaces_root, self.artifact_identifier + '.lib')
        
        self.external_library_path = lambda external_library: join(self.project_structure.external_libraries_root, external_library)

        self.external_interface_path = lambda external_interface: join(self.project_structure.external_libraries_interfaces_root, external_interface)

    def test_compile_main_sources_using_cache(self):
        file_system = FileSystemMock(
            directories={
                self.project_structure.main_sources_domain_root,
                self.project_structure.main_objects_root,
            }, 
            files={
                self.main_source_path('a.hpp'): b'header-a.',
                self.main_source_path('a.cpp'): b'source-a.',
                self.main_source_path('b.hpp'): b'updated-header-b.',
                self.main_source_path('b.cpp'): b'source-b.',
                self.main_source_path('d.hpp'): b'header-d.',
                self.main_source_path('d.cpp'): b'source-d.',
                self.main_source_path('e.cpp'): b'source-e.',

                self.main_object_path('org-art-a.obj'): b'header-a.source-a.',
                self.main_object_path('org-art-b.obj'): b'header-b.source-b.',
                self.main_object_path('org-art-c.obj'): b'header-c.source-c.',
            }
        )

        compiler = Compiler(file_system, self.project_structure, self.artifact_manifest, CompilingStrategyMock(file_system))

        headers = [
            self.main_source_path('a.hpp'), 
            self.main_source_path('b.hpp'),  
            self.main_source_path('d.hpp'),
        ]

        sources = [
            self.main_source_path('a.cpp'), 
            self.main_source_path('b.cpp'), 
            self.main_source_path('d.cpp'), 
            self.main_source_path('e.cpp'),
        ]
        
        cache = {
            self.main_source_path('a.cpp'): '8ceb2730683fdf075d4ede855d5ed98f32be31b093f74b0bee13fd5dea9037dc',
            self.main_source_path('b.cpp'): '5addc12d3b54fb9836277adccb06a03131ab92c10faf97613259bb77775db8d3',
            self.main_source_path('c.cpp'): '853b9c27fdbe775b24a8fb14f7ef43aba1d6e698df4f2df6bc4e0f22c800f1d5',
            self.main_source_path('e.cpp'): '7e0494e082ebf4d0b3b06d2433a4c59e3a610ea10e5e3747e5d4d68fd734e485',
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=5)

        objects = compiler.compile_sources_using_cache(headers, sources, cache, progress_bar_supplier, main_sources=True)

        expected_objects = {
            self.main_object_path('org-art-a.obj'), 
            self.main_object_path('org-art-b.obj'), 
            self.main_object_path('org-art-d.obj'), 
            self.main_object_path('org-art-e.obj'),
        }

        self.assertEqual(set(objects), expected_objects)

        expected_files = {
            self.main_source_path('a.hpp'): b'header-a.',
            self.main_source_path('a.cpp'): b'source-a.',
            self.main_source_path('b.hpp'): b'updated-header-b.',
            self.main_source_path('b.cpp'): b'source-b.',
            self.main_source_path('d.hpp'): b'header-d.',
            self.main_source_path('d.cpp'): b'source-d.',
            self.main_source_path('e.cpp'): b'source-e.',

            self.main_object_path('org-art-a.obj'): b'header-a.source-a.',
            self.main_object_path('org-art-b.obj'): b'updated-header-b.source-b.',
            self.main_object_path('org-art-d.obj'): b'header-d.source-d.',
            self.main_object_path('org-art-e.obj'): b'source-e.',
        }

        self.assertEqual(file_system.files, expected_files)

        expected_cache = {
            self.main_source_path('a.cpp'): '8ceb2730683fdf075d4ede855d5ed98f32be31b093f74b0bee13fd5dea9037dc',
            self.main_source_path('b.cpp'): 'db4b8fea71a29aedd0eac30601ac3489bdc72a3261697215901cf04da2d6a931',
            self.main_source_path('d.cpp'): 'edf58f60231d34dfe3eb468e1b4cfeb35dd39cecd796183660cf13bf301f103b',
            self.main_source_path('e.cpp'): '7e0494e082ebf4d0b3b06d2433a4c59e3a610ea10e5e3747e5d4d68fd734e485',
        }

        self.assertEqual(cache, expected_cache)

    def test_compile_test_sources_using_cache(self):
        file_system = FileSystemMock(
            directories={
                self.project_structure.main_sources_domain_root,
                self.project_structure.test_sources_domain_root,
                self.project_structure.main_objects_root,
                self.project_structure.test_objects_root,
            }, 
            files={
                self.test_source_path('a.test.hpp'): b'test-header-a.',
                self.test_source_path('a.test.cpp'): b'test-source-a.',

                self.test_source_path('b.test.hpp'): b'test-header-b.',
                self.test_source_path('b.test.cpp'): b'test-source-b.',

                self.test_source_path('d.test.hpp'): b'test-header-d.',
                self.test_source_path('d.test.cpp'): b'updated-test-source-d.',

                self.test_object_path('org-art-a.test.obj'): b'test-header-a.test-source-a.',
                self.test_object_path('org-art-c.test.obj'): b'test-header-c.test-source-c.',
                self.test_object_path('org-art-d.test.obj'): b'test-header-d.test-source-d.',
            }
        )

        compiler = Compiler(file_system, self.project_structure, self.artifact_manifest, CompilingStrategyMock(file_system))

        headers = [
            self.test_source_path('a.test.hpp'),
            self.test_source_path('b.test.hpp'), 
            self.test_source_path('d.test.hpp'), 
        ]

        sources = [
            self.test_source_path('a.test.cpp'),
            self.test_source_path('b.test.cpp'), 
            self.test_source_path('d.test.cpp'), 
        ]
        
        cache = {
            self.test_source_path('a.test.cpp'): '0c1efc8157c0e24570c3ceb9d41c113d09a092166fc2eb7b880d0c460c10901c',
            self.test_source_path('c.test.cpp'): '2ba2d0cb264e0ba449d93e7ffc17ad39fac70e376e848f6aa6b95ef902bb3eb7',
            self.test_source_path('d.test.cpp'): '6ca9143a1a5626063fbf57b6df23ae1959339bb2f4b87c34e6d80094625f6fc5',
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=4)

        objects = compiler.compile_sources_using_cache(headers, sources, cache, progress_bar_supplier, main_sources=False)

        expected_objects = {
            self.test_object_path('org-art-a.test.obj'), 
            self.test_object_path('org-art-b.test.obj'), 
            self.test_object_path('org-art-d.test.obj'), 
        }

        self.assertEqual(set(objects), expected_objects)

        expected_files = {
            self.test_source_path('a.test.hpp'): b'test-header-a.',
            self.test_source_path('a.test.cpp'): b'test-source-a.',

            self.test_source_path('b.test.hpp'): b'test-header-b.',
            self.test_source_path('b.test.cpp'): b'test-source-b.',

            self.test_source_path('d.test.hpp'): b'test-header-d.',
            self.test_source_path('d.test.cpp'): b'updated-test-source-d.',

            self.test_object_path('org-art-a.test.obj'): b'test-header-a.test-source-a.',
            self.test_object_path('org-art-b.test.obj'): b'test-header-b.test-source-b.',
            self.test_object_path('org-art-d.test.obj'): b'test-header-d.updated-test-source-d.',
        }

        self.assertEqual(file_system.files, expected_files)

        expected_cache = {
            self.test_source_path('a.test.cpp'): '0c1efc8157c0e24570c3ceb9d41c113d09a092166fc2eb7b880d0c460c10901c',
            self.test_source_path('b.test.cpp'): '0143a5127a26f8c4f3d6f22ebc665ba23a13dd6d0f181a7c2b0b1b58b0260702',
            self.test_source_path('d.test.cpp'): '032009fce12df09aabd3b1b6bb656c0892e4cddcb27dc8ad67e71f77d382a52f',
        }

        self.assertEqual(cache, expected_cache)

    def test_link_main_executable_using_cache(self):
        main_a      = self.main_object_path('org-art-a.obj')
        library_b   = self.external_library_path('b.dll')
        interface_b = self.external_interface_path('b.lib')

        file_system = FileSystemMock(
            directories={
                self.project_structure.main_objects_root,
                self.project_structure.executables_root,
                self.project_structure.symbols_tables_root,
                self.project_structure.external_libraries_root,
                self.project_structure.external_libraries_interfaces_root
            },
            files={
                main_a: b'object-a.',
                library_b:   b'external-library-b.',
                interface_b: b'external-library-interface-b.',
            }
        )

        compiler = Compiler(file_system, self.project_structure, self.artifact_manifest, CompilingStrategyMock(file_system))

        objects                       = [self.main_object_path('org-art-a.obj')]
        external_libraries            = [self.external_library_path('b.dll')]
        external_libraries_interfaces = [self.external_interface_path('b.lib')]

        cache = {}

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=1)

        executable, symbols_table = compiler.link_executable_using_cache(objects, 
                                                                         external_libraries,
                                                                         external_libraries_interfaces,
                                                                         cache,
                                                                         progress_bar_supplier,
                                                                         main_executable=True)
        
        expected_executable_path = join(self.project_structure.executables_root, self.artifact_identifier + '.exe')

        expected_symbols_path = join(self.project_structure.symbols_tables_root, self.artifact_identifier + '.exe.pdb')

        self.assertEqual(executable, expected_executable_path)

        self.assertEqual(symbols_table, expected_symbols_path)

        expected_files = {
            main_a:          b'object-a.',
            library_b:       b'external-library-b.',
            interface_b:     b'external-library-interface-b.',
            expected_executable_path: b'object-a.external-library-b.external-library-interface-b.exe',
            expected_symbols_path: b'object-a.external-library-b.external-library-interface-b.pbd'
        }

        self.assertEqual(file_system.files, expected_files)

        expected_cache = {}

        self.assertEqual(cache, expected_cache)

    def test_link_test_executable_using_cache(self):
        main_a = self.main_object_path('org-art-a.obj')
        test_a = self.test_object_path('org-art-a.test.obj')
        
        library_b   = self.external_library_path('b.dll')
        interface_b = self.external_interface_path('b.lib')

        file_system = FileSystemMock(
            directories={
                self.project_structure.main_objects_root,
                self.project_structure.test_objects_root,
                self.project_structure.executables_root,
                self.project_structure.symbols_tables_root,
                self.project_structure.external_libraries_root,
                self.project_structure.external_libraries_interfaces_root
            },
            files={
                main_a: b'object-a.',
                test_a: b'object-a-test.',
                library_b:   b'external-library-b.',
                interface_b: b'external-library-interface-b.',
            }
        )

        compiler = Compiler(file_system, self.project_structure, self.artifact_manifest, CompilingStrategyMock(file_system))

        objects                       = [main_a, test_a]
        external_libraries            = [library_b]
        external_libraries_interfaces = [interface_b]

        cache = {}

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=1)

        executable, symbols_table = compiler.link_executable_using_cache(objects, 
                                                                         external_libraries,
                                                                         external_libraries_interfaces,
                                                                         cache,
                                                                         progress_bar_supplier,
                                                                         main_executable=False)

        expected_executable_path = join(self.project_structure.executables_root, self.artifact_identifier + '.test.exe')

        expected_symbols_path = join(self.project_structure.symbols_tables_root, self.artifact_identifier + '.test.exe.pdb')

        self.assertEqual(executable, expected_executable_path)

        self.assertEqual(symbols_table, expected_symbols_path)

        expected_files = {
            main_a:          b'object-a.',
            test_a:          b'object-a-test.',
            library_b:       b'external-library-b.',
            interface_b:     b'external-library-interface-b.',
            expected_executable_path: b'object-a.object-a-test.external-library-b.external-library-interface-b.exe',
            expected_symbols_path: b'object-a.object-a-test.external-library-b.external-library-interface-b.pbd'
        }

        self.assertEqual(file_system.files, expected_files)

        expected_cache = {}

        self.assertEqual(cache, expected_cache)

    def test_link_library_using_cache(self):
        file_system = FileSystemMock(
            directories={
                self.project_structure.main_objects_root,
                self.project_structure.libraries_root,
                self.project_structure.libraries_interfaces_root,
                self.project_structure.symbols_tables_root,
                self.project_structure.external_libraries_root,
                self.project_structure.external_libraries_interfaces_root
            },
            files={
                self.main_object_path('org-art-a.obj'): b'object-a.',
                self.external_library_path('b.dll'):    b'external-library-b.',
                self.external_interface_path('c.lib'):  b'external-library-interface-c.'
            }
        )

        compiler = Compiler(file_system, self.project_structure, self.artifact_manifest, CompilingStrategyMock(file_system))

        objects                       = [self.main_object_path('org-art-a.obj')]
        external_libraries            = [self.external_library_path('b.dll')]
        external_libraries_interfaces = [self.external_interface_path('c.lib')]

        cache = {}

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=1)

        library, library_interface, symbols_table = compiler.link_library_using_cache(objects,
                                                                                      external_libraries,
                                                                                      external_libraries_interfaces,
                                                                                      cache,
                                                                                      progress_bar_supplier)
        
        self.assertEqual(library, self.library_path)

        self.assertEqual(library_interface, self.interface_path)

        expected_symbols_path = join(self.project_structure.symbols_tables_root, self.artifact_identifier + '.dll.pdb')

        self.assertEqual(symbols_table, expected_symbols_path)

        expected_files = {
            self.main_object_path('org-art-a.obj'): b'object-a.',
            self.external_library_path('b.dll'):    b'external-library-b.',
            self.external_interface_path('c.lib'):  b'external-library-interface-c.',
            self.library_path:   b'object-a.external-library-b.external-library-interface-c.dll',
            self.interface_path: b'object-a.external-library-b.external-library-interface-c.lib',
            expected_symbols_path: b'object-a.external-library-b.external-library-interface-c.pbd',
        }

        self.assertEqual(file_system.files, expected_files)

        expected_cache = {}

        self.assertEqual(cache, expected_cache)
