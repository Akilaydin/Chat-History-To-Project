from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .config import DEFAULT_MAX_FILE_BYTES, DEFAULT_MAX_TOKENS_PER_FILE
from .export_reader import iter_export
from .filters import matches_conversation
from .models import Conversation
from .parser import parse_conversation
from .splitter import split_conversations
from .tokenizer import Counter
from .writer import write_parts


@dataclass(frozen=True)
class ProcessResult:
    input_conversations: int
    selected_conversations: int
    output_files: int
    output_directory: Path


def process_export(
    source: str | Path,
    *,
    output_root: str | Path = "Output",
    max_files: int,
    max_tokens_per_file: int = DEFAULT_MAX_TOKENS_PER_FILE,
    max_bytes_per_file: int = DEFAULT_MAX_FILE_BYTES,
    from_date: date | None = None,
    to_date: date | None = None,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
    counter: Counter | None = None,
) -> ProcessResult:
    input_count = 0
    selected_count = 0

    def selected_conversations() -> Iterator[Conversation]:
        nonlocal input_count, selected_count
        for raw in iter_export(source):
            conversation = parse_conversation(raw)
            if conversation is None:
                # Official exports may contain empty placeholder objects.
                continue
            input_count += 1
            if matches_conversation(
                conversation,
                from_date=from_date,
                to_date=to_date,
                include=include,
                exclude=exclude,
            ):
                selected_count += 1
                yield conversation

    parts = split_conversations(
        selected_conversations(),
        max_files=max_files,
        max_tokens_per_file=max_tokens_per_file,
        max_bytes_per_file=max_bytes_per_file,
        counter=counter,
    )
    if not selected_count:
        raise ValueError("No conversations matched the selected input and filters.")
    output_directory = write_parts(parts, output_root)

    return ProcessResult(
        input_conversations=input_count,
        selected_conversations=selected_count,
        output_files=len(parts),
        output_directory=output_directory,
    )
