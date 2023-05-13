from praline.common import get_duplicates
from praline.common.pralinefile.validation.validator import validator, PralinefileValidationError
from typing import Any, Dict


@validator
def validate_unique_dependencies(pralinefile: Dict[str, Any]):
    dependencies = pralinefile.get('dependencies', [])

    def duplicate_artifact(a, b):
        return (a.get('organization', 'a') == b.get('organization', 'b') and 
                a.get('artifact', 'a') == b.get('artifact', 'b'))

    if any(duplicate_artifact(pralinefile, dependency) for dependency in dependencies):
        raise PralinefileValidationError(f"Pralinefile cannot have itself as a dependency")
    
    if get_duplicates(dependencies, lambda a, b: duplicate_artifact(a, b)):
        raise PralinefileValidationError(f"Pralinefile cannot have duplicate dependencies")
