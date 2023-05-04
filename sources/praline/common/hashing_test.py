from praline.common.hashing import (DeltaItem, DeltaType, delta, hash_archive, hash_binary, hash_file, 
                                    progression_resolution)
from praline.common.testing.file_system_mock import ArchiveMock, FileSystemMock

from os.path import join
from unittest import TestCase


class HashingTest(TestCase):
    def test_hash_file(self):
        directory   = 'my'
        file_name   = join('my', 'file')
        binary      = b'secretvalue'
        file_system = FileSystemMock(directories={directory}, files={file_name: binary})
        hash_value  = hash_file(file_system, file_name)

        self.assertEqual(hash_value, '3734c3023573321d4f7912cfeda42eb8fa74d1c3fb2f8f08147ac66ee14a5bba')

    def test_hash_binary(self):
        binary     = b'another_secret?!'
        hash_value = hash_binary(binary)

        self.assertEqual(hash_value, '62e404dfe29153db02cd492c1360eb1677a262ef1efe140083a7d9a0d893371e')


    def test_hash_archive(self):
        file_system = FileSystemMock(
            files={
                'archive.tar.gz': ArchiveMock({
                    'file.txt': b'file-contents',
                    'another_file.txt': b'another-file-contents'
                })
            }
        )

        hash_code = hash_archive(file_system, 'archive.tar.gz')

        self.assertEqual(hash_code, '2e4da9991e3832d955681d3d99599f1e44dfe266e5709d4c9561b4a813902313')

    def test_delta(self):
        keys       = ['a', 'b', 'c']
        key_hasher = lambda x: f'new_{x}'
        cache      = {'b': 'old_b', 'c': 'new_c', 'd': 'new_d'}
        new_cache  = {}
        deltas = {d for d in delta(keys, key_hasher, cache, new_cache)}

        expected_deltas = set({
            DeltaItem('a', DeltaType.Added),
            DeltaItem('b', DeltaType.Modified),
            DeltaItem('c', DeltaType.UpToDate),
            DeltaItem('d', DeltaType.Removed),
        })

        self.assertEqual(deltas, expected_deltas)

        expected_new_cache = {'a': 'new_a', 'b': 'new_b', 'c': 'new_c'}

        self.assertEqual(new_cache, expected_new_cache)

    def test_progression_resolution(self):
        keys  = ['a', 'b']
        cache = {'b': 'b-hash', 'c': 'c-hash'}

        resolution = progression_resolution(keys, cache)

        self.assertEqual(resolution, 3)
