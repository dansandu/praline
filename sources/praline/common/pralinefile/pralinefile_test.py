from praline.common.pralinefile import pralinefile_from_path, pralinefile_from_reader
from praline.common.constants import allowed_platforms, allowed_architectures, allowed_compilers, allowed_modes
from praline.common.testing.file_system_mock import FileSystemMock 
from io import StringIO
from textwrap import dedent
from unittest import TestCase

class PralinefileTest(TestCase):
    def test_pralinefile_from_path(self):
        file_system = FileSystemMock(files={'Pralinefile': b"""\
            organization: another_organization
            artifact: another_artifact
            compilers: [gcc]
            modes: [release]
            version: 7.7.7
            dependencies:
            - organization: org
              artifact: art
              scope: test
              version: 3.+5.+5
            """})

        expected_pralinefile = {
            'organization': 'another_organization',
            'artifact': 'another_artifact',
            'platforms': allowed_platforms,
            'architectures': allowed_architectures,
            'compilers': ['gcc'],
            'modes': ['release'],
            'version': '7.7.7',
            'dependencies': [
                {
                    'organization': 'org',
                    'artifact': 'art',
                    'scope': 'test',
                    'version': '3.+5.+5'
                }
            ]
        }

        actual_pralinefile = pralinefile_from_path(file_system, 'Pralinefile')

        self.assertEqual(actual_pralinefile, expected_pralinefile)


    def test_pralinefile_from_reader(self):
        reader = StringIO(dedent("""\
            organization: the_organization
            artifact: the_artifact
            version: 1.0.0
            dependencies:
            - organization: dep_organization
              artifact: dep_artifact
              version: 5.1.0
            """))

        expected_pralinefile = {
            'organization': 'the_organization',
            'artifact': 'the_artifact',
            'platforms': allowed_platforms,
            'architectures': allowed_architectures,
            'compilers': allowed_compilers,
            'modes': allowed_modes,
            'version': '1.0.0',
            'dependencies': [
                {
                    'organization': 'dep_organization',
                    'artifact': 'dep_artifact',
                    'scope': 'main',
                    'version': '5.1.0'
                }
            ]
        }

        actual_pralinefile = pralinefile_from_reader(reader)

        self.assertEqual(actual_pralinefile, expected_pralinefile)
