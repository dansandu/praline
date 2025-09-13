from praline.common import CompilerType
from praline.common.exception import PralinefileValidationException
from praline.common.pralinefile.validation.validator import validator
from typing import Any, Dict


@validator
def validate_compilers(pralinefile: Dict[str, Any]):
    allowed_compilers = [compiler.value for compiler in CompilerType]
    compilers = pralinefile.get('compilers', allowed_compilers)
    if not isinstance(compilers, list):
        raise PralinefileValidationException(
            f"Pralinefile compilers {compilers} has invalid type '{type(compilers)}' -- type must be list")
    if not compilers:
        raise PralinefileValidationException("Pralinefile compilers field cannot be empty")
    converted_compilers = []
    for compiler in compilers:
        if compiler not in allowed_compilers:
            raise PralinefileValidationException(
                f"Pralinefile çompiler '{compiler}' is not recognized -- allowed compilers are {allowed_compilers}")
        converted_compilers.append(CompilerType(compiler))
    pralinefile['compilers'] = converted_compilers
