from os.path import normpath
from praline.common import ProjectStructure
from praline.common.compiling.compiler import (
    ICompiler, compile_using_cache, link_executable_using_cache, link_library_using_cache, YieldDescriptor,
)
from praline.common.file_system import join
from praline.common.testing.file_system_mock import FileSystemMock
from praline.common.testing.progress_bar_mock import ProgressBarSupplierMock

from typing import List
from unittest import TestCase


class YieldDescriptorMock(YieldDescriptor):
    def get_object(self, sources_root: str, objects_root: str, source: str) -> str:
        return super().get_object(sources_root, objects_root, source) + '.obj'

    def get_executable(self, executables_root: str, name: str) -> str:
        return join(executables_root, f'{name}.exe')

    def get_library(self, libraries_root: str, name: str) -> str:
        return join(libraries_root, f'{name}.dll')

    def get_library_interface(self, library_interfaces_root: str, name: str) -> str:
        return join(library_interfaces_root, f'{name}.lib')

    def get_symbols_table(self, symbols_tables_root: str, name: str) -> str:
        return join(symbols_tables_root, f'{name}.pdb')


class CompilerMock(ICompiler):
    def __init__(self, file_system):
        self.file_system = file_system

    def get_yield_descriptor(self) -> YieldDescriptor:
        return YieldDescriptorMock()

    def preprocess(self,
                   headers_root: str,
                   external_headers_root: str,
                   headers: List[str],
                   source: str) -> bytes:
        header = [h for h in headers if source[:-4] == h[:-4]][0]
        with self.file_system.open_file(header, 'rb') as h:
            with self.file_system.open_file(source, 'rb') as s:
                return h.read() + s.read()

    def compile(self,
                headers_root: str,
                external_headers_root: str,
                headers: List[str],
                source: str,
                object_: str) -> None:
        data = self.preprocess(headers_root, external_headers_root, headers, source)
        with self.file_system.open_file(object_, 'wb') as o:
            o.write(data)

    def link_executable(self,
                        external_libraries_root: str,
                        external_libraries_interfaces_root: str,
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
                     external_libraries_root: str,
                     external_libraries_interfaces_root: str,
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
        self.artifact_identifier = 'org-art-x32-windows-compmock-debug-1.0.0'

        self.project_structure = ProjectStructure(
            project_directory='project',
            resources_root='resources',
            sources_root='sources',
            target_root='target',
            objects_root='target/objects',
            executables_root='target/executables',
            libraries_root='target/libraries',
            libraries_interfaces_root='target/libraries_interfaces',
            symbols_tables_root='target/symbols_tables',
            external_root='target/external',
            external_packages_root='target/external/packages',
            external_headers_root='target/external/headers',
            external_executables_root='target/external/executables',
            external_libraries_root='target/external/libraries',
            external_libraries_interfaces_root='target/external/libraries_interfaces',
            external_symbols_tables_root='target/external/symbols_tables'
        )

    def test_compilation_using_cache(self):
        file_system = FileSystemMock(
            directories={
                self.project_structure.objects_root,
                self.project_structure.sources_root,
                self.project_structure.external_headers_root
            }, 
            files={
                'sources/a.hpp': b'header-a.',
                'sources/a.cpp': b'source-a.',
                'sources/b.hpp': b'updated-header-b.',
                'sources/b.cpp': b'source-b.',
                'sources/d.hpp': b'header-d.',
                'sources/d.cpp': b'source-d.',
                'target/objects/a.obj': b'header-a.source-a.',
                'target/objects/b.obj': b'header-b.source-b.',
                'target/objects/c.obj': b'header-c.source-c.'
            }
        )

        compiler = CompilerMock(file_system)
        headers  = ['sources/a.hpp', 'sources/b.hpp', 'sources/d.hpp']
        sources  = ['sources/a.cpp', 'sources/b.cpp', 'sources/d.cpp']
        cache    = {
            'sources/a.cpp': '8ceb2730683fdf075d4ede855d5ed98f32be31b093f74b0bee13fd5dea9037dc',
            'sources/b.cpp': '5addc12d3b54fb9836277adccb06a03131ab92c10faf97613259bb77775db8d3',
            'sources/c.cpp': '853b9c27fdbe775b24a8fb14f7ef43aba1d6e698df4f2df6bc4e0f22c800f1d5'
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=4)

        objects = compile_using_cache(file_system,
                                      self.project_structure,
                                      compiler,
                                      headers,
                                      sources,
                                      cache,
                                      progress_bar_supplier)

        expected_objects = {'target/objects/a.obj', 'target/objects/b.obj', 'target/objects/d.obj'}

        self.assertEqual({normpath(o) for o in objects}, {normpath(o) for o in expected_objects})

        new_files = {
            'sources/a.hpp': b'header-a.',
            'sources/a.cpp': b'source-a.',
            'sources/b.hpp': b'updated-header-b.',
            'sources/b.cpp': b'source-b.',
            'sources/d.hpp': b'header-d.',
            'sources/d.cpp': b'source-d.',
            'target/objects/a.obj': b'header-a.source-a.',
            'target/objects/b.obj': b'updated-header-b.source-b.',
            'target/objects/d.obj': b'header-d.source-d.'
        }

        expected_files = {normpath(p): data for p, data in new_files.items()}

        self.assertEqual(file_system.files, expected_files)

        expected_cache = {
            'sources/a.cpp': '8ceb2730683fdf075d4ede855d5ed98f32be31b093f74b0bee13fd5dea9037dc',
            'sources/b.cpp': 'db4b8fea71a29aedd0eac30601ac3489bdc72a3261697215901cf04da2d6a931',
            'sources/d.cpp': 'edf58f60231d34dfe3eb468e1b4cfeb35dd39cecd796183660cf13bf301f103b'
        }

        self.assertEqual(cache, expected_cache)

    def test_link_executable_using_cache(self):
        file_system = FileSystemMock(
            directories={
                self.project_structure.objects_root,
                self.project_structure.executables_root,
                self.project_structure.symbols_tables_root,
                self.project_structure.external_libraries_root,
                self.project_structure.external_libraries_interfaces_root
            },
            files={
                'target/objects/a.obj':                       b'object-a.',
                'target/external/libraries/b.dll':            b'external-library-b.',
                'target/external/libraries_interfaces/c.lib': b'external-library-interface-c.'
            }
        )

        compiler                      = CompilerMock(file_system)
        objects                       = ['target/objects/a.obj']
        external_libraries            = ['target/external/libraries/b.dll']
        external_libraries_interfaces = ['target/external/libraries_interfaces/c.lib']
        cache                         = {}

        executable, symbols_table = link_executable_using_cache(file_system,
                                                                self.project_structure,
                                                                compiler,
                                                                self.artifact_identifier,
                                                                objects,
                                                                external_libraries,
                                                                external_libraries_interfaces,
                                                                cache)

        self.assertEqual(normpath(executable), 
                         normpath('target/executables/org-art-x32-windows-compmock-debug-1.0.0.exe'))

        self.assertEqual(normpath(symbols_table),
                         normpath('target/symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb'))

        new_files = {
            'target/objects/a.obj':                       b'object-a.',
            'target/external/libraries/b.dll':            b'external-library-b.',
            'target/external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'target/executables/org-art-x32-windows-compmock-debug-1.0.0.exe':
                b'object-a.external-library-b.external-library-interface-c.exe',
            'target/symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb':
                b'object-a.external-library-b.external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): d for p, d in new_files.items()})

        new_cache = {}

        self.assertEqual(cache, new_cache)

    def test_link_library_using_cache(self):
        file_system = FileSystemMock(
            directories={
                self.project_structure.objects_root,
                self.project_structure.libraries_root,
                self.project_structure.libraries_interfaces_root,
                self.project_structure.symbols_tables_root,
                self.project_structure.external_libraries_root,
                self.project_structure.external_libraries_interfaces_root
            },
            files={
                'target/objects/a.obj':                       b'object-a.',
                'target/external/libraries/b.dll':            b'external-library-b.',
                'target/external/libraries_interfaces/c.lib': b'external-library-interface-c.'
            }
        )

        compiler                      = CompilerMock(file_system)
        objects                       = ['target/objects/a.obj']
        external_libraries            = ['target/external/libraries/b.dll']
        external_libraries_interfaces = ['target/external/libraries_interfaces/c.lib']
        cache                         = {}

        library, library_interface, symbols_table = link_library_using_cache(file_system,
                                                                             self.project_structure,
                                                                             compiler,
                                                                             self.artifact_identifier,
                                                                             objects,
                                                                             external_libraries,
                                                                             external_libraries_interfaces,
                                                                             cache)

        self.assertEqual(normpath(library), 
                         normpath('target/libraries/org-art-x32-windows-compmock-debug-1.0.0.dll'))

        self.assertEqual(normpath(library_interface), 
                         normpath('target/libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib'))

        self.assertEqual(normpath(symbols_table), 
                         normpath('target/symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb'))

        new_files = {
            'target/objects/a.obj':                       b'object-a.',
            'target/external/libraries/b.dll':            b'external-library-b.',
            'target/external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'target/libraries/org-art-x32-windows-compmock-debug-1.0.0.dll': 
                b'object-a.external-library-b.external-library-interface-c.dll',
            'target/libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib': 
                b'object-a.external-library-b.external-library-interface-c.lib',
            'target/symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb': 
                b'object-a.external-library-b.external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): data for p, data in new_files.items()})

        new_cache = {}

        self.assertEqual(cache, new_cache)
