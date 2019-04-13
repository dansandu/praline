from praline.common.pralinefile.constants import organization_pattern
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator


def validate_root_organization(pralinefile):
    organization = pralinefile['organization']
    if not isinstance(organization, str):
        raise PralinefileValidationError(f"pralinefile organization '{organization}' has invalid type '{type(organization)}' -- type must be str")
    if not organization_pattern.fullmatch(organization):
        raise PralinefileValidationError(f"pralinefile organization '{organization}' is not valid -- organization should contain lowercase words separated by underscores")


def validate_dependencies_organization(pralinefile):
    for dependency in pralinefile['dependencies']:
        validate_root_organization(dependency)


@validator
def validate_organization(pralinefile):
    validate_root_organization(pralinefile)
    validate_dependencies_organization(pralinefile)
