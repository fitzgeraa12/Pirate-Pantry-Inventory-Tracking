from __future__ import annotations
from typing import Generic, TypeVar, Callable, Optional

T = TypeVar("T")
U = TypeVar("U")

class Option(Generic[T]):
    def __init__(self, value: Optional[T]):
        self._value = value

    @staticmethod
    def some(value: T) -> "Option[T]":
        return Option(value)

    @staticmethod
    def none() -> "Option[T]":
        return Option(None)

    def is_some(self) -> bool:
        return self._value is not None

    def is_none(self) -> bool:
        return self._value is None

    def unwrap(self) -> T:
        if self._value is None:
            raise ValueError("Called unwrap on None")
        return self._value

    def expect(self, msg: str) -> T:
        if self._value is None:
            raise ValueError(msg)
        return self._value

    def map(self, fn: Callable[[T], U]) -> "Option[U]":
        if self._value is None:
            return Option.none()
        return Option.some(fn(self._value))

    def unwrap_or(self, default: T) -> T:
        return self._value if self._value is not None else default

    def into_inner(self) -> Optional[T]:
        return self._value

    def __repr__(self) -> str:
        if self._value is None:
            return "Option::None"
        return f"Option::Some({self._value!r})"
