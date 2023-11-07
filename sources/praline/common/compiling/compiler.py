from praline.common import ArtifactManifest, Compiler, Platform, ProjectStructure, get_duplicates
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem, join, get_separator, relative_path
from praline.common.hashing import hash_binary, delta, DeltaType, progression_resolution
from praline.common.reflection import subclasses_of

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class CompilerInstantionError(Exception):
    pass


class NoSupportedCompilerFoundError(Exception):
    pass


class IYieldDescriptor(ABC):
    @abstractmethod
    def get_object(self, sources_root: str, objects_root: str, source: str) -> str:
        name = relative_path(source, sources_root).replace(get_separator(), '-')[:-len('.cpp')]
        return join(objects_root, name)

    @abstractmethod
    def get_executable(self, executables_root, name: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_library(self, libraries_root, name: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_library_interface(self, libraries_interfaces_root: str, name: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_symbols_table(self, symbols_tables_root: str, name: str) -> str:
        raise NotImplementedError()


class ICompiler(ABC):
    @abstractmethod
    def get_yield_descriptor(self) -> IYieldDescriptor:
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
                object_: str) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def link_executable(self,
                        external_libraries_root: str,
                        external_libraries_interfaces_root: str,
                        objects: List[str],
                        external_libraries: List[str],
                        external_libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str) -> Tuple[str, str, str]:
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
                     symbols_table: str) -> Tuple[str, str, str]:
        raise NotImplementedError()


class ICompilerSupplier(ABC):
    @abstractmethod
    def get_name(self) -> Compiler:
        raise NotImplementedError()

    @abstractmethod
    def get_yield_descriptor(self) -> IYieldDescriptor:
        raise NotImplementedError()

    @abstractmethod
    def instantiate_compiler(self, file_system: FileSystem, artifact_manifest: ArtifactManifest) -> ICompiler:
        raise NotImplementedError()


class CompilerWrapper:
    def __init__(self, file_system: FileSystem, compiler: ICompiler):
        self.file_system = file_system
        self.compiler    = compiler

    def get_yield_descriptor(self) -> IYieldDescriptor:
        return self.compiler.get_yield_descriptor()

    def compile_using_cache(self,
                            project_structure: ProjectStructure,
                            headers: List[str],
                            sources: List[str],
                            cache: Dict[str, Any],
                            progress_bar_supplier: ProgressBarSupplier) -> List[str]:
        new_cache        = {}
        objects          = []
        yield_descriptor = self.compiler.get_yield_descriptor()
        resolution       = progression_resolution(sources, cache)
        with progress_bar_supplier.create(resolution) as progress_bar:
            def hasher(source: str):
                progress_bar.update_summary(source)
                return hash_binary(self.compiler.preprocess(project_structure.sources_root, 
                                                            project_structure.external_headers_root,
                                                            headers, 
                                                            source))
            for item in delta(sources, hasher, cache, new_cache):
                source  = item.key
                object_ = yield_descriptor.get_object(project_structure.sources_root, 
                                                      project_structure.objects_root, 
                                                      source)
                if item.delta_type in [DeltaType.Added, DeltaType.Modified]:
                    self.compiler.compile(project_structure.sources_root, 
                                          project_structure.external_headers_root, 
                                          headers, 
                                          source, 
                                          object_)
                    objects.append(object_)
                elif item.delta_type == DeltaType.UpToDate:
                    if not self.file_system.exists(object_):
                        self.compiler.compile(project_structure.sources_root, 
                                              project_structure.external_headers_root, 
                                              headers, 
                                              source, 
                                              object_)
                    objects.append(object_)
                elif item.delta_type == DeltaType.Removed:
                    if self.file_system.exists(object_):
                        self.file_system.remove_file(object_)
                progress_bar.advance()
        cache.clear()
        cache.update(new_cache)
        return objects

    def link_executable_using_cache(self,
                                    project_structure: ProjectStructure,
                                    artifact_identifier: str,
                                    objects: List[str],
                                    external_libraries: List[str],
                                    external_libraries_interfaces: List[str],
                                    cache: Dict[str, Any]) -> Tuple[str, str]:
        yield_descriptor = self.compiler.get_yield_descriptor()
        executable       = yield_descriptor.get_executable(project_structure.executables_root, 
                                                           artifact_identifier)
        symbols_table    = yield_descriptor.get_symbols_table(project_structure.symbols_tables_root, 
                                                              artifact_identifier)
        self.compiler.link_executable(project_structure.external_libraries_root,
                                      project_structure.external_libraries_interfaces_root,
                                      objects,
                                      external_libraries,
                                      external_libraries_interfaces,
                                      executable,
                                      symbols_table)
        if self.file_system.exists(symbols_table):
            return (executable, symbols_table)
        else:
            return (executable, None)

    def link_library_using_cache(self,
                                 project_structure: ProjectStructure,
                                 artifact_identifier: str,
                                 objects: List[str],
                                 external_libraries: List[str],
                                 external_libraries_interfaces: List[str],
                                 cache: Dict[str, Any]) -> Tuple[str, str, str]:
        yield_descriptor  = self.compiler.get_yield_descriptor()
        library           = yield_descriptor.get_library(project_structure.libraries_root, 
                                                         artifact_identifier)
        library_interface = yield_descriptor.get_library_interface(project_structure.libraries_interfaces_root, 
                                                                   artifact_identifier)
        symbols_table     = yield_descriptor.get_symbols_table(project_structure.symbols_tables_root, 
                                                               artifact_identifier)
        self.compiler.link_library(project_structure.external_libraries_root,
                                   project_structure.external_libraries_interfaces_root,
                                   objects,
                                   external_libraries,
                                   external_libraries_interfaces,
                                   library,
                                   library_interface,
                                   symbols_table)
        if self.file_system.exists(symbols_table):
            return (library, library_interface, symbols_table)
        else:
            return (library, library_interface, None)


def get_compiler_suppliers() -> List[ICompilerSupplier]:
    compiler_suppliers = [klass() for klass in subclasses_of(ICompilerSupplier)]
    duplicates = get_duplicates(compiler_suppliers, lambda a, b: a.get_name() == b.get_name())
    if duplicates:
        raise RuntimeError("multiple compilers defined with the same name "
                           f"'{compiler_suppliers[duplicates[0][0]].get_name()}'")
    return compiler_suppliers


def get_compiler_supplier(name: Compiler) -> ICompilerSupplier:
    compilers = get_compiler_suppliers()
    matching  = [compiler for compiler in compilers if compiler.get_name() == name]
    if not matching:
        raise RuntimeError(f"no compiler named '{name}' was found")
    return matching[0]


def get_prefered_compiler(file_system: FileSystem) -> Compiler:
    platform = file_system.get_platform()
    if platform == Platform.windows:
        return Compiler.clang_cl
    elif platform == Platform.linux:
        return Compiler.msvc
    elif platform == Platform.darwin:
        return Compiler.clang
    else:
        None


def intantiate_compiler(file_system: FileSystem,
                        artifact_manifest: ArtifactManifest, 
                        compiler_name: Compiler, 
                        fallback_compilers: List[Compiler]) -> Tuple[ArtifactManifest, CompilerWrapper]:
    manifest       = vars(artifact_manifest)
    final_manifest = None
    compiler       = None
    if compiler_name:
        manifest['compiler'] = compiler_name
        final_manifest       = ArtifactManifest(**manifest)
        supplier             = get_compiler_supplier(compiler_name)
        compiler             = supplier.instantiate_compiler(file_system, final_manifest)
    else:        
        prefered_compiler = get_prefered_compiler(file_system)
        compilers = fallback_compilers[:]
        if prefered_compiler in fallback_compilers:
            compilers.remove(prefered_compiler)
            compilers = [prefered_compiler] + compilers
    
        messages = []
        for candidate in compilers:
            try:
                manifest['compiler'] = candidate
                final_manifest       = ArtifactManifest(**manifest)
                supplier             = get_compiler_supplier(candidate)
                compiler             = supplier.instantiate_compiler(file_system, final_manifest)
                break
            except CompilerInstantionError as e:
                messages.append(str(e))
    
        if compiler == None:
            raise NoSupportedCompilerFoundError(f"no suitable compiler was found:\n" + '\n'.join(messages))
    
    return (final_manifest, CompilerWrapper(file_system, compiler))
