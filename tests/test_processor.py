import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from chat_history_to_project.processor import process_export
from tests.helpers import CharacterCounter, raw_chat


class ProcessorTests(unittest.TestCase):
    def test_processes_zip_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_path = root / "export.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(
                    "conversations.json",
                    json.dumps(
                        [
                            raw_chat("Keep Kafka", "useful"),
                            raw_chat("Ignore", "temporary"),
                            {},
                        ]
                    ),
                )

            result = process_export(
                archive_path,
                output_root=root / "Output",
                max_files=5,
                max_tokens_per_file=10_000,
                max_bytes_per_file=10_000,
                include=("kafka",),
                counter=CharacterCounter(),
            )

            self.assertEqual(result.input_conversations, 2)
            self.assertEqual(result.selected_conversations, 1)
            self.assertEqual(result.output_files, 1)
            output_files = list(result.output_directory.glob("part_*.json"))
            self.assertEqual(len(output_files), 1)
            payload = json.loads(output_files[0].read_text(encoding="utf-8"))
            self.assertEqual(payload[0]["title"], "Keep Kafka")
            self.assertEqual(
                payload[0]["messages"],
                [{"role": "user", "content": "useful"}],
            )
