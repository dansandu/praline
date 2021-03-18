from dataclasses import dataclass
from logging import getLogger
from typing import Any, Dict, List, T


logger = getLogger(__name__)


class ResourceNotPresentError(Exception):
    pass


class ResourceOverriddenError(Exception):
    pass


class UndeclaredResourceSuppliedError(Exception):
    pass


@dataclass(frozen=True, repr=False)
class StageResources:
    stage: str
    activation: int
    resources: Dict[str, Any]
    constrained_output: List[str]

    def __repr__(self):
        return str(self.resources)

    def __str__(self):
        return str(self.resources)
    
    def __getitem__(self, resource: str) -> T:
        if resource not in self.resources:
            raise ResourceNotPresentError(f"stage '{self.stage}' is requesting resource '{resource}' but it hasn't been supplied yet")
        return self.resources[resource]

    def __setitem__(self, resource: str, value) -> None:
        logger.debug(f"stage '{self.stage}' set resource '{resource}' to {value}")
        if resource in self.resources:
            raise ResourceOverriddenError(f"stage '{self.stage}' is trying to override resource '{resource}'")
        if resource not in self.constrained_output:
            raise UndeclaredResourceSuppliedError(f"stage '{self.stage}' is trying to supply resource '{resource}' but it didn't declare it as output")
        self.resources[resource] = value

    def __contains__(self, resource: str) -> bool:
        return resource in self.resources
