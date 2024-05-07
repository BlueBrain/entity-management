"""Typing related declarations."""

import typing

T = typing.TypeVar("T")

MaybeList = T | list[T]
