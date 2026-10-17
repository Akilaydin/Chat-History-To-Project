from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .config import (
    DEFAULT_MAX_FILE_BYTES,
    DEFAULT_MAX_TOKENS_PER_FILE,
    DEFAULT_PLAN,
    PLAN_FILE_LIMITS,
    resolve_max_files,
)
from .processor import process_export


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chat-history-to-project",
        description="Prepare a ChatGPT data export for upload to a ChatGPT Project.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help=(
            "ChatGPT export ZIP, export directory, or conversations JSON "
            "(default: current directory)."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("Output"),
        help="Root output directory. Each run gets its own timestamped subdirectory.",
    )

    file_limit = parser.add_mutually_exclusive_group()
    file_limit.add_argument(
        "--plan",
        choices=tuple(PLAN_FILE_LIMITS),
        help=(f"Use the current ChatGPT Project file limit for a plan (default: {DEFAULT_PLAN})."),
    )
    file_limit.add_argument(
        "--max-files",
        type=_positive_int,
        help="Override the maximum number of output files.",
    )

    parser.add_argument(
        "--max-tokens-per-file",
        type=_positive_int,
        default=DEFAULT_MAX_TOKENS_PER_FILE,
        help=(f"Token budget per output file (default: {DEFAULT_MAX_TOKENS_PER_FILE:,})."),
    )
    parser.add_argument(
        "--max-file-mb",
        type=_positive_int,
        default=DEFAULT_MAX_FILE_BYTES // 1_000_000,
        help="Maximum output file size in MB (default: 512).",
    )
    parser.add_argument(
        "--from",
        dest="from_date",
        type=_iso_date,
        help="Keep chats on/after YYYY-MM-DD.",
    )
    parser.add_argument(
        "--to",
        dest="to_date",
        type=_iso_date,
        help="Keep chats on/before YYYY-MM-DD.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="TEXT",
        help=(
            "Keep chats containing TEXT in title or message content. Repeatable; terms are ORed."
        ),
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="TEXT",
        help=("Drop chats containing TEXT in title or message content. Repeatable."),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.from_date and args.to_date and args.from_date > args.to_date:
        parser.error("--from must be earlier than or equal to --to")

    max_files = resolve_max_files(args.plan, args.max_files)
    try:
        result = process_export(
            args.source,
            output_root=args.output_dir,
            max_files=max_files,
            max_tokens_per_file=args.max_tokens_per_file,
            max_bytes_per_file=args.max_file_mb * 1_000_000,
            from_date=args.from_date,
            to_date=args.to_date,
            include=tuple(args.include),
            exclude=tuple(args.exclude),
        )
    except (FileNotFoundError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")

    print(f"Conversations: {result.selected_conversations}/{result.input_conversations}")
    print(f"Output files: {result.output_files}/{max_files}")
    print(f"Output: {result.output_directory}")
    return 0


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from error
