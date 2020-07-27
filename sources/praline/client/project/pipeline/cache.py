import pickle
from logging import getLogger
from praline.common.file_system import FileSystem
from typing import Any, Dict


logger = getLogger(__name__)


class Cache:
    path       : str
    file_system: FileSystem
    cache      : Dict[str, Any]

    def __init__(self, file_system: FileSystem, path: str):
        self.path = path
        self.file_system = file_system
        self.cache = {}
    
    def __enter__(self):
        if self.file_system.exists(self.path):
            with self.file_system.open_file(self.path, 'rb') as handle:
                self.cache = pickle.load(handle)
        logger.debug(f"read cache={self.cache}")
        return self

    def __setitem__(self, key: str, value) -> None:
        self.cache[key] = value

    def __getitem__(self, key: str):
        return self.cache[key]

    def get(self, key: str, default=None):
        return self.cache.get(key, default)

    def __exit__(self, type, value, traceback):
        logger.debug(f"writing cache={self.cache}")
        self.file_system.create_file_if_missing(self.path)
        with self.file_system.open_file(self.path, 'wb') as handle:
            pickle.dump(self.cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
