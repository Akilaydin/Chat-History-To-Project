import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from chat_history_to_project.export_reader import iter_export, load_export
from tests.helpers import raw_chat


class ExportReaderTests(unittest.TestCase):
    def test_loads_single_conversations_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "conversations.json").write_text(
                json.dumps([raw_chat("one", "hello")]), encoding="utf-8"
            )
            chats = load_export(root)
            self.assertEqual([chat["title"] for chat in chats], ["one"])

    def test_loads_utf8_bom_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "conversations.json"
            path.write_text(json.dumps([raw_chat("one", "hello")]), encoding="utf-8-sig")
            chats = load_export(path)
            self.assertEqual([chat["title"] for chat in chats], ["one"])

    def test_numbered_files_are_combined_in_numeric_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "conversations-001.json").write_text(
                json.dumps([raw_chat("second", "b")]), encoding="utf-8"
            )
            (root / "conversations-000.json").write_text(
                json.dumps([raw_chat("first", "a")]), encoding="utf-8"
            )
            (root / "conversations.json").write_text(
                json.dumps([raw_chat("legacy", "ignored")]), encoding="utf-8"
            )
            chats = load_export(root)
            self.assertEqual([chat["title"] for chat in chats], ["first", "second"])

    def test_loads_numbered_files_directly_from_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "export.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(
                    "export/conversations-001.json", json.dumps([raw_chat("two", "b")])
                )
                archive.writestr(
                    "export/conversations-000.json", json.dumps([raw_chat("one", "a")])
                )
            chats = load_export(archive_path)
            self.assertEqual([chat["title"] for chat in chats], ["one", "two"])

    def test_reads_numbered_files_lazily(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "conversations-000.json").write_text(
                json.dumps([raw_chat("first", "hello")]), encoding="utf-8"
            )
            (root / "conversations-001.json").write_text("{invalid", encoding="utf-8")

            stream = iter_export(root)
            self.assertEqual(next(stream)["title"], "first")
            with self.assertRaises(json.JSONDecodeError):
                next(stream)


if __name__ == "__main__":
    unittest.main()
