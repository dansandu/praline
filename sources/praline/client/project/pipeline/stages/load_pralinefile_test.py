from praline.client.project.pipeline.stages.load_pralinefile import load_pralinefile, NoMatchingCompilerFoundError, UnsupportedArchitectureError, UnsupportedPlatformError
from praline.common.testing.file_system_mock import FileSystemMock
from unittest import TestCase


working_directory = 'my/project'


def gcc_which(thing: str) -> str:
    if thing == 'g++':
        return '/gcc/g++'


pralinefile = {
    'my/project/Pralinefile': b"""\
        organization: my_organization
        artifact: my_artifact
        version: 1.2.5
        """
}


program_arguments = {
    'global': {
        'release'      : False,
        'logging_level': 4
    }
}


class LoadPralinefileStageTest(TestCase):
    def test_load_pralinefile_stage_with_pralinefile(self):
        file_system = FileSystemMock({working_directory}, pralinefile, working_directory=working_directory, on_which=gcc_which)

        resources = {}

        load_pralinefile(file_system, resources, None, program_arguments, None, None)

        self.assertEqual(resources['project_directory'], file_system.get_working_directory())

        self.assertIn('pralinefile', resources)

        self.assertIn('compiler', resources)

    def test_load_pralinefile_stage_without_pralinefile(self):
        file_system = FileSystemMock({working_directory}, working_directory=working_directory, on_which=gcc_which)

        resources = {}

        self.assertRaises(FileNotFoundError, load_pralinefile, file_system, resources, None, program_arguments, None, None)

    def test_load_pralinefile_stage_with_invalid_architecture(self):
        file_system = FileSystemMock({working_directory}, pralinefile, working_directory=working_directory, architecture='cheese', on_which=gcc_which)

        resources = {}

        self.assertRaises(UnsupportedArchitectureError, load_pralinefile, file_system, resources, None, program_arguments, None, None)

    def test_load_pralinefile_stage_with_invalid_platform(self):
        file_system = FileSystemMock({working_directory}, pralinefile, working_directory=working_directory, platform='cake', on_which=gcc_which)

        resources = {}

        self.assertRaises(UnsupportedPlatformError, load_pralinefile, file_system, resources, None, program_arguments, None, None)

    def test_load_pralinefile_stage_with_no_matching_compiler(self):
        file_system = FileSystemMock({working_directory}, pralinefile, working_directory=working_directory)

        resources = {}

        self.assertRaises(NoMatchingCompilerFoundError, load_pralinefile, file_system, resources, None, program_arguments, None, None)
