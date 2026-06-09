
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from django_nublado_telegram.models import TelegramUser
from ..support.factories import TelegramUserFactory


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
