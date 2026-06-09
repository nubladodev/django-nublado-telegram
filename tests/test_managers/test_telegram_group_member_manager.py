from types import SimpleNamespace
from unittest.mock import patch

import pytest
from telegram.constants import ChatMemberStatus

from django_nublado_telegram.models import (
    TelegramChat,
    TelegramGroupMember,
)
from ..support.factories import (
    TelegramUserFactory,
    TelegramChatFactory,
    TelegramGroupMemberFactory,
)


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