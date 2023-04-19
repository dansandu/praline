from praline.common.pralinefile.validation.artifact_validator import validate_artifact
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class ArtifactValidatorTest(TestCase):
    def test_valid_artifact(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'my_artifact',
            'version': '1.5.0'
        }

        validate_artifact(pralinefile)
    
    def test_invalid_artifact_with_trailing_underscore(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'my_artifact_',
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_artifact, pralinefile)

    def test_invalid_artifact_with_underscore_prefix(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': '_my_artifact',
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_artifact, pralinefile)

    def test_invalid_artifact_with_numbers(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': '3my_artifact',
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_artifact, pralinefile)
