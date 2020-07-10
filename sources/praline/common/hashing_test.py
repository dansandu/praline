from praline.common.hashing import hash_archive, hash_binary, hash_file, key_delta
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase
import pickle

class HashingTest(TestCase):
    def test_hash_file(self):
        directory   = 'my'
        file_name   = 'my/file'
        binary      = b'secretvalue'
        file_system = FileSystemMock({directory}, {file_name: binary})
        hash_value  = hash_file(file_system, file_name)

        self.assertEqual(hash_value, '3734c3023573321d4f7912cfeda42eb8fa74d1c3fb2f8f08147ac66ee14a5bba')

    def test_hash_binary(self):
        binary     = b'another_secret?!'
        hash_value = hash_binary(binary)

        self.assertEqual(hash_value, '62e404dfe29153db02cd492c1360eb1677a262ef1efe140083a7d9a0d893371e')

    def test_key_delta(self):
        keys       = ['a', 'b', 'c']
        key_hasher = lambda x: f'new_{x}'
        cache      = {'b': 'old_b', 'c': 'new_c', 'd': 'new_d'}
        updated, removed, new_cache = key_delta(keys, key_hasher, cache)

        self.assertEqual(updated, ['a', 'b'])
        self.assertEqual(removed, ['d'])
        self.assertEqual(new_cache, {'a': 'new_a', 'b': 'new_b', 'c': 'new_c'})

    def test_hash_archive(self):
        file_system = FileSystemMock(files={
            'archive.tar.gz': pickle.dumps({
                'path/to/file.txt': b'file-contents',
                'another_path/to/another_file.txt': b'another-file-contents'
            })
        })

        hash_code = hash_archive(file_system, 'archive.tar.gz')

        self.assertEqual(hash_code, 'de53e4f349df70285ef8acc48135f45d842be16094fbcd09bcea189b2adfb2c8')
