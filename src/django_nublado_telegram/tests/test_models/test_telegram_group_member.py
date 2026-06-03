import pytest

from django.db import transaction, IntegrityError

from django_telegram.models import (
    TelegramUser,
    TelegramChat,
    TelegramGroupMember,
)


@pytest.fixture
def telegram_user():
    return TelegramUser.objects.create(
        id=123,
        username="fooman",
    )


@pytest.fixture
def telegram_chat():
    return TelegramChat.objects.create(
        id=456,
        chat_type=TelegramChat.ChatType.GROUP,
        title="Foo Test Group",
    )


class TestTelegramGroupMember:
    """
    Tests for the TelegramGroupMember model.
    """

    pytestmark = pytest.mark.django_db

    def test_create_member(self, telegram_user, telegram_chat):
        """
        Create a TelegramGroupMember object and check its attribute values.
        """
        member = TelegramGroupMember.objects.create(
            user=telegram_user,
            chat=telegram_chat,
            role=TelegramGroupMember.GroupRole.MEMBER,
        )
        assert member.user == telegram_user
        assert member.chat == telegram_chat
        assert member.role == TelegramGroupMember.GroupRole.MEMBER
        assert member.is_active is True
        assert member.points == 0
        assert member.joined_at is not None
        assert member.left_at is None
        assert member.created_at is not None
        assert member.updated_at is not None

    @pytest.mark.parametrize(
        "role",
        TelegramGroupMember.GroupRole.values,
        ids=TelegramGroupMember.GroupRole.values,
    )
    def test_role_choices(self, telegram_user, telegram_chat, role):
        """
        The TelegramChatMember enum values can be saved and retrieved correctly.
        """
        member = TelegramGroupMember.objects.create(
            user=telegram_user, chat=telegram_chat, role=role
        )
        assert member.role == role

    def test_unique_constraint(self, telegram_user, telegram_chat):
        """
        User and chat are unique together.
        """
        TelegramGroupMember.objects.create(
            user=telegram_user,
            chat=telegram_chat,
            role=TelegramGroupMember.GroupRole.MEMBER,
        )
        # Attempt to create another group member with the same
        # user and chat
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                TelegramGroupMember.objects.create(
                    user=telegram_user,
                    chat=telegram_chat,
                    role=TelegramGroupMember.GroupRole.ADMIN,
                )
        # Sanity check to make sure no faulty group member was created.
        assert TelegramGroupMember.objects.count() == 1

    def test_str_representation(self, telegram_user, telegram_chat):
        """
        __str__ returns f"{member.user} in {member.chat} ({member.role})"
        """
        member = TelegramGroupMember.objects.create(
            user=telegram_user,
            chat=telegram_chat,
            role=TelegramGroupMember.GroupRole.ADMIN,
        )
        assert str(member) == f"{member.user} in {member.chat} ({member.role})"
