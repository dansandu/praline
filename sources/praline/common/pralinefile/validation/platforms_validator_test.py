from praline.common.pralinefile.validation.platforms_validator import validate_platforms
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class PlatformsValidatorTest(TestCase):
    def test_valid_platforms(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'platforms': ['windows', 'darwin', 'linux'],
            'version': '1.5.0'
        }
        validate_platforms(pralinefile)

    def test_invalid_platforms_value(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'platforms': ['tomato'],
            'version': '1.5.0'
        }
        
        self.assertRaises(PralinefileValidationError, validate_platforms, pralinefile)

    def test_invalid_platforms_type(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'platforms': 'linux',
            'version': '1.5.0'
        }
        
        self.assertRaises(PralinefileValidationError, validate_platforms, pralinefile)

    def test_invalid_empty_platforms(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'platforms': [],
            'version': '1.5.0'
        }
        
        self.assertRaises(PralinefileValidationError, validate_platforms, pralinefile)

    def test_valid_unset_platforms_field(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.5.0'
        }
        
        validate_platforms(pralinefile)
