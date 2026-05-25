from praline.common import ArtifactManifest, CompilerType, Platform, get_duplicates
from praline.common.yield_descriptor import IYieldDescriptor
from praline.common.project_structure import ProjectStructure
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.file_system import FileSystem
from praline.common.hashing import DeltaItem, DeltaType, delta, hash_binary, progression_resolution
from praline.common.exception import CompilerInstantionException, NoSupportedCompilerFoundException
from praline.common.reflection import subclasses_of

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


logger = logging.getLogger(__name__)


class ICompilingStrategy(ABC):
    @abstractmethod
    def get_yield_descriptor(self) -> IYieldDescriptor:
        raise NotImplementedError()

    @abstractmethod
    def preprocess(self, headers: List[str], source_path: str, main_source: bool) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def compile(self, headers: List[str], source_path: str, object_path: str, main_source: bool) -> List[str]:
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
    def instantiate(
        self,
        file_system: FileSystem,
        configuration: Dict[str, Any],
        artifact_manifest: ArtifactManifest,
        project_structure: ProjectStructure
    ) -> ICompilingStrategy:
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

    def compile_sources_using_cache(self,
                                    headers: List[str],
                                    sources: List[str],
                                    cache: Dict[str, Any],
                                    progress_bar_supplier: ProgressBarSupplier,
                                    main_sources: bool) -> List[str]:
        new_cache  = {}
        objects    = []
        resolution = progression_resolution(sources, cache)

        yield_descriptor = self.compiler_strategy.get_yield_descriptor()

        object_path_supplier = self.project_structure.get_main_object_path if main_sources else self.project_structure.get_test_object_path

        with progress_bar_supplier.create(resolution) as progress_bar:
            def hasher(source_path: str):
                progress_bar.update_description(source_path)
                return hash_binary(self.compiler_strategy.preprocess(headers, source_path, main_sources))

            def consumer(item: DeltaItem):
                source_path = item.key
                object_path = object_path_supplier(yield_descriptor, source_path)

                if item.delta_type in [DeltaType.Added, DeltaType.Modified]:
                    logger.debug(f"Source '{source_path}' has been changed and will be compiled")
                    self.compiler_strategy.compile(headers, source_path, object_path, main_sources)
                    objects.append(object_path)

                elif item.delta_type == DeltaType.UpToDate:
                    logger.debug(f"Source '{source_path}' is up-to-date and will not be recompiled")
                    if not self.file_system.exists(object_path):
                        self.compiler_strategy.compile(headers, source_path, object_path, main_sources)

                    objects.append(object_path)
                elif item.delta_type == DeltaType.Removed:
                    logger.debug(f"Source '{source_path}' has been removed")
                    if self.file_system.exists(object_path):
                        self.file_system.remove_file(object_path)

                progress_bar.advance()

            delta(sources, hasher, cache, new_cache, consumer)

        cache.clear()
        cache.update(new_cache)
        return objects

    def link_executable_using_cache(self,
                                    objects: List[str],
                                    external_libraries: List[str],
                                    external_libraries_interfaces: List[str],
                                    cache: Dict[str, Any],
                                    progress_bar_supplier: ProgressBarSupplier,
                                    main_executable: bool) -> Tuple[str, str]:
        artifact_identifier = self.artifact_manifest.get_artifact_identifier()
        if not main_executable:
            artifact_identifier += '.test'

        yield_descriptor = self.compiler_strategy.get_yield_descriptor()

        executable_path, symbols_table_path = self.project_structure.get_executable_and_symbols_table_path(yield_descriptor, artifact_identifier)

        with progress_bar_supplier.create(resolution=1) as progress_bar:
            progress_bar.update_description(executable_path)
            self.compiler_strategy.link_executable(objects, external_libraries, external_libraries_interfaces, executable_path, symbols_table_path)
            progress_bar.advance()

        if self.file_system.exists(symbols_table_path):
            return (executable_path, symbols_table_path)
        else:
            return (executable_path, None)

    def link_library_using_cache(self,
                                 objects: List[str],
                                 external_libraries: List[str],
                                 external_libraries_interfaces: List[str],
                                 cache: Dict[str, Any],
                                 progress_bar_supplier: ProgressBarSupplier,
                                 test_library: bool = False) -> Tuple[str, str, str]:
        artifact_identifier    = self.artifact_manifest.get_artifact_identifier()

        if test_library:
            artifact_identifier += '.test'

        yield_descriptor = self.compiler_strategy.get_yield_descriptor()

        library_path, symbols_table_path = self.project_structure.get_library_and_symbols_table_path(yield_descriptor, artifact_identifier)

        library_interface_path = self.project_structure.get_library_interface_path(yield_descriptor, artifact_identifier)

        with progress_bar_supplier.create(resolution=1) as progress_bar:
            progress_bar.update_description(library_path)
            self.compiler_strategy.link_library(objects,
                                                external_libraries,
                                                external_libraries_interfaces,
                                                library_path,
                                                library_interface_path,
                                                symbols_table_path)
            progress_bar.advance()

        if self.file_system.exists(symbols_table_path):
            return (library_path, library_interface_path, symbols_table_path)
        else:
            return (library_path, library_interface_path, None)


def get_compiling_strategy_suppliers() -> List[ICompilingStrategySupplier]:
    suppliers = [klass() for klass in subclasses_of(ICompilingStrategySupplier)]
    duplicates = get_duplicates(suppliers, lambda a, b: a.get_type() == b.get_type())
    if duplicates:
        raise RuntimeError(f"Multiple compilers defined with the same type '{suppliers[duplicates[0][0]].get_type()}'")
    return suppliers


def get_compiling_strategy_supplier(compiler_type: CompilerType) -> ICompilingStrategySupplier:
    suppliers = get_compiling_strategy_suppliers()
    matching  = [supplier for supplier in suppliers if supplier.get_type() == compiler_type]
    if not matching:
        raise RuntimeError(f"No compiler with type '{compiler_type}' was found")
    return matching[0]


def get_preferred_compiler(file_system: FileSystem) -> CompilerType:
    platform = file_system.get_platform()
    if platform == Platform.windows:
        return CompilerType.msvc
    elif platform == Platform.linux:
        return CompilerType.gcc
    elif platform == Platform.darwin:
        return CompilerType.clang
    else:
        None


def intantiate_compiler(file_system: FileSystem,
                        configuration: Dict[str, Any],
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
        compiling_strategy   = supplier.instantiate(file_system, configuration, final_manifest, project_structure)
    else:
        prefered_compiler = get_preferred_compiler(file_system)
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
                compiling_strategy   = supplier.instantiate(file_system, configuration, final_manifest, project_structure)
                break
            except CompilerInstantionException as e:
                messages.append(str(e))

        if compiling_strategy == None:
            raise NoSupportedCompilerFoundException(f"No suitable compiler was found:\n" + '\n'.join(messages))

    return Compiler(file_system, project_structure, final_manifest, compiling_strategy)
