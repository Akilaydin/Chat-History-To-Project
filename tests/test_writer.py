import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from chat_history_to_project.writer import write_parts


class WriterTests(unittest.TestCase):
    def test_each_run_uses_exact_timestamp_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixed = datetime(2026, 9, 27, 18, 54, 12, 123456, tzinfo=timezone.utc)
            output = write_parts([[{"title": "A", "messages": {}}]], Path(temp), now=fixed)
            self.assertEqual(output.name, "2026-09-27_18-54-12-123456+0000")
            self.assertTrue((output / "part_001.json").exists())


if __name__ == "__main__":
    unittest.main()
