from types import SimpleNamespace

import pytest
from telegram.constants import ChatMemberStatus

from django.db import transaction, IntegrityError
from django.utils import timezone

from django_nublado_telegram.models import (
    TelegramUser,
    TelegramChat,
    TelegramGroupMember,
)

from ..support.factories import (
    TelegramUserFactory,
    TelegramChatFactory,
    TelegramGroupMemberFactory,
)


class TestTelegramGroupMember:
    """
    Tests for the TelegramGroupMember model.
    """

    @pytest.mark.django_db
    def test_create_member(self):
        """
        Create a TelegramGroupMember object and check its attribute values.
        """
        user = TelegramUserFactory()
        chat = TelegramChatFactory()
        member = TelegramGroupMember.objects.create(
            user=user,
            chat=chat,
            role=TelegramGroupMember.GroupRole.MEMBER,
        )
        assert member.user == user
        assert member.chat == chat
        assert member.role == TelegramGroupMember.GroupRole.MEMBER
        assert member.is_active is True
        assert member.points == 0
        assert member.joined_at is not None
        assert member.left_at is None
        assert member.created_at is not None
        assert member.updated_at is not None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "role",
        TelegramGroupMember.GroupRole.values,
        ids=TelegramGroupMember.GroupRole.values,
    )
    def test_role_choices(self, role):
        """
        The TelegramChatMember enum values can be saved and retrieved correctly.
        """
        user = TelegramUserFactory()
        chat = TelegramChatFactory()
        member = TelegramGroupMember.objects.create(
            user=user, chat=chat, role=role
        )
        assert member.role == role

    @pytest.mark.django_db
    def test_unique_constraint(self):
        """
        User and chat are unique together.
        """
        user = TelegramUserFactory()
        chat = TelegramChatFactory()
        TelegramGroupMember.objects.create(
            user=user,
            chat=chat,
            role=TelegramGroupMember.GroupRole.MEMBER,
        )
        # Attempt to create another group member with the same
        # user and chat
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                TelegramGroupMember.objects.create(
                    user=user,
                    chat=chat,
                    role=TelegramGroupMember.GroupRole.ADMIN,
                )
        # Sanity check to make sure no faulty group member was created.
        assert TelegramGroupMember.objects.count() == 1

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "initial, incoming_status, expected_fields, expected_state",
        [
            # 1. No change (stable member)
            (
                dict(
                    role=TelegramGroupMember.GroupRole.MEMBER,
                    is_active=True,
                    left_at=None,
                ),
                TelegramGroupMember.GroupRole.MEMBER,
                [],
                dict(
                    role=TelegramGroupMember.GroupRole.MEMBER,
                    is_active=True,
                    left_at=None,
                ),
            ),

            # 2. Role change (member -> admin)
            (
                dict(
                    role=TelegramGroupMember.GroupRole.MEMBER,
                    is_active=True,
                    left_at=None,
                ),
                TelegramGroupMember.GroupRole.ADMIN,
                ["role"],
                dict(
                    role=TelegramGroupMember.GroupRole.ADMIN,
                    is_active=True,
                    left_at=None,
                ),
            ),

            # 3. Active -> inactive (left)
            (
                dict(
                    role=TelegramGroupMember.GroupRole.MEMBER,
                    is_active=True,
                    left_at=None,
                ),
                ChatMemberStatus.LEFT,
                ["is_active", "left_at"],
                dict(
                    role=TelegramGroupMember.GroupRole.MEMBER,
                    is_active=False,
                    left_at="set",
                ),
            ),

            # 4. Inactive -> active (rejoin)
            (
                dict(
                    role=TelegramGroupMember.GroupRole.MEMBER,
                    is_active=False,
                    left_at=timezone.now(),
                ),
                TelegramGroupMember.GroupRole.MEMBER,
                ["is_active", "left_at"],
                dict(
                    role=TelegramGroupMember.GroupRole.MEMBER,
                    is_active=True,
                    left_at=None,
                ),
            ),
        ],
    )
    def test_update_snapshot(
        self,
        initial,
        incoming_status,
        expected_fields,
        expected_state,
    ):
        member = TelegramGroupMemberFactory(**initial)

        tg_member = SimpleNamespace(status=incoming_status)

        updated = member.update_snapshot(tg_member)

        # 1. diff contract
        assert set(updated) == set(expected_fields)

        # 2. reload from DB
        member.refresh_from_db()

        # 3. state contract checks
        assert member.role == expected_state["role"]
        assert member.is_active == expected_state["is_active"]

        if expected_state["left_at"] == "set":
            assert member.left_at is not None
        else:
            assert member.left_at == expected_state["left_at"]

    @pytest.mark.django_db
    def test_mention_html_display_name(self):
        user = TelegramUserFactory(
            id=123,
            username="fooman",
        )
        member = TelegramGroupMemberFactory(user=user)

        assert (
            member.mention_html
            == '<a href="tg://user?id=123">@fooman</a>'
        )

    @pytest.mark.django_db
    def test_mention_html_escape(self):
        user = TelegramUserFactory(
            first_name='<script>alert("boom")</script>',
            username=None,
            last_name=None,
        )
        member = TelegramGroupMemberFactory(user=user)

        assert (
            member.mention_html
            == '<a href="tg://user?id='
            f'{user.id}'
            '">&lt;script&gt;alert(&quot;boom&quot;)&lt;/script&gt;</a>'
        )

    @pytest.mark.django_db
    def test_str_representation(self):
        """
        __str__ returns f"{member.user} in {member.chat} ({member.role})"
        """
        user = TelegramUserFactory()
        chat = TelegramChatFactory()
        member = TelegramGroupMember.objects.create(
            user=user,
            chat=chat,
            role=TelegramGroupMember.GroupRole.ADMIN,
        )
        assert str(member) == f"{member.user} in {member.chat} ({member.role})"
