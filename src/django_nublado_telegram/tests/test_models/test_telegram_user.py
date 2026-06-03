import pytest

from django_telegram.models import TelegramUser


class TestTelegramUser:
    """
    Tests for the TelegramUser model.
    """

    pytestmark = pytest.mark.django_db

    def test_pk(self):
        """
        id is the primary key
        """
        assert TelegramUser._meta.pk.name == "id"

    def test_create_user_defaults(self):
        """
        Create a TelegramUser object and check its default values.
        """
        user = TelegramUser.objects.create(id=1)
        assert user.id == 1
        assert user.is_bot is False
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_display_name(self):
        # With username.
        user = TelegramUser.objects.create(
            id=222, username="username2", first_name="firstname2"
        )
        assert user.display_name == f"@{user.username}"

        # No username, with first_name and last_name
        user = TelegramUser.objects.create(
            id=333, first_name="firstname3", last_name="lastname3"
        )
        assert user.display_name == f"{user.first_name} {user.last_name}"

        # No username, with first_name and no last_name.
        user = TelegramUser.objects.create(id=444, first_name="firstname4")
        assert user.display_name == user.first_name

    def test_str_representation(self):
        """
        __str__ returns username, or id if username doesn't exist.
        """
        user = TelegramUser.objects.create(
            id=111, first_name="foo", username="foo"
        )
        assert str(user) == f"{user.display_name} : {user.id}"
