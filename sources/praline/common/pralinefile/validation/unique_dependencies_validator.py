from praline.common.pralinefile.validation.validator import validator, PralinefileValidationError
from typing import Any, Dict


@validator
def validate_unique_dependencies(pralinefile: Dict[str, Any]):
    dependencies = pralinefile.get('dependencies', [])

    def artifacts_match(a, b):
        return a.get('organization', '') == b.get('organization', '') and a.get('artifact', '') == b.get('artifact', '')

    if any(artifacts_match(pralinefile, dependency) for dependency in dependencies):
        raise PralinefileValidationError(f"pralinefile cannot have itself as a dependency")
    
    duplicates = [(i, j) for i in range(len(dependencies)) for j in range(i + 1, len(dependencies)) if artifacts_match(dependencies[i], dependencies[j])]
    for duplicate in duplicates:
        raise PralinefileValidationError(f"pralinefile cannot have duplicate dependencies -- dependency {dependencies[duplicate[0]]} is in conflict with dependency {dependencies[duplicate[1]]}")
