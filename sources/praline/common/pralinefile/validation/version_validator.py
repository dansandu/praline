from praline.common.pralinefile.constants import fixed_version_pattern, wildcard_version_pattern
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator


def validate_root_version(pralinefile, pattern):
    version = pralinefile['version']
    if not isinstance(version, str):
        raise PralinefileValidationError(f"pralinefile version '{version}' has invalid type '{type(version)}' -- type must be str")
    if not pattern.fullmatch(version):
        raise PralinefileValidationError(f"pralinefile version '{version}' is not valid")


def validate_dependencies_version(pralinefile):
    for dependency in pralinefile['dependencies']:
        validate_root_version(dependency, wildcard_version_pattern)


@validator
def validate_version(pralinefile):
    validate_root_version(pralinefile, fixed_version_pattern)
    validate_dependencies_version(pralinefile)
