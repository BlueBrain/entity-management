# SPDX-License-Identifier: Apache-2.0

"""Typing related declarations."""

import typing

T = typing.TypeVar("T")

MaybeList = typing.Union[T, typing.List[T]]
