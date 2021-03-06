from typing import Any, Type


def subclasses_of(klass: Type[Any]):
    subclasses = []
    stack      = [klass]
    while stack:
        parent = stack.pop()
        for subclass in parent.__subclasses__():
            if subclass not in subclasses:
                stack.append(subclass)
                subclasses.append(subclass)
    return subclasses
