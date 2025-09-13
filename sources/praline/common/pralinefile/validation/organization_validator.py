from praline.common import organization_pattern
from praline.common.pralinefile.validation.validator import PralinefileValidationException, validator
from typing import Any, Dict


def validate_organization_work(pralinefile: Dict[str, Any]):
    organization = pralinefile.get('organization')
    if organization == None:
        raise PralinefileValidationException(f"Pralinefile is missing mandatory organization field")
    if not isinstance(organization, str):
        raise PralinefileValidationException(
            f"Pralinefile organization '{organization}' has invalid type '{type(organization)}' -- type must be str")
    if not organization_pattern.fullmatch(organization):
        raise PralinefileValidationException(
            f"Pralinefile organization '{organization}' is not valid -- organization must contain lowercase "
            "alphanumerics or underscores")


@validator
def validate_organization(pralinefile: Dict[str, Any]):
    validate_organization_work(pralinefile)
    for dependency in pralinefile.get('dependencies', []):
        validate_organization_work(dependency)
