from abc import ABC, abstractmethod
from praline.common.file_system import create_directory_if_missing, directory_name, exists, join, relative_path, remove, separator, which
from praline.common.hashing import hash_binary, key_delta, hash_file
from praline.common.reflection import subclasses_of


class Compiler(ABC):
    @abstractmethod
    def name(self):
        raise NotImplementedError()

    @abstractmethod
    def executable(self):
        raise NotImplementedError()

    @abstractmethod
    def allowed_platforms(self):
        raise NotImplementedError()

    @abstractmethod
    def preprocess(self, source, header_roots, headers):
        raise NotImplementedError()

    @abstractmethod
    def compile(self, object_, source, headers_roots, headers):
        raise NotImplementedError()
    
    @abstractmethod
    def link_executable(self, executable, objects, external_libraries):
        raise NotImplementedError()

    @abstractmethod
    def link_library(self, library, objects, external_libraries):
        raise NotImplementedError()


def compile_using_cache(compiler, objects_root, sources_root, sources, headers_roots, headers, cache):
    create_directory_if_missing(objects_root)
    def translation_unit_hasher(source):
        return hash_binary(compiler.preprocess(source, headers_roots, headers))

    def get_object(source):
        name = relative_path(source, sources_root).replace(separator, '-').replace('.cpp', '.o')
        return join(objects_root, name)

    updated, removed, new_cache = key_delta(sources, cache, key_hasher=translation_unit_hasher)
    objects = []
    for source in updated:
        object_ = get_object(source)
        compiler.compile(source, object_, headers_roots, headers)
    for source in removed:
        remove(get_object(source))
    for source in sources:
        object_ = get_object(source)
        if not exists(object_):
            compiler.compile(source, object_, headers_roots, headers)
        objects.append(object_)
    cache.clear()
    cache.update(new_cache)
    return objects


def link_executable_using_cache(compiler, executable, objects, external_libraries, cache):
    create_directory_if_missing(directory_name(executable))
    cache['input'] = input_ = cache.get('input', {})
    output = cache.get('output')
    updated, removed, new_cache = key_delta(objects + external_libraries, input_, hash_file)
    if updated or removed or not exists(executable):
        if output:
            remove(output)
        compiler.link_executable(executable, objects, external_libraries)
    cache['input'] = new_cache
    cache['output'] = executable


def link_library_using_cache(compiler, library, objects, external_libraries, cache):
    create_directory_if_missing(directory_name(library))
    cache['input'] = input_ = cache.get('input', {})
    output = cache.get('output')
    updated, removed, new_cache = key_delta(objects + external_libraries, input_, hash_file)
    if updated or removed or not exists(library):
        if output:
            remove(output)
        compiler.link_library(library, objects, external_libraries)
    cache['input'] = new_cache
    cache['output'] = library


def get_compilers():
    compilers = [compilerClass() for compilerClass in subclasses_of(Compiler)]
    duplicates = [(i, j) for i in range(len(compilers)) for j in range(i + 1, len(compilers)) if compilers[i].name() == compilers[j].name()]
    if duplicates:
        raise RuntimeError(f"multiple compilers defined with the same name '{compilers[duplicates[0][0]].name}'")
    return compilers
