from __future__ import annotations

import json
import re
import zipfile
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Any, TypeVar

_SINGLE_FILE = re.compile(r"^conversations\.json$", re.IGNORECASE)
_NUMBERED_FILE = re.compile(r"^conversations-(\d+)\.json$", re.IGNORECASE)
T = TypeVar("T")


def load_export(source: str | Path) -> list[dict[str, Any]]:
    """Materialize the export for callers that need the full raw history in memory."""
    return list(iter_export(source))


def iter_export(source: str | Path) -> Iterator[dict[str, Any]]:
    """Read one conversation JSON file at a time, including multi-file exports."""
    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Input does not exist: {source_path}")

    if source_path.is_dir():
        yield from _load_from_directory(source_path)
        return
    if zipfile.is_zipfile(source_path):
        yield from _load_from_zip(source_path)
        return
    if source_path.suffix.lower() == ".json":
        yield from _load_json_file(source_path)
        return

    raise ValueError("Input must be a ChatGPT export ZIP, a directory, or a JSON file.")


def _load_from_directory(directory: Path) -> Iterator[dict[str, Any]]:
    candidates = [path for path in directory.rglob("*.json") if _is_conversation_file(path.name)]
    selected = _select_conversation_files(candidates, lambda path: path.name)
    if not selected:
        raise FileNotFoundError(
            f"No conversations.json or conversations-*.json found in {directory}"
        )

    for path in selected:
        yield from _load_json_file(path)


def _load_from_zip(archive_path: Path) -> Iterator[dict[str, Any]]:
    with zipfile.ZipFile(archive_path) as archive:
        candidates = [
            name
            for name in archive.namelist()
            if not name.endswith("/") and _is_conversation_file(Path(name).name)
        ]
        selected = _select_conversation_files(candidates, lambda name: Path(name).name)
        if not selected:
            raise FileNotFoundError(
                f"No conversations.json or conversations-*.json found in {archive_path}"
            )

        for member in selected:
            with archive.open(member) as file:
                payload = json.load(file)
            yield from _expect_conversation_list(payload, member)


def _load_json_file(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as file:
        payload = json.load(file)
    yield from _expect_conversation_list(payload, str(path))


def _expect_conversation_list(payload: Any, source_name: str) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON array of conversations in {source_name}")
    return payload


def _is_conversation_file(file_name: str) -> bool:
    return bool(_SINGLE_FILE.match(file_name) or _NUMBERED_FILE.match(file_name))


def _select_conversation_files(items: Iterable[T], name_of: Callable[[T], str]) -> list[T]:
    items = list(items)
    numbered: list[tuple[int, T]] = []
    single: list[T] = []

    for item in items:
        file_name = name_of(item)
        numbered_match = _NUMBERED_FILE.match(file_name)
        if numbered_match:
            numbered.append((int(numbered_match.group(1)), item))
        elif _SINGLE_FILE.match(file_name):
            single.append(item)

    if numbered:
        return [item for _, item in sorted(numbered, key=lambda pair: pair[0])]
    return sorted(single, key=lambda item: str(item))[:1]
