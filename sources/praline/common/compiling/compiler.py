from abc import ABC, abstractmethod
from praline.common.compiling.yield_descriptor import YieldDescriptor
from praline.common.constants import get_artifact_full_name
from praline.common.file_system import directory_name, FileSystem, get_separator, join, relative_path
from praline.common.hashing import key_delta, hash_binary, hash_file
from praline.common.reflection import subclasses_of
from typing import Any, Dict, List, Tuple


class Compiler(ABC):
    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_architecture(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_platform(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_mode(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def matches(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def preprocess(self,
                   headers_root: str,
                   external_headers_root: str,
                   headers: List[str],
                   source: str) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def compile(self,
                headers_root: str,
                external_headers_root: str,
                headers: List[str],
                source: str,
                object_: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def link_executable(self,
                        external_libraries_root: str,
                        external_libraries_interfaces_root: str,
                        objects: List[str],
                        external_libraries: List[str],
                        external_libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def link_library(self,
                     external_libraries_root: str,
                     external_libraries_interfaces_root: str,
                     objects: List[str],
                     external_libraries: List[str],
                     external_libraries_interfaces: List[str],
                     library: str,
                     library_interface: str,
                     symbols_table: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_yield_descriptor(self) -> YieldDescriptor:
        raise NotImplementedError()


def compile_using_cache(file_system: FileSystem,
                        compiler: Compiler,
                        headers_root: str,
                        external_headers_root: str,
                        sources_root: str,
                        objects_root: str,
                        headers: List[str],
                        sources: List[str],
                        cache: Dict[str, Any]) -> List[str]:
    file_system.create_directory_if_missing(objects_root)

    def hash_translation_unit(source):
        return hash_binary(compiler.preprocess(headers_root, external_headers_root, headers, source))

    updated, removed, new_cache = key_delta(sources, hash_translation_unit, cache)
    objects                     = []
    yield_descriptor            = compiler.get_yield_descriptor()

    for source in updated:
        object_ = yield_descriptor.get_object(sources_root, objects_root, source)
        compiler.compile(headers_root, external_headers_root, headers, source, object_)
    for source in removed:
        object_ = yield_descriptor.get_object(sources_root, objects_root, source)
        if file_system.exists(object_):
            file_system.remove_file(object_)
    for source in sources:
        object_ = yield_descriptor.get_object(sources_root, objects_root, source)
        if not file_system.exists(object_):
            compiler.compile(headers_root, external_headers_root, headers, source, object_)
        objects.append(object_)
    
    cache.clear()
    cache.update(new_cache)
    return objects


def link_executable_using_cache(file_system: FileSystem,
                                compiler: Compiler,
                                executables_root: str,
                                symbols_tables_root: str,
                                external_libraries_root: str,
                                external_libraries_interfaces_root: str,
                                objects: List[str],
                                external_libraries: List[str],
                                external_libraries_interfaces: List[str],
                                organization: str,
                                artifact: str,
                                version: str,
                                cache: Dict[str, Any],
                                is_test: bool = False) -> Tuple[str, str]:
    file_system.create_directory_if_missing(executables_root)
    file_system.create_directory_if_missing(symbols_tables_root)

    name                        = get_artifact_full_name(organization, artifact, compiler.get_architecture(),
                                                         compiler.get_platform(), compiler.get_name(),
                                                         compiler.get_mode(), version) + ('.test' if is_test else '')
    cache['input']              = input_ = cache.get('input', {})
    (old_executable,
     old_symbols_table)         = cache.get('output', (None, None))
    hasher                      = lambda path: hash_file(file_system, path)
    updated, removed, new_cache = key_delta(objects + external_libraries + external_libraries_interfaces, hasher, input_)
    yield_descriptor            = compiler.get_yield_descriptor()
    executable                  = yield_descriptor.get_executable(executables_root, name)
    symbols_table               = yield_descriptor.get_symbols_table(symbols_tables_root, name)
    remake_executable           = executable and not file_system.exists(executable)
    remake_symbols_table        = symbols_table and not file_system.exists(symbols_table)
    if updated or removed or remake_executable or remake_symbols_table:
        if old_executable and file_system.exists(old_executable):
            file_system.remove_file(old_executable)
        if old_symbols_table and file_system.exists(old_symbols_table):
            file_system.remove_file(old_symbols_table)
        compiler.link_executable(external_libraries_root,
                                 external_libraries_interfaces_root,
                                 objects,
                                 external_libraries,
                                 external_libraries_interfaces,
                                 executable,
                                 symbols_table)
    cache['input'] = new_cache
    cache['output'] = (executable, symbols_table)
    return (executable, symbols_table)


def link_library_using_cache(file_system: FileSystem,
                             compiler: Compiler,
                             libraries_root: str,
                             libraries_interfaces_root: str,
                             symbols_tables_root: str,
                             external_libraries_root: str,
                             external_libraries_interfaces_root: str,
                             objects: List[str],
                             external_libraries: List[str],
                             external_libraries_interfaces: List[str],
                             organization: str,
                             artifact: str,
                             version: str,
                             cache: Dict[str, Any]) -> Tuple[str, str, str]:
    file_system.create_directory_if_missing(libraries_root)
    file_system.create_directory_if_missing(libraries_interfaces_root)
    file_system.create_directory_if_missing(symbols_tables_root)
    name                        = get_artifact_full_name(organization, artifact, compiler.get_architecture(), 
                                                         compiler.get_platform(), compiler.get_name(),
                                                         compiler.get_mode(), version)
    cache['input']              = input_ = cache.get('input', {})
    (old_library, 
     old_library_interface,
     old_symbols_table)         = cache.get('output', (None, None, None))
    hasher                      = lambda path: hash_file(file_system, path)
    updated, removed, new_cache = key_delta(objects + external_libraries + external_libraries_interfaces, hasher, input_)
    yield_descriptor            = compiler.get_yield_descriptor()
    library                     = yield_descriptor.get_library(libraries_root, name)
    library_interface           = yield_descriptor.get_library_interface(libraries_interfaces_root, name)
    symbols_table               = yield_descriptor.get_symbols_table(symbols_tables_root, name)
    remake_library              = library and not file_system.exists(library)
    remake_library_interface    = library_interface and not file_system.exists(library_interface)
    remake_symbols_table        = symbols_table and not file_system.exists(symbols_table)
    if updated or removed or remake_library or remake_library_interface or remake_symbols_table:
        if old_library and file_system.exists(old_library):
            file_system.remove_file(old_library)
        if old_library_interface and file_system.exists(old_library_interface):
            file_system.remove_file(old_library_interface)
        if old_symbols_table and file_system.exists(old_symbols_table):
            file_system.remove_file(old_symbols_table)
        compiler.link_library(external_libraries_root,
                              external_libraries_interfaces_root,
                              objects,
                              external_libraries,
                              external_libraries_interfaces,
                              library,
                              library_interface,
                              symbols_table)
    cache['input'] = new_cache
    cache['output'] = (library, library_interface, symbols_table)
    return (library, library_interface, symbols_table)


def get_compilers(file_system: FileSystem, architecture: str, platform: str, mode: str) -> List[Compiler]:
    compilers = [klass(file_system, architecture, platform, mode) for klass in subclasses_of(Compiler)]
    duplicates = [(i, j) for i in range(len(compilers)) for j in range(i + 1, len(compilers)) if compilers[i].get_name() == compilers[j].get_name()]
    if duplicates:
        raise RuntimeError(f"multiple compilers defined with the same name '{compilers[duplicates[0][0]].get_name()}'")
    return compilers

def get_compiler(file_system: FileSystem, name: str, architecture: str, platform: str, mode: str) -> Compiler:
    compilers = [klass(file_system, architecture, platform, mode) for klass in subclasses_of(Compiler)]
    matching  = [compiler for compiler in compilers if compiler.get_name() == name]
    if not matching:
        raise RuntimeError(f"no compiler named '{name}' was found")
    return matching[0]
