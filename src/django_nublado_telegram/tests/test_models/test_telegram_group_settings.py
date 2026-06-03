import pytest

from django.db import transaction, IntegrityError
from django.conf import settings as django_settings

from django_telegram.models import TelegramChat, TelegramGroupSettings


@pytest.fixture
def telegram_chat():
    return TelegramChat.objects.create(
        id=456,
        chat_type=TelegramChat.ChatType.GROUP,
        title="Foo Test Group",
    )


class TestTelegramGroupSettings:
    """
    Tests for the TelegramGroupSettings model.
    """

    pytestmark = pytest.mark.django_db

    def test_create_group_settings(self, telegram_chat):
        """
        Create a TelegramGroupSettings object for a chat.
        """
        group_settings = TelegramGroupSettings.objects.create(chat=telegram_chat)

        assert group_settings.chat == telegram_chat
        assert group_settings.created_at is not None
        assert group_settings.updated_at is not None
        assert group_settings.language == django_settings.LANGUAGE_CODE

        group_settings.refresh_from_db()
        assert group_settings.updated_at >= group_settings.created_at

    def test_one_to_one_constraint(self, telegram_chat):
        """
        There can only be one settings per chat.
        """
        # Create a settings object for a chat.
        TelegramGroupSettings.objects.create(chat=telegram_chat)

        # Attempt to create another settings object for the same chat
        # and fail.
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                TelegramGroupSettings.objects.create(chat=telegram_chat)

        # Sanity check to make sure only one settings object was created.
        assert TelegramGroupSettings.objects.count() == 1

    def test_str_representation(self, telegram_chat):
        """
        __str__ returns f"Settings: {chat} (language={language})"
        """
        group_settings = TelegramGroupSettings.objects.create(chat=telegram_chat)
        assert (
            str(group_settings)
            == f"Settings: {group_settings.chat} (language={group_settings.language})"
        )
