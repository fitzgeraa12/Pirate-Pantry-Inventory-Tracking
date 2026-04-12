class _UnsetType:
    def __repr__(self) -> str:
        return "UNSET"

UNSET = _UnsetType()

from typing import TypeAlias
Unset: TypeAlias = _UnsetType
