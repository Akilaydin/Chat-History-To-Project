import unittest
from datetime import datetime, timezone

from chat_history_to_project.parser import parse_conversations
from tests.helpers import raw_chat


class ParserTests(unittest.TestCase):
    def test_preserves_required_message_fields(self) -> None:
        parsed = parse_conversations([raw_chat("Title", "Привет 🌍")])
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].title, "Title")
        self.assertEqual(parsed[0].messages[0].content, ("Привет 🌍",))
        self.assertEqual(parsed[0].messages[0].role, "user")

    def test_uses_only_active_current_node_branch(self) -> None:
        chat = {
            "title": "Regenerated answer",
            "create_time": 1_767_225_600.0,
            "current_node": "new-answer",
            "mapping": {
                "root": {
                    "id": "root",
                    "parent": None,
                    "children": ["user"],
                    "message": None,
                },
                "user": {
                    "id": "user",
                    "parent": "root",
                    "children": ["old-answer", "new-answer"],
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Question"]},
                    },
                },
                "old-answer": {
                    "id": "old-answer",
                    "parent": "user",
                    "children": [],
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Rejected answer"]},
                    },
                },
                "new-answer": {
                    "id": "new-answer",
                    "parent": "user",
                    "children": [],
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Visible answer"]},
                    },
                },
            },
        }

        parsed = parse_conversations([chat])[0]

        self.assertEqual(
            [message.content for message in parsed.messages],
            [("Question",), ("Visible answer",)],
        )
        self.assertNotIn("Rejected answer", parsed.searchable_text())

    def test_reads_text_payload_for_non_parts_content(self) -> None:
        chat = raw_chat("Code", "placeholder")
        chat["mapping"]["1"]["message"]["content"] = {
            "content_type": "code",
            "text": "print('hello')",
        }

        parsed = parse_conversations([chat])[0]

        self.assertEqual(parsed.messages[0].content, ("print('hello')",))

    def test_uses_first_message_timestamp_when_conversation_timestamp_is_null(self) -> None:
        chat = raw_chat("Timestamp", "hello")
        chat["create_time"] = None

        parsed = parse_conversations([chat])[0]

        self.assertEqual(
            parsed.create_time,
            datetime.fromtimestamp(1_767_225_600.0, tz=timezone.utc),
        )

    def test_tolerates_millisecond_message_timestamp_in_official_export(self) -> None:
        chat = raw_chat("Timestamp", "hello")
        chat["mapping"]["1"]["message"]["create_time"] = 1_749_567_670_315.0

        parsed = parse_conversations([chat])[0]

        self.assertEqual(
            parsed.messages[0].create_time,
            datetime.fromtimestamp(1_749_567_670.315, tz=timezone.utc),
        )

    def test_skips_empty_placeholders_and_nonvisible_internal_messages(self) -> None:
        chat = raw_chat("Visible", "hello")
        chat["mapping"]["2"] = {
            "id": "2",
            "parent": "1",
            "children": [],
            "message": {
                "author": {"role": "assistant"},
                "content": {"content_type": "thoughts", "thoughts": ["not visible"]},
            },
        }
        chat["current_node"] = "2"

        parsed = parse_conversations([{}, chat])

        self.assertEqual(len(parsed), 1)
        self.assertEqual([message.content for message in parsed[0].messages], [("hello",)])


if __name__ == "__main__":
    unittest.main()
