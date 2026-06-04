from types import SimpleNamespace

import pytest

from django_nublado_telegram.models import TelegramUser

from ..support.factories import TelegramUserFactory


class TestTelegramUser:
    """
    Tests for the TelegramUser model.
    """

    def test_pk(self):
        """
        id is the primary key
        """
        assert TelegramUser._meta.pk.name == "id"

    @pytest.mark.django_db
    def test_create_user_defaults(self):
        """
        Create a TelegramUser object and check its default values.
        """
        user = TelegramUser.objects.create(id=1)
        assert user.id == 1
        assert user.is_bot is False
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "initial, incoming, expected_fields, expected_state",
        [
            # No change
            (
                dict(username="alice", first_name="Alice", last_name="Smith", is_bot=False),
                dict(username="alice", first_name="Alice", last_name="Smith", is_bot=False),
                [],
                dict(username="alice", first_name="Alice", last_name="Smith", is_bot=False),
            ),

            # Username change
            (
                dict(username="old", first_name="Alice", last_name="Smith", is_bot=False),
                dict(username="new", first_name="Alice", last_name="Smith", is_bot=False),
                ["username"],
                dict(username="new", first_name="Alice", last_name="Smith", is_bot=False),
            ),

            # First name change
            (
                dict(username="alice", first_name="Old", last_name="Smith", is_bot=False),
                dict(username="alice", first_name="New", last_name="Smith", is_bot=False),
                ["first_name"],
                dict(username="alice", first_name="New", last_name="Smith", is_bot=False),
            ),

            # Last name change
            (
                dict(username="alice", first_name="Alice", last_name="Old", is_bot=False),
                dict(username="alice", first_name="Alice", last_name="New", is_bot=False),
                ["last_name"],
                dict(username="alice", first_name="Alice", last_name="New", is_bot=False),
            ),

            # Bot flag change
            (
                dict(username="alice", first_name="Alice", last_name="Smith", is_bot=False),
                dict(username="alice", first_name="Alice", last_name="Smith", is_bot=True),
                ["is_bot"],
                dict(username="alice", first_name="Alice", last_name="Smith", is_bot=True),
            ),

            # Multiple changes
            (
                dict(username="old", first_name="Old", last_name="Old", is_bot=False),
                dict(username="new", first_name="New", last_name="New", is_bot=True),
                ["username", "first_name", "last_name", "is_bot"],
                dict(username="new", first_name="New", last_name="New", is_bot=True),
            ),
        ],
    )
    def test_update_snapshot(self, initial, incoming, expected_fields, expected_state):
        user = TelegramUserFactory(**initial)

        tg_user = SimpleNamespace(**incoming)

        updated = user.update_snapshot(tg_user)

        # 1. Check returned diff
        assert set(updated) == set(expected_fields)

        # 2. Reload from DB (important — verifies persistence)
        user.refresh_from_db()

        # 3. Check final state
        for field, value in expected_state.items():
            assert getattr(user, field) == value


    @pytest.mark.django_db
    def test_str_representation(self):
        """
        __str__ returns username and id.
        """
        user = TelegramUserFactory(username="bob")
        assert str(user) == f"{user.display_name} : {user.id}"

    @pytest.mark.django_db
    def test_display_name_username(self):
        user = TelegramUserFactory(username="bob")
        assert user.display_name == "@bob"

    @pytest.mark.django_db
    def test_display_name_full_name(self):
        user = TelegramUserFactory(username=None, first_name="Bob", last_name="Smith")
        assert user.display_name == "Bob Smith"

    @pytest.mark.django_db
    def test_display_name_first_only(self):
        user = TelegramUserFactory(username=None, last_name=None, first_name="Bob")
        assert user.display_name == "Bob"