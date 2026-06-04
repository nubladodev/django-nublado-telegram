from types import SimpleNamespace

import pytest
from unittest.mock import patch
from telegram.constants import ChatMemberStatus

from django_nublado_telegram.models import (
    TelegramUser,
    TelegramChat,
    TelegramGroupMember,
)
from .support.factories import (
    TelegramUserFactory,
    TelegramChatFactory,
    TelegramGroupMemberFactory,
)


@pytest.mark.django_db
class TestTelegramUserManager:
    def test_get_or_create_from_user_creates_user(self):
        user_id = 999
        tg_user = SimpleNamespace(
            id=user_id,
            username="alice",
            first_name="Alice",
            last_name="Smith",
            is_bot=False,
        )

        user, created = TelegramUser.objects.get_or_create_from_user(tg_user)

        assert created is True
        assert user.id == user_id
        assert user.username == "alice"
        assert user.first_name == "Alice"
        assert user.last_name == "Smith"
        assert user.is_bot is False

    def test_get_or_create_from_user_updates_existing_user(self):
        user = TelegramUserFactory(
            username="oldname",
            first_name="Old",
            last_name="User",
            is_bot=False,
        )

        tg_user = SimpleNamespace(
            id=user.id,
            username="newname",
            first_name="New",
            last_name="User",
            is_bot=True,
        )

        returned_user, created = TelegramUser.objects.get_or_create_from_user(
            tg_user
        )

        assert created is False
        assert returned_user.pk == user.pk

        returned_user.refresh_from_db()

        assert returned_user.username == "newname"
        assert returned_user.first_name == "New"
        assert returned_user.last_name == "User"
        assert returned_user.is_bot is True

    def test_get_or_create_from_user_calls_update_snapshot(self):
        user = TelegramUserFactory(
            username="oldname",
        )

        tg_user = SimpleNamespace(
            id=user.id,
            username="newname",
            first_name="Alice",
            last_name="Smith",
            is_bot=False,
        )

        with patch.object(
            TelegramUser,
            "update_snapshot",
            return_value=["username"],
        ) as mock_update:
            user, created = TelegramUser.objects.get_or_create_from_user(
                tg_user
            )

        assert created is False
        mock_update.assert_called_once_with(tg_user)


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


@pytest.mark.django_db
class TestTelegramGroupMemberManager:
    def test_get_or_create_from_chat_member_creates_member(self):
        user_id = 333
        tg_user = SimpleNamespace(
            id=user_id,
            username="alice",
            first_name="Alice",
            last_name=None,
            is_bot=False,
        )

        chat_id = 444
        tg_chat = SimpleNamespace(
            id=chat_id,
            type=TelegramChat.ChatType.GROUP,
            title="Foo Group",
            username=None,
        )

        tg_member = SimpleNamespace(
            user=tg_user,
            status=ChatMemberStatus.MEMBER,
        )

        member, created = (
            TelegramGroupMember.objects.get_or_create_from_chat_member(
                tg_member,
                tg_chat,
            )
        )

        assert created is True
        assert member.role == TelegramGroupMember.GroupRole.MEMBER
        assert member.is_active is True

    def test_get_or_create_from_chat_member_calls_update_snapshot(self):
        user = TelegramUserFactory()
        chat = TelegramChatFactory()

        TelegramGroupMemberFactory(
            user=user,
            chat=chat,
        )

        tg_user = SimpleNamespace(
            id=user.id,
            username="alice",
            first_name="Alice",
            last_name=None,
            is_bot=False,
        )

        tg_chat = SimpleNamespace(
            id=chat.id,
            type=TelegramChat.ChatType.GROUP,
            title="Foo Group",
            username=None,
        )

        tg_member = SimpleNamespace(
            user=tg_user,
            status=ChatMemberStatus.ADMINISTRATOR,
        )

        with patch.object(
            TelegramGroupMember,
            "update_snapshot",
            return_value=["role"],
        ) as mock_update:

            member, created = (
                TelegramGroupMember.objects.get_or_create_from_chat_member(
                    tg_member,
                    tg_chat,
                )
            )

        assert created is False
        mock_update.assert_called_once_with(tg_member)

    def test_get_or_create_from_chat_member_invalid_status_becomes_inactive(self):
        user_id = 777
        tg_user = SimpleNamespace(
            id=user_id,
            username="alice",
            first_name="Alice",
            last_name=None,
            is_bot=False,
        )

        chat_id=888
        tg_chat = SimpleNamespace(
            id=chat_id,
            type=TelegramChat.ChatType.GROUP,
            title="Foo Group",
            username=None,
        )

        tg_member = SimpleNamespace(
            user=tg_user,
            status="totally_bogus_status",
        )

        member, created = (
            TelegramGroupMember.objects.get_or_create_from_chat_member(
                tg_member,
                tg_chat,
            )
        )

        assert created is True
        assert member.role == TelegramGroupMember.GroupRole.MEMBER
        assert member.is_active is False