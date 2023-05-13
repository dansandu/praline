from praline.common import ExportedSymbols
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_exported_symbols(pralinefile: Dict[str, Any]):
    allowed_exported_symbols = [exported.value for exported in ExportedSymbols]
    exported_symbols = pralinefile.get('exported_symbols', ExportedSymbols.explicit.value)
    if not isinstance(exported_symbols, str):
        raise PralinefileValidationError(
            f"Pralinefile exported_symbols field has invalid type '{type(exported_symbols)}' -- type must be str")
    if exported_symbols not in allowed_exported_symbols:
        raise PralinefileValidationError(
                f"Pralinefile exported_symbols '{exported_symbols}' is not recognized -- allowed exported_symbols "
                f"are {allowed_exported_symbols}")
    pralinefile['exported_symbols'] = ExportedSymbols(exported_symbols)
