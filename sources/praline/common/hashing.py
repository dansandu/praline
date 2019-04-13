import hashlib
from praline.common.tracing import trace


@trace
def hash_file(path):
    hasher = hashlib.sha3_256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_binary(data):
    return hashlib.sha3_256(data).hexdigest()


@trace
def key_delta(keys, cache, key_hasher):
    new_cache, updated = {}, []
    removed = [k for k in cache if k not in keys]
    for key in keys:
        key_hash = key_hasher(key)
        if key not in cache or cache[key] != key_hash:
            updated.append(key)
        new_cache[key] = key_hash
    return (updated, removed, new_cache)
