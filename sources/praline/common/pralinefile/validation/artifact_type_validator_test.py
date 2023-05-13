from praline.common.pralinefile.validation.artifact_type_validator import validate_artifact_type
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class ArtifactTypeValidatorTest(TestCase):
    def test_valid_executable(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'artifact_type': 'executable',
            'version': '1.5.0'
        }
        validate_artifact_type(pralinefile)

    def test_valid_library(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'artifact_type': 'library',
            'version': '1.5.0'
        }
        validate_artifact_type(pralinefile)

    def test_invalid_artifact_type(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'artifact_type': ['executable'],
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_artifact_type, pralinefile)

    def test_invalid_artifact_type_value(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'artifact_type': 'lib',
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_artifact_type, pralinefile)

    def test_default_value(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.5.0'
        }
        
        validate_artifact_type(pralinefile)
