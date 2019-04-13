import pickle
from logging import getLogger
from praline.common.file_system import create_file_if_missing, exists

logger = getLogger(__name__)


class Cache:
    def __init__(self, path):
        self.cache = {}
        self.path = path
    
    def __enter__(self):
        if exists(self.path):
            with open(self.path, 'rb') as handle:
                self.cache = pickle.load(handle)
        logger.debug(f"read cache={self.cache}")
        return self

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __getitem__(self, key):
        return self.cache[key]

    def get(self, key, default=None):
        return self.cache.get(key, default)

    def __exit__(self, type, value, traceback):
        logger.debug(f"writing cache={self.cache}")
        create_file_if_missing(self.path)
        with open(self.path, 'wb') as handle:
            pickle.dump(self.cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
