"""Debug utilities."""

import os
import sys
from functools import partial
from typing import Optional


def _env_true(var_name: str) -> Optional[bool]:
    """Return True, False, or None depending on the value of the given env variable name.

    Return:

    - True if the env variable is set to "1" or "true" (case-insensitive)
    - None if it's set to an empty string, or not set
    - False if it's set to something else
    """
    env = os.getenv(var_name, None)
    return env.upper() in {"1", "TRUE"} if env else None


def _get_pformat():
    """Return the function to be used for formatting."""
    if _env_true("PY_DEVTOOLS_ENABLE"):
        from devtools import pformat  # pylint: disable=import-error,import-outside-toplevel

        force_highlight = _env_true("PY_DEVTOOLS_HIGHLIGHT")
        highlight = sys.stdout.isatty() if force_highlight is None else force_highlight
        return partial(pformat, highlight=highlight)
    return str


class PP:
    """Lazy pretty printer with pformat from devtools, or fallback to str.

    To enable devtools pretty formatting:

    - ensure that devtools is installed
    - set PY_DEVTOOLS_ENABLE=1
    - set PY_DEVTOOLS_HIGHLIGHT=1
    """

    _pformat = staticmethod(_get_pformat())

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self._pformat(self.value)
