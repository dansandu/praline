from praline.common import ArtifactPrefix, source_file_extension
from praline.common.file_system import get_separator
from abc import ABC, abstractmethod


class IYieldDescriptor(ABC):
    @abstractmethod
    def get_object(self, source_relative_path: str) -> str:
        return source_relative_path.replace(get_separator(), '-')[:-len(source_file_extension)]

    @abstractmethod
    def get_executable_and_symbols_table(self, artifact_identifier: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_library_and_symbols_table(self, artifact_identifier: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_library_interface(self, artifact_identifier: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_executable_prefix(self, artifact_prefix: ArtifactPrefix) -> ArtifactPrefix:
        raise NotImplementedError()

    @abstractmethod
    def get_library_prefix(self, artifact_prefix: ArtifactPrefix) -> ArtifactPrefix:
        raise NotImplementedError()

