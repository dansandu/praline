from praline.common.pralinefile.validation.exported_symbols_validator import validate_exported_symbols
from praline.common.pralinefile.validation.validator import PralinefileValidationError
from unittest import TestCase


class ExportedSymbolsValidatorTest(TestCase):
    def test_valid_exported_symbols(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'exported_symbols': 'all',
            'version': '1.5.0'
        }
        validate_exported_symbols(pralinefile)

    def test_invalid_exported_symbols_type(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'exported_symbols': ['all', 'explicit'],
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_exported_symbols, pralinefile)

    def test_invalid_exported_symbols_value(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'exported_symbols': 'implicit',
            'version': '1.5.0'
        }

        self.assertRaises(PralinefileValidationError, validate_exported_symbols, pralinefile)

    def test_default_value(self):
        pralinefile = {
            'organization': 'candyco',
            'artifact': 'chocolaterie',
            'version': '1.5.0'
        }
        
        validate_exported_symbols(pralinefile)
