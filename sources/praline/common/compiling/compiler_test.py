from os.path import normpath
from praline.common.compiling.compiler import compile_using_cache, link_executable_using_cache, link_library_using_cache
from praline.common.compiling.yield_descriptor import YieldDescriptor
from praline.common.file_system import get_separator, join, relative_path
from praline.common.testing.file_system_mock import FileSystemMock
from typing import List
from unittest import TestCase


class ProgressBarMock:
    def __init__(self, test_case: TestCase, resolution: int):
        self.test_case = test_case
        self.resolution = resolution
        self.progress = 0

    def __enter__(self):
        return self
    
    def update_summary(self, summary: str):
        pass

    def advance(self, amount: int = 1):
        self.progress += amount
        self.test_case.assertLessEqual(self.progress, self.resolution)

    def __exit__(self, type, value, traceback):
        self.test_case.assertEqual(self.progress, self.resolution)


class ProgressBarSupplierMock:
    def __init__(self, test_case: TestCase, expected_resolution: int):
        self.test_case = test_case
        self.expected_resolution = expected_resolution

    def create(self, resolution: int):
        self.test_case.assertEqual(resolution, self.expected_resolution)
        return ProgressBarMock(self.test_case, resolution)


class YieldDescriptorMock(YieldDescriptor):
    def get_object(self, sources_root: str, objects_root: str, source: str) -> str:
        name = relative_path(source, sources_root).replace(get_separator(), '-').replace('.cpp', '.obj')
        return join(objects_root, name)

    def get_executable(self, executables_root: str, name: str) -> str:
        return join(executables_root, f'{name}.exe')

    def get_library(self, libraries_root: str, name: str) -> str:
        return join(libraries_root, f'{name}.dll')

    def get_library_interface(self, library_interfaces_root: str, name: str) -> str:
        return join(library_interfaces_root, f'{name}.lib')

    def get_symbols_table(self, symbols_tables_root: str, name: str) -> str:
        return join(symbols_tables_root, f'{name}.pdb')


class CompilerMock:
    def __init__(self, file_system):
        self.file_system = file_system
        self.architecture = 'x32'
        self.platform = 'windows'
        self.mode = 'debug'

    def get_name(self):
        return 'compmock'

    def get_architecture(self) -> str:
        return self.architecture

    def get_platform(self) -> str:
        return self.platform

    def get_mode(self) -> str:
        return self.mode

    def matches(self) -> bool:
        return True

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
                data = data + o.read()
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
                data = data + o.read()
        with self.file_system.open_file(library, 'wb') as l:
            l.write(data + b'dll')
        with self.file_system.open_file(library_interface, 'wb') as li:
            li.write(data + b'lib')
        with self.file_system.open_file(symbols_table, 'wb') as s:
            s.write(data + b'pbd')

    def get_yield_descriptor(self) -> YieldDescriptor:
        return YieldDescriptorMock()

    def get_packager(self):
        raise NotImplementedError()


organization = 'org'
artifact     = 'art'
version      = '1.0.0'

class CompilerTest(TestCase):
    def test_compilation_using_cache(self):
        objects_root = 'objects/'
        sources_root = 'sources/'
        headers_root = 'sources/'
        external_headers_root = 'external/headers/'
        file_system = FileSystemMock({
            objects_root,
            sources_root,
            headers_root,
            external_headers_root
        }, {
            'sources/a.hpp': b'header-a.',
            'sources/a.cpp': b'source-a.',
            'sources/b.hpp': b'updated-header-b.',
            'sources/b.cpp': b'source-b.',
            'sources/d.hpp': b'header-d.',
            'sources/d.cpp': b'source-d.',
            'objects/a.obj': b'header-a.source-a.',
            'objects/b.obj': b'header-b.source-b.',
            'objects/c.obj': b'header-c.source-c.'
        })
        compiler       = CompilerMock(file_system)
        headers        = ['sources/a.hpp', 'sources/b.hpp', 'sources/d.hpp']
        sources        = ['sources/a.cpp', 'sources/b.cpp', 'sources/d.cpp']
        to_be_compiled = [                 'sources/b.cpp', 'sources/d.cpp']
        cache          = {
            'sources/a.cpp': '8ceb2730683fdf075d4ede855d5ed98f32be31b093f74b0bee13fd5dea9037dc',
            'sources/b.cpp': '5addc12d3b54fb9836277adccb06a03131ab92c10faf97613259bb77775db8d3',
            'sources/c.cpp': '853b9c27fdbe775b24a8fb14f7ef43aba1d6e698df4f2df6bc4e0f22c800f1d5'
        }

        progress_bar_supplier = ProgressBarSupplierMock(self, expected_resolution=len(to_be_compiled))

        objects = compile_using_cache(file_system,
                                      compiler,
                                      headers_root,
                                      external_headers_root,
                                      sources_root,
                                      objects_root,
                                      headers,
                                      sources,
                                      cache,
                                      progress_bar_supplier)

        self.assertEqual(objects, ['objects/a.obj', 'objects/b.obj', 'objects/d.obj'])

        new_files = {
            'sources/a.hpp': b'header-a.',
            'sources/a.cpp': b'source-a.',
            'sources/b.hpp': b'updated-header-b.',
            'sources/b.cpp': b'source-b.',
            'sources/d.hpp': b'header-d.',
            'sources/d.cpp': b'source-d.',
            'objects/a.obj': b'header-a.source-a.',
            'objects/b.obj': b'updated-header-b.source-b.',
            'objects/d.obj': b'header-d.source-d.'
        }

        self.assertEqual(file_system.files, {normpath(p): data for p, data in new_files.items()})

        new_cache = {
            'sources/a.cpp': '8ceb2730683fdf075d4ede855d5ed98f32be31b093f74b0bee13fd5dea9037dc',
            'sources/b.cpp': 'db4b8fea71a29aedd0eac30601ac3489bdc72a3261697215901cf04da2d6a931',
            'sources/d.cpp': 'edf58f60231d34dfe3eb468e1b4cfeb35dd39cecd796183660cf13bf301f103b'
        }

        self.assertEqual(cache, new_cache)

    def test_link_executable_using_clean_cache(self):
        objects_root                       = 'objects/'
        executables_root                   = 'executables/'
        symbols_tables_root                = 'symbols_tables/'
        external_libraries_root            = 'external/libraries'
        external_libraries_interfaces_root = 'external/libraries_interfaces'
        file_system = FileSystemMock({
            objects_root,
            executables_root,
            symbols_tables_root,
            external_libraries_root,
            external_libraries_interfaces_root
        }, {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.'
        })
        compiler                           = CompilerMock(file_system)
        objects                            = ['objects/a.obj']
        external_libraries                 = ['external/libraries/b.dll']
        external_libraries_interfaces      = ['external/libraries_interfaces/c.lib']
        cache                              = {}

        executable, symbols_table = link_executable_using_cache(file_system,
                                                                compiler,
                                                                executables_root,
                                                                symbols_tables_root,
                                                                external_libraries_root,
                                                                external_libraries_interfaces_root,
                                                                objects,
                                                                external_libraries,
                                                                external_libraries_interfaces,
                                                                organization,
                                                                artifact,
                                                                version,
                                                                cache)

        self.assertEqual(executable, 'executables/org-art-x32-windows-compmock-debug-1.0.0.exe')

        self.assertEqual(symbols_table, 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')

        new_files = {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'executables/org-art-x32-windows-compmock-debug-1.0.0.exe':       b'object-a.external-library-b.external-library-interface-c.exe',
            'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb':    b'object-a.external-library-b.external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): d for p, d in new_files.items()})

        new_cache = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.dll':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('executables/org-art-x32-windows-compmock-debug-1.0.0.exe', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }

        self.assertEqual(cache, new_cache)

    def test_link_executable_using_cache_with_changed_object(self):
        objects_root                       = 'objects/'
        executables_root                   = 'executables/'
        symbols_tables_root                = 'symbols_tables/'
        external_libraries_root            = 'external/libraries'
        external_libraries_interfaces_root = 'external/libraries_interfaces'
        file_system = FileSystemMock({
            objects_root,
            executables_root,
            symbols_tables_root,
            external_libraries_root,
            external_libraries_interfaces_root
        }, {
            'objects/a.obj':                       b'updated-object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'executables/org-art-x32-windows-compmock-debug-1.0.0.exe': b'object-a.external-library-b.external-library-interface-c.exe',
            'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb': b'object-a.external-library-b.external-library-interface-c.pbd'
        })
        compiler                           = CompilerMock(file_system)
        objects                            = ['objects/a.obj']
        external_libraries                 = ['external/libraries/b.dll']
        external_libraries_interfaces      = ['external/libraries_interfaces/c.lib']
        cache                              = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.dll':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('executables/org-art-x32-windows-compmock-debug-1.0.0.exe', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }

        executable, symbols_table = link_executable_using_cache(file_system,
                                                                compiler,
                                                                executables_root,
                                                                symbols_tables_root,
                                                                external_libraries_root,
                                                                external_libraries_interfaces_root,
                                                                objects,
                                                                external_libraries,
                                                                external_libraries_interfaces,
                                                                organization,
                                                                artifact,
                                                                version,
                                                                cache)

        self.assertEqual(executable, 'executables/org-art-x32-windows-compmock-debug-1.0.0.exe')

        self.assertEqual(symbols_table, 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')

        new_files = {
            'objects/a.obj':                       b'updated-object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'executables/org-art-x32-windows-compmock-debug-1.0.0.exe': b'updated-object-a.external-library-b.external-library-interface-c.exe',
            'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb': b'updated-object-a.external-library-b.external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): data for p, data in new_files.items()})

        new_cache = {
            'input': {
                'objects/a.obj':                       'e44b36b477a83194da4a4da7a97ed69932cf3729127dfc98af3a83c7abe43e10',
                'external/libraries/b.dll':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('executables/org-art-x32-windows-compmock-debug-1.0.0.exe', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }

        self.assertEqual(cache, new_cache)

    def test_link_executable_using_cache_with_changed_external_library(self):
        objects_root                       = 'objects/'
        executables_root                   = 'executables/'
        symbols_tables_root                = 'symbols_tables/'
        external_libraries_root            = 'external/libraries'
        external_libraries_interfaces_root = 'external/libraries_interfaces'
        file_system = FileSystemMock({
            objects_root,
            executables_root,
            symbols_tables_root,
            external_libraries_root,
            external_libraries_interfaces_root
        }, {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'updated-external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'executables/my-executable.exe':       b'object-a.external-library-b.external-library-interface-c.exe',
            'symbols_tables/my-executable.pdb':    b'object-a.external-library-b.external-library-interface-c.pbd'
        })
        compiler                           = CompilerMock(file_system)
        objects                            = ['objects/a.obj']
        external_libraries                 = ['external/libraries/b.dll']
        external_libraries_interfaces      = ['external/libraries_interfaces/c.lib']
        cache                              = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.dll':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('executables/my-executable.exe', 'symbols_tables/my-executable.pdb')
        }

        executable, symbols_table = link_executable_using_cache(file_system,
                                                                compiler,
                                                                executables_root,
                                                                symbols_tables_root,
                                                                external_libraries_root,
                                                                external_libraries_interfaces_root,
                                                                objects,
                                                                external_libraries,
                                                                external_libraries_interfaces,
                                                                organization,
                                                                artifact,
                                                                version,
                                                                cache)

        self.assertEqual(executable, 'executables/org-art-x32-windows-compmock-debug-1.0.0.exe')

        self.assertEqual(symbols_table, 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')

        new_files = {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'updated-external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'executables/org-art-x32-windows-compmock-debug-1.0.0.exe': b'object-a.updated-external-library-b.external-library-interface-c.exe',
            'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb': b'object-a.updated-external-library-b.external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): data for p, data in new_files.items()})

        new_cache = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.dll':            '09e93c7c7aae2efb94a0f6d12ee5b59c0b7a810989d84f866ef515e8dd0f6e41',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('executables/org-art-x32-windows-compmock-debug-1.0.0.exe', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }

        self.assertEqual(cache, new_cache)

    def test_link_executable_using_cache_with_changed_external_library_interface(self):
        objects_root                       = 'objects/'
        executables_root                   = 'executables/'
        symbols_tables_root                = 'symbols_tables/'
        external_libraries_root            = 'external/libraries'
        external_libraries_interfaces_root = 'external/libraries_interfaces'
        file_system = FileSystemMock({
            objects_root,
            executables_root,
            symbols_tables_root,
            external_libraries_root,
            external_libraries_interfaces_root
        }, {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'updated-external-library-interface-c.',
            'executables/my-executable.exe':       b'object-a.external-library-b.external-library-interface-c.exe',
            'symbols_tables/my-executable.pdb':    b'object-a.external-library-b.external-library-interface-c.pbd'
        })
        compiler                           = CompilerMock(file_system)
        objects                            = ['objects/a.obj']
        external_libraries                 = ['external/libraries/b.dll']
        external_libraries_interfaces      = ['external/libraries_interfaces/c.lib']
        name                               = 'my-executable'
        cache                              = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.dll':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('executables/my-executable.exe', 'symbols_tables/my-executable.pdb')
        }

        executable, symbols_table = link_executable_using_cache(file_system,
                                                                compiler,
                                                                executables_root,
                                                                symbols_tables_root,
                                                                external_libraries_root,
                                                                external_libraries_interfaces_root,
                                                                objects,
                                                                external_libraries,
                                                                external_libraries_interfaces,
                                                                organization,
                                                                artifact,
                                                                version,
                                                                cache)

        self.assertEqual(executable, 'executables/org-art-x32-windows-compmock-debug-1.0.0.exe')

        self.assertEqual(symbols_table, 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')

        new_files = {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'updated-external-library-interface-c.',
            'executables/org-art-x32-windows-compmock-debug-1.0.0.exe': b'object-a.external-library-b.updated-external-library-interface-c.exe',
            'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb': b'object-a.external-library-b.updated-external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): data for p, data in new_files.items()})

        new_cache = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.dll':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '4655380785da55ddee626b49e92bf336911a4f8ea828b1693ecbf1d12714d8f8'
            },
            'output': ('executables/org-art-x32-windows-compmock-debug-1.0.0.exe', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }

        self.assertEqual(cache, new_cache)

    def test_link_library_using_clean_cache(self):
        objects_root                       = 'objects/'
        libraries_root                     = 'libraries/'
        libraries_interfaces_root          = 'libraries_interfaces/'
        symbols_tables_root                = 'symbols_tables/'
        external_libraries_root            = 'external/libraries'
        external_libraries_interfaces_root = 'external/libraries_interfaces'
        file_system = FileSystemMock({
            objects_root,
            libraries_root,
            libraries_interfaces_root,
            symbols_tables_root,
            external_libraries_root,
            external_libraries_interfaces_root
        }, {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.'
        })
        compiler                           = CompilerMock(file_system)
        objects                            = ['objects/a.obj']
        external_libraries                 = ['external/libraries/b.dll']
        external_libraries_interfaces      = ['external/libraries_interfaces/c.lib']
        name                               = 'my-library'
        cache                              = {}
        library, library_interface, symbols_table = link_library_using_cache(file_system,
                                                                             compiler,
                                                                             libraries_root,
                                                                             libraries_interfaces_root,
                                                                             symbols_tables_root,
                                                                             external_libraries_root,
                                                                             external_libraries_interfaces_root,
                                                                             objects,
                                                                             external_libraries,
                                                                             external_libraries_interfaces,
                                                                             organization,
                                                                             artifact,
                                                                             version,
                                                                             cache)

        self.assertEqual(library, 'libraries/org-art-x32-windows-compmock-debug-1.0.0.dll')

        self.assertEqual(library_interface, 'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib')

        self.assertEqual(symbols_table, 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')

        new_files = {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'libraries/org-art-x32-windows-compmock-debug-1.0.0.dll': b'object-a.external-library-b.external-library-interface-c.dll',
            'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib': b'object-a.external-library-b.external-library-interface-c.lib',
            'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb': b'object-a.external-library-b.external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): data for p, data in new_files.items()})

        new_cache = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.dll':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('libraries/org-art-x32-windows-compmock-debug-1.0.0.dll', 'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }

        self.assertEqual(cache, new_cache)

    def test_link_library_using_cache_with_changed_object(self):
        objects_root                       = 'objects/'
        libraries_root                     = 'libraries/'
        libraries_interfaces_root          = 'libraries_interfaces/'
        symbols_tables_root                = 'symbols_tables/'
        external_libraries_root            = 'external/libraries'
        external_libraries_interfaces_root = 'external/libraries_interfaces'
        file_system = FileSystemMock({
            objects_root,
            libraries_root,
            libraries_interfaces_root,
            symbols_tables_root,
            external_libraries_root,
            external_libraries_interfaces_root,
        }, {
            'objects/a.obj':                       b'updated-object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.'
        })
        compiler                           = CompilerMock(file_system)
        objects                            = ['objects/a.obj']
        external_libraries                 = ['external/libraries/b.dll']
        external_libraries_interfaces      = ['external/libraries_interfaces/c.lib']
        cache                              = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.obj':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('libraries/org-art-x32-windows-compmock-debug-1.0.0.dll', 'libraries/interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }
        library, library_interface, symbols_table = link_library_using_cache(file_system,
                                                                             compiler,
                                                                             libraries_root,
                                                                             libraries_interfaces_root,
                                                                             symbols_tables_root,
                                                                             external_libraries_root,
                                                                             external_libraries_interfaces_root,
                                                                             objects,
                                                                             external_libraries,
                                                                             external_libraries_interfaces,
                                                                             organization,
                                                                             artifact,
                                                                             version,
                                                                             cache)

        self.assertEqual(library, 'libraries/org-art-x32-windows-compmock-debug-1.0.0.dll')

        self.assertEqual(library_interface, 'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib')

        self.assertEqual(symbols_table, 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')

        new_files = {
            'objects/a.obj':                       b'updated-object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'libraries/org-art-x32-windows-compmock-debug-1.0.0.dll': b'updated-object-a.external-library-b.external-library-interface-c.dll',
            'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib': b'updated-object-a.external-library-b.external-library-interface-c.lib',
            'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb': b'updated-object-a.external-library-b.external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): data for p, data in new_files.items()})

        new_cache = {
            'input': {
                'objects/a.obj':                       'e44b36b477a83194da4a4da7a97ed69932cf3729127dfc98af3a83c7abe43e10',
                'external/libraries/b.dll':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('libraries/org-art-x32-windows-compmock-debug-1.0.0.dll', 'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }

        self.assertEqual(cache, new_cache)

    def test_link_library_using_cache_with_changed_library(self):
        objects_root                       = 'objects/'
        libraries_root                     = 'libraries/'
        libraries_interfaces_root          = 'libraries_interfaces/'
        symbols_tables_root                = 'symbols_tables/'
        external_libraries_root            = 'external/libraries'
        external_libraries_interfaces_root = 'external/libraries_interfaces'
        file_system = FileSystemMock({
            objects_root,
            libraries_root,
            libraries_interfaces_root,
            symbols_tables_root,
            external_libraries_root,
            external_libraries_interfaces_root
        }, {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'updated-external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.'
        })
        compiler                           = CompilerMock(file_system)
        objects                            = ['objects/a.obj']
        external_libraries                 = ['external/libraries/b.dll']
        external_libraries_interfaces      = ['external/libraries_interfaces/c.lib']
        cache                              = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.obj':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('libraries/org-art-x32-windows-compmock-debug-1.0.0.dll', 'libraries/interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }
        library, library_interface, symbols_table = link_library_using_cache(file_system,
                                                                             compiler,
                                                                             libraries_root,
                                                                             libraries_interfaces_root,
                                                                             symbols_tables_root,
                                                                             external_libraries_root,
                                                                             external_libraries_interfaces_root,
                                                                             objects,
                                                                             external_libraries,
                                                                             external_libraries_interfaces,
                                                                             organization,
                                                                             artifact,
                                                                             version,
                                                                             cache)

        self.assertEqual(library, 'libraries/org-art-x32-windows-compmock-debug-1.0.0.dll')

        self.assertEqual(library_interface, 'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib')

        self.assertEqual(symbols_table, 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')

        new_files = {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'updated-external-library-b.',
            'external/libraries_interfaces/c.lib': b'external-library-interface-c.',
            'libraries/org-art-x32-windows-compmock-debug-1.0.0.dll': b'object-a.updated-external-library-b.external-library-interface-c.dll',
            'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib': b'object-a.updated-external-library-b.external-library-interface-c.lib',
            'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb': b'object-a.updated-external-library-b.external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): data for p, data in new_files.items()})

        new_cache = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.dll':            '09e93c7c7aae2efb94a0f6d12ee5b59c0b7a810989d84f866ef515e8dd0f6e41',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('libraries/org-art-x32-windows-compmock-debug-1.0.0.dll', 'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }

        self.assertEqual(cache, new_cache)

    def test_link_library_using_cache_with_changed_library_interface(self):
        objects_root                       = 'objects/'
        libraries_root                     = 'libraries/'
        libraries_interfaces_root          = 'libraries_interfaces/'
        symbols_tables_root                = 'symbols_tables/'
        external_libraries_root            = 'external/libraries'
        external_libraries_interfaces_root = 'external/libraries_interfaces'
        file_system = FileSystemMock({
            objects_root,
            libraries_root,
            libraries_interfaces_root,
            symbols_tables_root,
            external_libraries_root,
            external_libraries_interfaces_root
        }, {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'updated-external-library-interface-c.'
        })
        compiler                           = CompilerMock(file_system)
        objects                            = ['objects/a.obj']
        external_libraries                 = ['external/libraries/b.dll']
        external_libraries_interfaces      = ['external/libraries_interfaces/c.lib']
        cache                              = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.obj':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '8c777213d1130643127d77653c90f5d6784f6f95dac361afb454a3e6db084f4e'
            },
            'output': ('libraries/org-art-x32-windows-compmock-debug-1.0.0.dll', 'libraries/interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }
        library, library_interface, symbols_table = link_library_using_cache(file_system,
                                                                             compiler,
                                                                             libraries_root,
                                                                             libraries_interfaces_root,
                                                                             symbols_tables_root,
                                                                             external_libraries_root,
                                                                             external_libraries_interfaces_root,
                                                                             objects,
                                                                             external_libraries,
                                                                             external_libraries_interfaces,
                                                                             organization,
                                                                             artifact,
                                                                             version,
                                                                             cache)

        self.assertEqual(library, 'libraries/org-art-x32-windows-compmock-debug-1.0.0.dll')

        self.assertEqual(library_interface, 'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib')

        self.assertEqual(symbols_table, 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')

        new_files = {
            'objects/a.obj':                       b'object-a.',
            'external/libraries/b.dll':            b'external-library-b.',
            'external/libraries_interfaces/c.lib': b'updated-external-library-interface-c.',
            'libraries/org-art-x32-windows-compmock-debug-1.0.0.dll': b'object-a.external-library-b.updated-external-library-interface-c.dll',
            'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib': b'object-a.external-library-b.updated-external-library-interface-c.lib',
            'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb': b'object-a.external-library-b.updated-external-library-interface-c.pbd'
        }

        self.assertEqual(file_system.files, {normpath(p): data for p, data in new_files.items()})

        new_cache = {
            'input': {
                'objects/a.obj':                       'a6cc476fe402432f09d3e66d73b6382421ee1a855ac6bde79357fc1483878463',
                'external/libraries/b.dll':            '440602105d9abfce75656e19197e74539add8cb0dd002f4a550d46d7e8c1e837',
                'external/libraries_interfaces/c.lib': '4655380785da55ddee626b49e92bf336911a4f8ea828b1693ecbf1d12714d8f8'
            },
            'output': ('libraries/org-art-x32-windows-compmock-debug-1.0.0.dll', 'libraries_interfaces/org-art-x32-windows-compmock-debug-1.0.0.lib', 'symbols_tables/org-art-x32-windows-compmock-debug-1.0.0.pdb')
        }

        self.assertEqual(cache, new_cache)
