from praline.common.constants import organization_pattern
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict


def validate_root_organization(pralinefile: Dict[str, Any]):
    organization = pralinefile.get('organization', '')
    if not isinstance(organization, str):
        raise PralinefileValidationError(f"pralinefile organization '{organization}' has invalid type '{type(organization)}' -- type must be str")
    if not organization_pattern.fullmatch(organization):
        raise PralinefileValidationError(f"pralinefile organization '{organization}' is not valid -- organization should contain lowercase words separated by underscores")


def validate_dependencies_organization(pralinefile: Dict[str, Any]):
    for dependency in pralinefile.get('dependencies', []):
        validate_root_organization(dependency)


@validator
def validate_organization(pralinefile: Dict[str, Any]):
    validate_root_organization(pralinefile)
    validate_dependencies_organization(pralinefile)
