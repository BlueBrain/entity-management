#!/usr/bin/env python3
"""Unasync wrapper."""

import re
from dataclasses import dataclass
from pathlib import Path

import unasync


@dataclass(kw_only=True)
class Item:
    src: str
    dst: str


def _check_files(src_file, dst_file):
    """Check the src and dst paths, and create a backup copy."""
    src = Path(src_file).resolve()
    dst = Path(dst_file).resolve()
    if src == dst:
        raise RuntimeError("Source and destination files must be different")
    if dst.is_file():
        dst.replace(dst.parent / f"{dst.name}.bak")


def _postprocess(
    filepath: str,
    prepend_text: str = "# Automatically generated, DO NOT EDIT.\n",
    exclude_pattern: re.Pattern = re.compile("# *unasync: *remove"),
) -> None:
    """Postprocess output files.

    Args:
        filepath: path of the file to be processed.
        prepend_text: text to be added at the beginning of the file.
        exclude_pattern: pattern for lines to be excluded.
    """
    with open(filepath, "r+") as f:
        lines = [line for line in f if not exclude_pattern.search(line)]
        f.seek(0)
        f.write(prepend_text)
        f.writelines(lines)
        f.truncate()


def _run(fromdir: str, todir: str, additional_replacements: dict) -> None:
    top = Path(fromdir)
    filepaths = [
        Item(src=str(root / name), dst=str(root / name).replace(fromdir, todir))
        for root, _dirs, files in top.walk()
        for name in files
        if name.endswith(".py")
    ]
    for item in filepaths:
        _check_files(src_file=item.src, dst_file=item.dst)
    unasync.unasync_files(
        [item.src for item in filepaths],
        rules=[
            unasync.Rule(
                fromdir=fromdir,
                todir=todir,
                additional_replacements=additional_replacements,
            )
        ],
    )
    for item in filepaths:
        _postprocess(filepath=item.dst)


def main() -> None:
    """Transform asynchronous code into synchronous code."""
    additional_replacements = {
        "AsyncClient": "Client",
        "_async": "_sync",
        "aclosing": "closing",
        "aclose": "close",
        "AsyncMock": "MagicMock",
        "assert_awaited_once_with": "assert_called_once_with",
        "aiter_bytes": "iter_bytes",
        "aread": "read",
        "a_refresh_token": "refresh_token",
        "entity_management_async": "entity_management",
    }
    _run(
        fromdir="entity_management_async/",
        todir="entity_management/",
        additional_replacements=additional_replacements,
    )
    _run(
        fromdir="tests/_async/",
        todir="tests/_sync/",
        additional_replacements=additional_replacements,
    )


if __name__ == "__main__":
    main()
