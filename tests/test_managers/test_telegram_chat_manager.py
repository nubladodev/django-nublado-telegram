from types import SimpleNamespace
from unittest.mock import patch

import pytest

from django_nublado_telegram.models import TelegramChat
from ..support.factories import TelegramChatFactory


@pytest.mark.django_db
class TestTelegramChatManager:
    def test_get_or_create_from_chat_creates_chat(self):
        chat_id = 111
        tg_chat = SimpleNamespace(
            id=chat_id,
            type=TelegramChat.ChatType.GROUP,
            title="Foo Group",
            username="foo_group",
        )

        chat, created = TelegramChat.objects.get_or_create_from_chat(
            tg_chat
        )

        assert created is True
        assert chat.id == chat.id
        assert chat.chat_type == TelegramChat.ChatType.GROUP
        assert chat.title == "Foo Group"
        assert chat.username == "foo_group"

    def test_get_or_create_from_chat_updates_existing_chat(self):
        chat = TelegramChatFactory(
            chat_type=TelegramChat.ChatType.GROUP,
            title="Old Title",
            username="old_group",
        )

        tg_chat = SimpleNamespace(
            id=chat.id,
            type=TelegramChat.ChatType.SUPERGROUP,
            title="New Title",
            username="new_group",
        )

        chat, created = TelegramChat.objects.get_or_create_from_chat(
            tg_chat
        )

        assert created is False

        chat.refresh_from_db()

        assert chat.chat_type == TelegramChat.ChatType.SUPERGROUP
        assert chat.title == "New Title"
        assert chat.username == "new_group"

    def test_get_or_create_from_chat_id_creates_chat(self):
        chat, created = (
            TelegramChat.objects.get_or_create_from_chat_id(222)
        )

        assert created is True
        assert chat.id == 222
        assert chat.chat_type == TelegramChat.ChatType.UNKNOWN
        assert chat.title is None
        assert chat.username is None

    def test_get_or_create_from_chat_calls_update_snapshot(self):
        chat = TelegramChatFactory()
        tg_chat = SimpleNamespace(
            id=chat.id,
            type=TelegramChat.ChatType.GROUP,
            title="Foo",
            username="foo",
        )

        with patch.object(
            TelegramChat,
            "update_snapshot",
            return_value=["title"],
        ) as mock_update:
            chat, created = TelegramChat.objects.get_or_create_from_chat(
                tg_chat
            )

        assert created is False
        mock_update.assert_called_once_with(tg_chat)
