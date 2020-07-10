from praline.common.pralinefile.validation.modes_validator import validate_mode
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class ModeValidatorTest(TestCase):
    def test_valid_modes(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'modes': ['debug', 'release'],
            'version': '1.5.0'
        }
        validate_mode(pralinefile)

    def test_invalid_modes_type(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'modes': 'debug',
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_mode, pralinefile)

    def test_invalid_modes_value(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'modes': ['debugrelease'],
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_mode, pralinefile)

    def test_invalid_empty_modes(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'modes': [],
            'version': '1.5.0'
        }
        
        self.assertRaises(PralinefileValidationError, validate_mode, pralinefile)

    def test_valid_unset_modes_field(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.5.0'
        }
        
        validate_mode(pralinefile)
