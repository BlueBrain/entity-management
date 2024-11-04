"""Http wrapper."""

from contextlib import asynccontextmanager

import httpx


class HTTPStatusError(httpx.HTTPStatusError):
    """Wrap HTTPStatusError."""


async def get(*args, **kwargs):
    """Wrap get."""
    async with httpx.AsyncClient() as client:
        return await client.get(*args, **kwargs)


async def post(*args, **kwargs):
    """Wrap post."""
    async with httpx.AsyncClient() as client:
        return await client.post(*args, **kwargs)


async def put(*args, **kwargs):
    """Wrap put."""
    async with httpx.AsyncClient() as client:
        return await client.put(*args, **kwargs)


async def delete(*args, **kwargs):
    """Wrap delete."""
    async with httpx.AsyncClient() as client:
        return await client.delete(*args, **kwargs)


@asynccontextmanager
async def stream(*args, **kwargs):
    """Wrap stream."""
    async with httpx.AsyncClient() as client, client.stream(*args, **kwargs) as response:
        yield response
