import pytest

from django.db import transaction, IntegrityError
from django.conf import settings as django_settings

from django_nublado_telegram.models import TelegramGroupSettings
from ..support.factories import TelegramChatFactory


class TestTelegramGroupSettings:
    """
    Tests for the TelegramGroupSettings model.
    """

    @pytest.mark.django_db
    def test_create_group_settings(self):
        """
        Create a TelegramGroupSettings object for a chat.
        """
        chat = TelegramChatFactory()
        group_settings = TelegramGroupSettings.objects.create(chat=chat)

        assert group_settings.chat == chat
        assert group_settings.created_at is not None
        assert group_settings.updated_at is not None
        assert group_settings.language == django_settings.LANGUAGE_CODE

        group_settings.refresh_from_db()
        assert group_settings.updated_at >= group_settings.created_at

    @pytest.mark.django_db
    def test_one_to_one_constraint(self):
        """
        There can only be one settings per chat.
        """
        chat = TelegramChatFactory()
        # Create a settings object for a chat.
        TelegramGroupSettings.objects.create(chat=chat)

        # Attempt to create another settings object for the same chat
        # and fail.
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                TelegramGroupSettings.objects.create(chat=chat)

        # Sanity check to make sure only one settings object was created.
        assert TelegramGroupSettings.objects.filter(chat=chat).count() == 1

    @pytest.mark.django_db
    def test_str_representation(self):
        """
        __str__ returns f"Settings: {chat} (language={language})"
        """
        chat = TelegramChatFactory()
        group_settings = TelegramGroupSettings.objects.create(chat=chat)
        assert (
            str(group_settings)
            == f"Settings: {group_settings.chat} (language={group_settings.language})"
        )
