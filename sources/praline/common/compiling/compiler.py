from praline.common import ArtifactManifest, CompilerType, Platform, get_duplicates
from praline.common.yield_descriptor import IYieldDescriptor
from praline.common.project_structure import ProjectStructure
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem
from praline.common.hashing import hash_binary, delta, DeltaType, progression_resolution
from praline.common.reflection import subclasses_of

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class CompilerInstantionError(Exception):
    pass


class NoSupportedCompilerFoundError(Exception):
    pass


class ICompilingStrategy(ABC):
    @abstractmethod
    def get_yield_descriptor(self) -> IYieldDescriptor:
        raise NotImplementedError()

    @abstractmethod
    def preprocess(self, headers: List[str], source_path: str) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def compile(self, headers: List[str], source_path: str, object_path: str) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def link_executable(self,
                        objects: List[str],
                        external_libraries: List[str],
                        external_libraries_interfaces: List[str],
                        executable: str,
                        symbols_table: str) -> Tuple[str, str, str]:
        raise NotImplementedError()

    @abstractmethod
    def link_library(self,
                     objects: List[str],
                     external_libraries: List[str],
                     external_libraries_interfaces: List[str],
                     library: str,
                     library_interface: str,
                     symbols_table: str) -> Tuple[str, str, str]:
        raise NotImplementedError()


class ICompilingStrategySupplier(ABC):
    @abstractmethod
    def get_type(self) -> CompilerType:
        raise NotImplementedError()

    @abstractmethod
    def get_yield_descriptor(self) -> IYieldDescriptor:
        raise NotImplementedError()

    @abstractmethod
    def instantiate(self, file_system: FileSystem, artifact_manifest: ArtifactManifest, project_structure: ProjectStructure) -> ICompilingStrategy:
        raise NotImplementedError()


class Compiler:
    def __init__(self, 
                 file_system: FileSystem, 
                 project_structure: ProjectStructure, 
                 artifact_manifest: ArtifactManifest, 
                 compiler_strategy: ICompilingStrategy):
        self.file_system = file_system
        self.project_structure = project_structure
        self.artifact_manifest = artifact_manifest
        self.compiler_strategy = compiler_strategy

    def compile_using_cache(self,
                            headers: List[str],
                            sources: List[str],
                            cache: Dict[str, Any],
                            progress_bar_supplier: ProgressBarSupplier) -> List[str]:
        new_cache        = {}
        objects          = []
        yield_descriptor = self.compiler_strategy.get_yield_descriptor()
        resolution       = progression_resolution(sources, cache)
        with progress_bar_supplier.create(resolution) as progress_bar:
            def hasher(source: str):
                progress_bar.update_summary(source)
                return hash_binary(self.compiler_strategy.preprocess(headers, source))
            for item in delta(sources, hasher, cache, new_cache):
                source_path = item.key
                object_path = self.project_structure.get_object_path(yield_descriptor, source_path)

                if item.delta_type in [DeltaType.Added, DeltaType.Modified]:
                    self.compiler_strategy.compile(headers, source_path, object_path)
                    objects.append(object_path)
                elif item.delta_type == DeltaType.UpToDate:
                    if not self.file_system.exists(object_path):
                        self.compiler_strategy.compile(headers, source_path, object_path)
                    objects.append(object_path)
                elif item.delta_type == DeltaType.Removed:
                    if self.file_system.exists(object_path):
                        self.file_system.remove_file(object_path)
                progress_bar.advance()
        cache.clear()
        cache.update(new_cache)
        return objects

    def link_executable_using_cache(self,
                                    is_test_executable: bool,
                                    objects: List[str],
                                    external_libraries: List[str],
                                    external_libraries_interfaces: List[str],
                                    cache: Dict[str, Any]) -> Tuple[str, str]:
        artifact_identifier = self.artifact_manifest.get_artifact_identifier() + ('.test' if is_test_executable else '')
        yield_descriptor    = self.compiler_strategy.get_yield_descriptor()
        executable          = self.project_structure.get_executable_path(yield_descriptor, artifact_identifier)
        symbols_table       = self.project_structure.get_symbols_table_path(yield_descriptor, artifact_identifier)
        self.compiler_strategy.link_executable(objects,
                                               external_libraries,
                                               external_libraries_interfaces,
                                               executable,
                                               symbols_table)
        if self.file_system.exists(symbols_table):
            return (executable, symbols_table)
        else:
            return (executable, None)

    def link_library_using_cache(self,
                                 objects: List[str],
                                 external_libraries: List[str],
                                 external_libraries_interfaces: List[str],
                                 cache: Dict[str, Any]) -> Tuple[str, str, str]:
        artifact_identifier = self.artifact_manifest.get_artifact_identifier()
        yield_descriptor    = self.compiler_strategy.get_yield_descriptor()
        library             = self.project_structure.get_library_path(yield_descriptor, artifact_identifier)
        library_interface   = self.project_structure.get_library_interface_path(yield_descriptor, artifact_identifier)
        symbols_table       = self.project_structure.get_symbols_table_path(yield_descriptor, artifact_identifier)
        self.compiler_strategy.link_library(objects,
                                            external_libraries,
                                            external_libraries_interfaces,
                                            library,
                                            library_interface,
                                            symbols_table)
        if self.file_system.exists(symbols_table):
            return (library, library_interface, symbols_table)
        else:
            return (library, library_interface, None)


def get_compiling_strategy_suppliers() -> List[ICompilingStrategySupplier]:
    suppliers = [klass() for klass in subclasses_of(ICompilingStrategySupplier)]
    duplicates = get_duplicates(suppliers, lambda a, b: a.get_type() == b.get_type())
    if duplicates:
        raise RuntimeError("multiple compilers defined with the same type "
                           f"'{suppliers[duplicates[0][0]].get_type()}'")
    return suppliers


def get_compiling_strategy_supplier(compiler_type: CompilerType) -> ICompilingStrategySupplier:
    suppliers = get_compiling_strategy_suppliers()
    matching  = [supplier for supplier in suppliers if supplier.get_type() == compiler_type]
    if not matching:
        raise RuntimeError(f"no compiler with type '{compiler_type}' was found")
    return matching[0]


def get_prefered_compiler(file_system: FileSystem) -> CompilerType:
    platform = file_system.get_platform()
    if platform == Platform.windows:
        return CompilerType.clang_cl
    elif platform == Platform.linux:
        return CompilerType.msvc
    elif platform == Platform.darwin:
        return CompilerType.clang
    else:
        None


def intantiate_compiler(file_system: FileSystem,
                        artifact_manifest: ArtifactManifest, 
                        project_structure: ProjectStructure,
                        compiler_name: CompilerType, 
                        fallback_compilers: List[CompilerType]) -> Compiler:
    manifest           = vars(artifact_manifest)
    final_manifest     = None
    compiling_strategy = None
    if compiler_name:
        manifest['compiler'] = compiler_name
        final_manifest       = ArtifactManifest(**manifest)
        supplier             = get_compiling_strategy_supplier(compiler_name)
        compiling_strategy   = supplier.instantiate(file_system, final_manifest, project_structure)
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
                supplier             = get_compiling_strategy_supplier(candidate)
                compiling_strategy   = supplier.instantiate(file_system, final_manifest, project_structure)
                break
            except CompilerInstantionError as e:
                messages.append(str(e))
    
        if compiling_strategy == None:
            raise NoSupportedCompilerFoundError(f"no suitable compiler was found:\n" + '\n'.join(messages))
    
    return Compiler(file_system, project_structure, final_manifest, compiling_strategy)
