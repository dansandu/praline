from dataclasses import dataclass
from datetime import datetime, timezone
from enum import auto, StrEnum
from typing import List, Callable, Tuple, TypeVar

import re


snapshot_datetime_format = "%Y%m%d%H%M%S%f"

farseer_file_extension = '.seer'

header_file_extension = '.hpp'

generated_header_file_extension = '.g.hpp'

source_file_extension = '.cpp'

generated_source_file_extension = '.g.cpp'

executable_source_file_name = 'executable.cpp'

package_extension = '.tar.gz'


class Architecture(StrEnum):
    arm = auto()
    x32 = auto()
    x64 = auto()


class ArtifactType(StrEnum):
    executable = auto()
    library    = auto()


class ExportedSymbols(StrEnum):
    explicit = auto()
    all      = auto()


class CompilerType(StrEnum):
    gcc      = auto()
    clang    = auto()
    clang_cl = auto()
    msvc     = auto()


class Mode(StrEnum):
    debug   = auto()
    release = auto()


class Platform(StrEnum):
    windows = auto()
    linux   = auto()
    darwin  = auto()


class DependencyScope(StrEnum):
    main = auto()
    test = auto()


@dataclass(eq=True)
class ArtifactPrefix:
    def __init__(self, prefix: str):
        if ':' in prefix:
            self.scope, self.prefix = prefix.split(':')
        else:
            self.scope = 'main'
            self.prefix = prefix

    def __str__(self):
        return f"{self.scope}:{self.prefix}"
    
    def __repr__(self):
        return f"{type(self).__name__}({self.__str__().__repr__()})"


@dataclass(frozen=True)
class ServiceConfiguration:
    executable_to_run: ArtifactPrefix
    library_to_load: ArtifactPrefix
    service_name: str


number_regex = r"0|[1-9]\d*"


organization_regex = r"[a-z][_a-z0-9]*[a-z0-9]"


artifact_regex = r"[a-z][_a-z0-9]*[a-z0-9]"


organization_pattern = re.compile(organization_regex)


artifact_pattern = re.compile(artifact_regex)


artifact_version_pattern = re.compile(
    fr"(?P<major>{number_regex})\."
    fr"(?P<minor>{number_regex})\."
    fr"(?P<patch>{number_regex})(?P<snapshot>.SNAPSHOT)?"
)


dependency_version_pattern = re.compile(
    fr"(?P<major>{number_regex})\."
    fr"(?P<minor_wildcard>\+)?(?P<minor>{number_regex})\."
    fr"(?P<patch_wildcard>\+)?(?P<patch>{number_regex})(?P<snapshot>.SNAPSHOT)?"
)


package_version_pattern = re.compile(
    fr"(?P<major>{number_regex})\."
    fr"(?P<minor>{number_regex})\."
    fr"(?P<patch>{number_regex})(?P<snapshot>.SNAPSHOT\d{{20}})?"
)


package_name_pattern = re.compile(
    f"(?P<organization>{organization_regex})-"
    f"(?P<artifact>{artifact_regex})-"
    f"(?P<architecture>{'|'.join(Architecture)})-"
    f"(?P<platform>{'|'.join(Platform)})-"
    f"(?P<compiler>{'|'.join(CompilerType)})-"
    f"(?P<mode>{'|'.join(Mode)})-"
    fr"(?P<major>{number_regex})\."
    fr"(?P<minor>{number_regex})\."
    fr"(?P<patch>{number_regex})(?P<snapshot>.SNAPSHOT\d{{20}})?\.tar\.gz"
)


@dataclass(frozen=True)
class ArtifactVersion:
    major: int
    minor: int
    patch: int
    snapshot: bool

    @classmethod
    def from_string(cls, string: str):
        match = artifact_version_pattern.fullmatch(string)
        if not match:
            raise ValueError(f"Could not match artifact version against '{string}'")
        return ArtifactVersion(int(match['major']), 
                               int(match['minor']),
                               int(match['patch']),
                               match['snapshot'] != None)

    def __str__(self) -> str:
        snapshot = '.SNAPSHOT' if self.snapshot else ''
        return f"{self.major}.{self.minor}.{self.patch}{snapshot}"


@dataclass(frozen=True, init=False)
class PackageVersion(ArtifactVersion):
    timestamp: datetime

    @classmethod
    def from_string(cls, string: str):
        match = package_version_pattern.fullmatch(string)
        if not match:
            raise ValueError(f"Could not match package version against '{string}'")
        snapshot = match['snapshot']
        timestamp = datetime(year=int(snapshot[9:13]), 
                             month=int(snapshot[13:15]), 
                             day=int(snapshot[15:17]),
                             hour=int(snapshot[17:19]),
                             minute=int(snapshot[19:21]),
                             second=int(snapshot[21:23]),
                             microsecond=int(snapshot[23:]),
                             tzinfo=timezone.utc) if snapshot else None
        return PackageVersion(int(match['major']), 
                              int(match['minor']), 
                              int(match['patch']), 
                              timestamp)

    def __init__(self, 
                 major: int, 
                 minor: int, 
                 patch: int,
                 timestamp: datetime):
        super().__init__(major, minor, patch, timestamp != None)
        object.__setattr__(self, 'timestamp', timestamp)

    def __str__(self) -> str:
        timestamp = self.timestamp.strftime(snapshot_datetime_format) if self.snapshot else ''
        return super().__str__() + timestamp
    
    def __lt__(self, other) -> bool:
        a = (self.major, self.minor, self.patch, not self.snapshot, self.timestamp)
        b = (other.major, other.minor, other.patch, not other.snapshot, other.timestamp)
        return a < b


@dataclass(frozen=True, init=False)
class DependencyVersion(ArtifactVersion):
    minor_wildcard: bool
    patch_wildcard: bool

    @classmethod
    def from_string(cls, string: str):
        match = dependency_version_pattern.fullmatch(string)
        if not match:
            raise ValueError(f"Could not match dependency version against '{string}'")
        return DependencyVersion(int(match['major']), 
                                 int(match['minor']), 
                                 match['minor_wildcard'] != None,
                                 int(match['patch']), 
                                 match['patch_wildcard'] != None, 
                                 match['snapshot'] != None)

    def __init__(self, 
                 major: int, 
                 minor: int, 
                 minor_wildcard: bool, 
                 patch: int, 
                 patch_wildcard: bool, 
                 snapshot: bool):
        super().__init__(major, minor, patch, snapshot)
        object.__setattr__(self, 'minor_wildcard', minor_wildcard)
        object.__setattr__(self, 'patch_wildcard', minor_wildcard or patch_wildcard)

    def __str__(self) -> str:
        minor = f"{'+' if self.minor_wildcard else ''}{self.minor}"
        patch = f"{'+' if self.patch_wildcard else ''}{self.patch}"
        snapshot = '.SNAPSHOT' if self.snapshot else ''
        return f"{self.major}.{minor}.{patch}{snapshot}"

    def matches(self, other: PackageVersion):
        return (
             self.major == other.major and
            (self.minor == other.minor or (self.minor_wildcard and self.minor <= other.minor)) and
            (self.patch == other.patch or (self.minor_wildcard and self.minor <  other.minor) 
                                       or (self.patch_wildcard and self.patch <= other.patch)) and
            (self.snapshot or not other.snapshot)
        )


@dataclass(frozen=True)
class ArtifactDependency:
    organization: str
    artifact: str
    version: DependencyVersion
    scope: DependencyScope


@dataclass(frozen=True)
class ArtifactManifest:
    organization: str
    artifact: str
    version: ArtifactVersion
    mode: Mode
    architecture: Architecture
    platform: Platform
    compiler: CompilerType
    exported_symbols: ExportedSymbols
    artifact_type: ArtifactType
    main_service: ServiceConfiguration
    test_service: ServiceConfiguration
    dependencies: List[ArtifactDependency]

    def get_artifact_identifier(self, 
                                dependency: ArtifactDependency = None, 
                                override_version: PackageVersion = None) -> str:
        target  = dependency       if dependency != None       else self
        version = override_version if override_version != None else target.version
        return (f"{target.organization}-{target.artifact}-{self.architecture}-{self.platform}-{self.compiler}-"
                f"{self.mode}-{version}")

    def get_package_file_name(self) -> str:
        return self.get_artifact_identifier() + package_extension

    def get_package_file_name_and_instantiate_snapshot(self) -> str:
        version = PackageVersion(self.version.major, 
                                 self.version.minor, 
                                 self.version.patch, 
                                 datetime.now(timezone.utc)) if self.version.snapshot else self.version

        return self.get_artifact_identifier(override_version=version) + package_extension

    def get_package_dependencies_file_names(self) -> List[str]:
        return [self.get_artifact_identifier(d) + package_extension for d in self.dependencies]

    def is_compatible(self, other) -> bool:
        return (
            self.mode == other.mode and
            self.architecture == other.architecture and
            self.platform == other.platform and
            self.compiler == other.compiler
        )


T = TypeVar('T')


def get_duplicates(array: List[T], predicate: Callable[[T, T], bool]) -> List[Tuple[int, int]]:
    return [(i, j) for i in range(len(array)) for j in range(i + 1, len(array)) if predicate(array[i], array[j])]
