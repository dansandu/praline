from praline.common.exception import PralinefileValidationException
import functools


registered_validators = []


def validator(function):
    registered_validators.append(function)
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return wrapper


def validate(pralinefile):
    if not isinstance(pralinefile, dict):
        raise PralinefileValidationException(
            f"Pralinefile has invalid type '{type(pralinefile)}' -- type must be dictionary")
    for validator in registered_validators:
        validator(pralinefile)
