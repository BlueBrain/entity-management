# Automatically generated, DO NOT EDIT.
"""Http wrapper."""

from contextlib import contextmanager

import httpx


class HTTPStatusError(httpx.HTTPStatusError):
    """Wrap HTTPStatusError."""


def get(*args, **kwargs):
    """Wrap get."""
    with httpx.Client() as client:
        return client.get(*args, **kwargs)


def post(*args, **kwargs):
    """Wrap post."""
    with httpx.Client() as client:
        return client.post(*args, **kwargs)


def put(*args, **kwargs):
    """Wrap put."""
    with httpx.Client() as client:
        return client.put(*args, **kwargs)


def delete(*args, **kwargs):
    """Wrap delete."""
    with httpx.Client() as client:
        return client.delete(*args, **kwargs)


@contextmanager
def stream(*args, **kwargs):
    """Wrap stream."""
    with httpx.Client() as client, client.stream(*args, **kwargs) as response:
        yield response
