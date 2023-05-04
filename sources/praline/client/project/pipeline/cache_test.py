from praline.client.project.pipeline.cache import Cache
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase

import pickle
from os.path import join


class InterruptCacheWritingError(Exception):
    pass


class CacheTest(TestCase):
    def test_key_retrieval_with_fresh_cache(self):
        file_name   = 'my_file'
        file_system = FileSystemMock()

        with Cache(file_system, file_name) as cache:
            self.assertRaises(KeyError, cache.__getitem__, 'myKey')
    
    def test_key_retrieval_with_existing_cache(self):
        directory   = 'my'
        file_name   = join('my', 'cache')
        data        = pickle.dumps({'myKey': 38}, protocol=pickle.HIGHEST_PROTOCOL)
        file_system = FileSystemMock(
            directories={
                directory
            }, 
            files={
                file_name: data
            }
        )

        with Cache(file_system, file_name) as cache:
            self.assertEqual(cache['myKey'], 38)

        with Cache(file_system, file_name) as cache:
            self.assertEqual(cache['myKey'], 38)

    def test_key_adding_with_fresh_cache(self):
        file_name   = join('my', 'cache')
        file_system = FileSystemMock()

        with Cache(file_system, file_name) as cache:
            cache['dragon'] = 'blue'
            self.assertEqual(cache['dragon'], 'blue')

        with Cache(file_system, file_name) as cache:
            cache['cat'] = 'black'
            self.assertEqual(cache['cat'], 'black')
            self.assertEqual(cache['dragon'], 'blue')

    def test_key_adding_with_existing_cache(self):
        directory   = 'my'
        file_name   = join('my', 'cache')
        data        = pickle.dumps({'someKey': 'someValue'}, protocol=pickle.HIGHEST_PROTOCOL)
        file_system = FileSystemMock(
            directories={
                directory
            }, 
            files={
                file_name: data
            }
        )

        with Cache(file_system, file_name) as cache:
            cache['otherKey'] = 'otherValue'
            self.assertEqual(cache['someKey'], 'someValue')
            self.assertEqual(cache['otherKey'], 'otherValue')

        with Cache(file_system, file_name) as cache:
            self.assertEqual(cache['someKey'], 'someValue')
            self.assertEqual(cache['otherKey'], 'otherValue')
        
    def test_key_update_with_existing_cache(self):
        directory   = 'my'
        file_name   = join('my', 'cache')
        data        = pickle.dumps({'car': 'red'}, protocol=pickle.HIGHEST_PROTOCOL)
        file_system = FileSystemMock(
            directories={
                directory
            },
            files={
                file_name: data
            }
        )

        with Cache(file_system, file_name) as cache:
            cache['car'] = 'yellow'
            self.assertEqual(cache['car'], 'yellow')

        with Cache(file_system, file_name) as cache:
            self.assertEqual(cache['car'], 'yellow')

    def test_key_retrieval_with_default(self):
        directory   = 'my'
        file_name   = join('my', 'cache')
        data        = pickle.dumps({'bike': 'green'}, protocol=pickle.HIGHEST_PROTOCOL)
        file_system = FileSystemMock(
            directories={
                directory
            },
            files={
                file_name: data
            }
        )

        with Cache(file_system, file_name) as cache:
            self.assertEqual(cache.get('bike'), 'green')
            self.assertEqual(cache.get('bicycle'), None)
            self.assertEqual(cache.get('scooter', 'white'), 'white')

    def test_previously_added_keys_are_preserved_on_exception(self):
        file_name   = join('my', 'cache')
        file_system = FileSystemMock()

        try:
            with Cache(file_system, file_name) as cache:
                cache['whale'] = 'blue'
                cache['dog']   = 'grey'

                raise InterruptCacheWritingError()
        except InterruptCacheWritingError:
            with Cache(file_system, file_name) as cache:
                self.assertEqual(cache.get('whale'), 'blue')
                self.assertEqual(cache.get('dog'), 'grey')
