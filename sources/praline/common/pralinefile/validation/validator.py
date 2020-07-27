from praline.common.tracing import trace
import functools


registered_validators = []


class PralinefileValidationError(Exception):
    pass


def validator(function):
    registered_validators.append(function)
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return wrapper


@trace(validators=[validator.__name__ for validator in registered_validators])
def validate(pralinefile):
    if not isinstance(pralinefile, dict):
        raise PralinefileValidationError(f"pralinefile has invalid type '{type(pralinefile)}' -- type must be dictionary")
    dependencies = pralinefile.get('dependencies', [])
    if not isinstance(dependencies, list):
        raise PralinefileValidationError(f"pralinefile dependencies {dependencies} has invalid type '{type(dependencies)}' -- type must be list")
    for dependency in dependencies:
        if not isinstance(pralinefile, dict):
            raise PralinefileValidationError(f"pralinefile dependency {dependency} has invalid type '{type(dependency)}' -- type must be dictionary")
    
    for validator in registered_validators:
        validator(pralinefile)
