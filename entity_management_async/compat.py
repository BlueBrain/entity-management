"""Compatibility with older Python versions."""

import sys

if sys.version_info < (3, 9):
    import importlib_resources as resources  # noqa pylint: disable=unused-import
else:
    from importlib import resources  # noqa pylint: disable=unused-import
