from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from .tokenizer import compact_json


def write_parts(
    parts: Iterable[list[dict[str, Any]]],
    output_root: str | Path,
    *,
    now: datetime | None = None,
) -> Path:
    output_root_path = Path(output_root).expanduser().resolve()
    timestamp = (now or datetime.now().astimezone()).strftime("%Y-%m-%d_%H-%M-%S-%f%z")
    run_directory = output_root_path / timestamp
    run_directory.mkdir(parents=True, exist_ok=False)

    for index, part in enumerate(parts, start=1):
        output_path = run_directory / f"part_{index:03d}.json"
        output_path.write_text(compact_json(part), encoding="utf-8")

    return run_directory
