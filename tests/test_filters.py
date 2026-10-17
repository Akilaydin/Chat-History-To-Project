import unittest
from datetime import date, datetime, timezone

from chat_history_to_project.filters import filter_conversations
from tests.helpers import conversation


class FilterTests(unittest.TestCase):
    def test_filters_by_date_include_and_exclude(self) -> None:
        chats = [
            conversation(
                "Platform Kafka",
                "migration notes",
                create_time=datetime(2026, 3, 5, tzinfo=timezone.utc),
            ),
            conversation(
                "Platform RabbitMQ",
                "legacy queue",
                create_time=datetime(2026, 4, 5, tzinfo=timezone.utc),
            ),
            conversation(
                "Other", "Kafka experiment", create_time=datetime(2025, 12, 5, tzinfo=timezone.utc)
            ),
        ]
        result = filter_conversations(
            chats,
            from_date=date(2026, 1, 1),
            to_date=date(2026, 12, 31),
            include=("platform",),
            exclude=("rabbitmq",),
        )
        self.assertEqual([chat.title for chat in result], ["Platform Kafka"])


if __name__ == "__main__":
    unittest.main()
