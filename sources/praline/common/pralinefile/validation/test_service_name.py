from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


@validator
def validate_test_service_name(pralinefile: Dict[str, Any]):
    test_service_name = pralinefile.get('test_service_name', 'default')
    if not isinstance(test_service_name, str):
        raise PralinefileValidationError("Pralinefile test service name has invalid " +
                                         f"type '{type(test_service_name)}' -- type must be str")    
    pralinefile['test_service_name'] = test_service_name
