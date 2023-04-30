from praline.common import artifact_version_pattern, dependency_version_pattern, ArtifactVersion, DependencyVersion
from praline.common.pralinefile.validation.validator import PralinefileValidationError, validator
from typing import Any, Dict, Pattern


def validate_version_work(pralinefile: Dict[str, Any], pattern: Pattern[str], klass: type):
    version = pralinefile.get('version')
    if version == None:
        raise PralinefileValidationError(f"Pralinefile is missing mandatory version field")
    if not isinstance(version, str):
        raise PralinefileValidationError(
            f"Pralinefile version '{version}' has invalid type '{type(version)}' -- type must be str")
    if not pattern.fullmatch(version):
        raise PralinefileValidationError(f"Pralinefile version '{version}' is not valid")
    pralinefile['version'] = klass.from_string(version)

@validator
def validate_version(pralinefile: Dict[str, Any]):
    validate_version_work(pralinefile, artifact_version_pattern, ArtifactVersion)
    for dependency in pralinefile.get('dependencies', []):
        validate_version_work(dependency, dependency_version_pattern, DependencyVersion)
