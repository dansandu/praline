from praline.common.file_system import FileSystem

import logging
import pickle
from typing import Any, Dict


logger = logging.getLogger(__name__)


class FileCache:
    file_system: FileSystem
    file_path  : str
    cache      : Dict[str, Any]
    active     : bool

    def __init__(self, file_system: FileSystem, file_path: str, active: bool):
        self.file_system = file_system
        self.file_path = file_path
        self.cache = {}
        self.active = active
    
    def __enter__(self):
        if self.active and self.file_system.exists(self.file_path):
            logger.debug(f"Reading cache from file '{self.file_path}'")
            with self.file_system.open_file(self.file_path, 'rb') as handle:
                self.cache = pickle.load(handle)
        return self

    def __setitem__(self, key: str, value) -> None:
        self.cache[key] = value

    def __getitem__(self, key: str):
        return self.cache[key]

    def get(self, key: str, default=None):
        return self.cache.get(key, default)

    def __exit__(self, type, value, traceback):
        if self.active:
            logger.debug(f"Writing cache to file '{self.file_path}'")
            self.file_system.create_file_if_missing(self.file_path)
            with self.file_system.open_file(self.file_path, 'wb') as handle:
                pickle.dump(self.cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
