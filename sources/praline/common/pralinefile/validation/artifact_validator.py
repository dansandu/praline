from praline.common.pralinefile.constants import artifact_pattern
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator


def validate_root_artifact(pralinefile):
    artifact = pralinefile['artifact']
    if not isinstance(artifact, str):
        raise PralinefileValidationError(f"pralinefile artifact '{artifact}' has invalid type '{type(artifact)}' -- type must be str")
    if not artifact_pattern.fullmatch(artifact):
        raise PralinefileValidationError(f"pralinefile artifact '{artifact}' is not valid -- artifact should contain lowercase words separated by underscores")


def validate_dependencies_artifact(pralinefile):
    for dependency in pralinefile['dependencies']:
        validate_root_artifact(dependency)


@validator
def validate_artifact(pralinefile):
    validate_root_artifact(pralinefile)
    validate_dependencies_artifact(pralinefile)
