from praline.common import (
    Architecture, ArtifactVersion, ArtifactType, Compiler, DependencyScope, DependencyVersion, ExportedSymbols, 
    Mode, Platform
)
from praline.common.pralinefile import read_pralinefile
from praline.common.testing.file_system_mock import FileSystemMock 

from unittest import TestCase


class PralinefileTest(TestCase):
    def test_pralinefile_with_mandatory_fields_only(self):
        file_system = FileSystemMock(
            files={
                'Pralinefile': b"""\
                    organization: another_organization
                    artifact: another_artifact
                    version: 7.3.4.SNAPSHOT
                    dependencies:
                    - organization: org
                      artifact: art
                      version: 3.+5.+5
                    """
            }
        )

        expected_pralinefile = {
            'organization': 'another_organization',
            'artifact': 'another_artifact',
            'version': ArtifactVersion.from_string('7.3.4.SNAPSHOT'),
            'platforms': list(Platform),
            'architectures': list(Architecture),
            'modes': list(Mode),
            'compilers': list(Compiler),
            'exported_symbols': ExportedSymbols.explicit,
            'artifact_type': ArtifactType.library,
            'dependencies': [
                {
                    'organization': 'org',
                    'artifact': 'art',
                    'scope': DependencyScope.main,
                    'version': DependencyVersion.from_string('3.+5.+5')
                }
            ]
        }

        actual_pralinefile = read_pralinefile(file_system, 'Pralinefile')

        self.assertEqual(actual_pralinefile, expected_pralinefile)


    def test_pralinefile_with_all_fields(self):
        file_system = FileSystemMock(
            files={
                'Pralinefile': b"""\
                    organization: another_organization2
                    artifact: another_artifact2
                    version: 7.3.4
                    architectures: [arm, x32]
                    platforms: [linux, windows]
                    modes: [release]
                    compilers: [gcc, clang]
                    exported_symbols: all
                    artifact_type: executable
                    dependencies:
                    - organization: org
                      artifact: art
                      scope: test
                      version: 3.+5.+5.SNAPSHOT
                    """
            }
        )

        expected_pralinefile = {
            'organization': 'another_organization2',
            'artifact': 'another_artifact2',
            'version': ArtifactVersion.from_string('7.3.4'),
            'platforms': [Platform.linux, Platform.windows],
            'architectures': [Architecture.arm, Architecture.x32],
            'modes': [Mode.release],
            'compilers': [Compiler.gcc, Compiler.clang],
            'exported_symbols': ExportedSymbols.all,
            'artifact_type': ArtifactType.executable,
            'dependencies': [
                {
                    'organization': 'org',
                    'artifact': 'art',
                    'scope': DependencyScope.test,
                    'version': DependencyVersion.from_string('3.+5.+5.SNAPSHOT')
                }
            ]
        }

        actual_pralinefile = read_pralinefile(file_system, 'Pralinefile')

        self.assertEqual(actual_pralinefile, expected_pralinefile)
