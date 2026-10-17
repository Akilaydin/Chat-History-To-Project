"""Legacy launcher for running the repository without the installed console entry point."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from chat_history_to_project.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
