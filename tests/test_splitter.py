import unittest

from chat_history_to_project.splitter import SplitLimitError, split_conversations
from chat_history_to_project.tokenizer import TokenCounter, compact_json
from tests.helpers import CharacterCounter, conversation


class SplitterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.counter = CharacterCounter()

    def test_never_returns_more_than_max_files(self) -> None:
        chats = [conversation(f"Chat {index}", "x" * 80) for index in range(6)]
        with self.assertRaises(SplitLimitError):
            split_conversations(
                chats,
                max_files=2,
                max_tokens_per_file=250,
                max_bytes_per_file=10_000,
                counter=self.counter,
            )

    def test_large_conversation_is_split_between_messages(self) -> None:
        chat = conversation("Large", *("x" * 120 for _ in range(8)))
        parts = split_conversations(
            [chat],
            max_files=20,
            max_tokens_per_file=600,
            max_bytes_per_file=10_000,
            counter=self.counter,
        )
        self.assertGreater(len(parts), 1)
        self.assertTrue(all(len(compact_json(part)) <= 600 for part in parts))
        titles = [item["title"] for part in parts for item in part]
        self.assertTrue(all(title.startswith("Large (part ") for title in titles))
        fragment_messages = [
            message for part in parts for record in part for message in record["messages"]
        ]
        self.assertEqual(
            [message["content"] for message in fragment_messages],
            ["x" * 120] * 8,
        )
        self.assertEqual(
            [message["role"] for message in fragment_messages],
            ["user", "assistant"] * 4,
        )

    def test_small_conversations_share_a_file(self) -> None:
        chats = [conversation("A", "hello"), conversation("B", "world")]
        parts = split_conversations(
            chats,
            max_files=5,
            max_tokens_per_file=10_000,
            max_bytes_per_file=10_000,
            counter=self.counter,
        )
        self.assertEqual(len(parts), 1)
        self.assertEqual([item["title"] for item in parts[0]], ["A", "B"])

    def test_does_not_reorder_to_bypass_file_limit(self) -> None:
        chats = [
            conversation("A1", "x" * 60),
            conversation("A2", "x" * 60),
            conversation("B1", "x" * 40),
            conversation("B2", "x" * 40),
        ]
        large_and_small = compact_json([chats[0].to_output_dict(), chats[2].to_output_dict()])

        with self.assertRaisesRegex(SplitLimitError, "Output order cannot be changed"):
            split_conversations(
                chats,
                max_files=2,
                max_tokens_per_file=len(large_and_small),
                max_bytes_per_file=10_000,
                counter=self.counter,
            )

        parts = split_conversations(
            chats,
            max_files=3,
            max_tokens_per_file=len(large_and_small),
            max_bytes_per_file=10_000,
            counter=self.counter,
        )
        self.assertEqual(len(parts), 3)
        self.assertEqual(
            [item["title"] for part in parts for item in part],
            ["A1", "A2", "B1", "B2"],
        )

    def test_split_fragments_keep_order_across_output_files(self) -> None:
        chat = conversation(
            "Sequential",
            *[f"message-{index}-" + "x" * 100 for index in range(6)],
        )
        parts = split_conversations(
            [chat],
            max_files=10,
            max_tokens_per_file=340,
            max_bytes_per_file=10_000,
            counter=self.counter,
        )
        self.assertGreater(len(parts), 1)
        self.assertEqual(
            [
                message["content"]
                for part in parts
                for record in part
                for message in record["messages"]
            ],
            [f"message-{index}-" + "x" * 100 for index in range(6)],
        )

    def test_final_payload_respects_real_token_limit(self) -> None:
        counter = TokenCounter()
        chats = [conversation(f"Chat {index}", "hello world " * 20) for index in range(8)]
        parts = split_conversations(
            chats,
            max_files=20,
            max_tokens_per_file=150,
            max_bytes_per_file=10_000,
            counter=counter,
        )
        self.assertTrue(all(counter.count_text(compact_json(part)) <= 150 for part in parts))

    def test_token_counter_accepts_text_that_looks_like_special_token(self) -> None:
        counter = TokenCounter()
        self.assertGreater(counter.count_text("literal <|endoftext|> text"), 0)


if __name__ == "__main__":
    unittest.main()
