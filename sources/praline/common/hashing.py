from praline.common.file_system import FileSystem
from praline.common.tracing import trace

from dataclasses import dataclass
from enum import Enum
from hashlib import sha3_256
from typing import Any, Callable, Dict, List, Tuple, Generator


@trace
def hash_file(file_system: FileSystem, file_path: str) -> str:
    hasher = sha3_256()
    with file_system.open_file(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


@trace
def hash_archive(file_system: FileSystem, archive_path: str):
    hasher = sha3_256()
    with file_system.open_tarfile(archive_path, 'r:gz') as archive:
        for member in archive.getmembers():
            if member.isfile():
                hasher.update(member.name.encode('utf-8'))
                with archive.extractfile(member.name) as f:
                    for chunk in iter(lambda: f.read(4096), b''):
                        hasher.update(chunk)
    return hasher.hexdigest()


def hash_binary(data: bytes) -> str:
    return sha3_256(data).hexdigest()


@trace
def key_delta(keys: List[str], key_hasher: Callable[[str],str], cache: Dict[str, str]) -> Tuple[List[str], List[str], Dict[str, Any]]:
    updated   = []
    removed   = [key for key in cache if key not in keys]
    new_cache = {}
    for key in keys:
        key_hash = key_hasher(key)
        if key not in cache or cache[key] != key_hash:
            updated.append(key)
        new_cache[key] = key_hash
    return (updated, removed, new_cache)


class DeltaType(Enum):
    Added    = 0
    Modified = 1
    UpToDate = 2
    Removed  = 3


@dataclass(frozen=True)
class DeltaItem:
    key: str
    delta_type: DeltaType


@trace
def delta(keys: List[str], 
          key_hasher: Callable[[str],str], 
          cache: Dict[str, str], 
          new_cache: Dict[str, str]) -> Generator[DeltaItem, None, None]:
    for key in cache:
        if key not in keys:
            yield DeltaItem(key, DeltaType.Removed)
    
    for key in keys:
        new_cache[key] = key_hash = key_hasher(key)
        if key not in cache:
            yield DeltaItem(key, DeltaType.Added)
        elif cache[key] != key_hash:
            yield DeltaItem(key, DeltaType.Modified)
        else:
            yield DeltaItem(key, DeltaType.UpToDate)


def progression_resolution(keys: List[str], cache: Dict[str, str]):
    added_modified_or_update_to_date_count = len(keys)
    removed_count = 0
    for key in cache:
        if key not in keys:
            removed_count += 1
    return added_modified_or_update_to_date_count + removed_count
