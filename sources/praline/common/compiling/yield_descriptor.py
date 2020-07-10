from abc import ABC, abstractmethod


class YieldDescriptor(ABC):
    @abstractmethod
    def get_object(self, sources_root: str, objects_root: str, source: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_executable(self, executables_root: str, name: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_library(self, libraries_root: str, name: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_library_interface(self, libraries_interfaces_root: str, name: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_symbols_table(self, symbols_tables_root: str, name: str) -> str:
        raise NotImplementedError()
