import unittest

from chat_history_to_project.models import Conversation, Message


class OutputModelTests(unittest.TestCase):
    def test_serializes_an_ordered_dialogue_without_internal_graph_fields(self) -> None:
        chat = Conversation(
            title="Decision log",
            messages=(
                Message(role="user", content=("Should we use JSON?",)),
                Message(role="assistant", content=("Yes.",)),
                Message(role="assistant", content=("Keep the original text.",)),
            ),
        )

        self.assertEqual(
            chat.to_output_dict(),
            {
                "title": "Decision log",
                "messages": [
                    {"role": "user", "content": "Should we use JSON?"},
                    {"role": "assistant", "content": "Yes."},
                    {"role": "assistant", "content": "Keep the original text."},
                ],
            },
        )

    def test_keeps_multimodal_parts_and_multi_part_text_exactly(self) -> None:
        image = {
            "content_type": "image_asset_pointer",
            "asset_pointer": "file-service://test",
            "metadata": {"source": "upload", "width": 1200},
        }
        audio = {"content_type": "audio_transcription", "text": "Meet at noon"}

        chat = Conversation(
            title="Multimodal",
            messages=(
                Message(role="user", content=(image, "What is in this picture?")),
                Message(role="user", content=(audio,)),
                Message(role="assistant", content=("First part", "Second part")),
            ),
        )

        self.assertEqual(
            chat.to_output_dict()["messages"],
            [
                {"role": "user", "content": [image, "What is in this picture?"]},
                {"role": "user", "content": [audio]},
                {"role": "assistant", "content": ["First part", "Second part"]},
            ],
        )


if __name__ == "__main__":
    unittest.main()
