from types import SimpleNamespace

import pytest

from django_nublado_telegram.models import TelegramChat

from ..support.factories import TelegramChatFactory


class TestTelegramChat:
    """
    Tests for the TelegramChat model.
    """

    def test_pk(self):
        """
        id is the primary key
        """
        assert TelegramChat._meta.pk.name == "id"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "chat_type",
        TelegramChat.ChatType.values,
        ids=TelegramChat.ChatType.values,
    )
    def test_chat_type_choices(self, chat_type):
        """
        The ChatType enum values can be saved and retrieved correctly.
        """
        chat = TelegramChat.objects.create(
            id=1,
            chat_type=chat_type,
        )
        chat.refresh_from_db()
        assert chat.chat_type == chat_type

    @pytest.mark.django_db
    def test_create_chat(self):
        """
        Create a TelegramChat object and check its attribute values.
        """
        chat = TelegramChatFactory(title="Foo Group")
        assert chat.id is not None
        assert chat.title.startswith("Foo Group")
        assert chat.chat_type == TelegramChat.ChatType.GROUP
        assert chat.created_at is not None
        assert chat.updated_at is not None

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "initial, incoming, expected_fields, expected_state",
        [
            # No change
            (
                dict(
                    chat_type=TelegramChat.ChatType.GROUP,
                    title="Foo",
                    username="bar",
                ),
                dict(
                    type=TelegramChat.ChatType.GROUP,
                    title="Foo",
                    username="bar",
                ),
                [],
                dict(
                    chat_type=TelegramChat.ChatType.GROUP,
                    title="Foo",
                    username="bar",
                ),
            ),

            # chat_type change
            (
                dict(
                    chat_type=TelegramChat.ChatType.GROUP,
                    title="Foo",
                    username="bar",
                ),
                dict(
                    type=TelegramChat.ChatType.SUPERGROUP,
                    title="Foo",
                    username="bar",
                ),
                ["chat_type"],
                dict(
                    chat_type=TelegramChat.ChatType.SUPERGROUP,
                    title="Foo",
                    username="bar",
                ),
            ),

            # title change
            (
                dict(
                    chat_type=TelegramChat.ChatType.GROUP,
                    title="Old",
                    username="bar",
                ),
                dict(
                    type=TelegramChat.ChatType.GROUP,
                    title="New",
                    username="bar",
                ),
                ["title"],
                dict(
                    chat_type=TelegramChat.ChatType.GROUP,
                    title="New",
                    username="bar",
                ),
            ),

            # username change
            (
                dict(
                    chat_type=TelegramChat.ChatType.GROUP,
                    title="Foo",
                    username="old",
                ),
                dict(
                    type=TelegramChat.ChatType.GROUP,
                    title="Foo",
                    username="new",
                ),
                ["username"],
                dict(
                    chat_type=TelegramChat.ChatType.GROUP,
                    title="Foo",
                    username="new",
                ),
            ),

            # multiple changes
            (
                dict(
                    chat_type=TelegramChat.ChatType.GROUP,
                    title="Old",
                    username="old",
                ),
                dict(
                    type=TelegramChat.ChatType.CHANNEL,
                    title="New",
                    username="new",
                ),
                ["chat_type", "title", "username"],
                dict(
                    chat_type=TelegramChat.ChatType.CHANNEL,
                    title="New",
                    username="new",
                ),
            ),
        ],
    )
    def test_update_snapshot(self, initial, incoming, expected_fields, expected_state):
        chat = TelegramChatFactory(**initial)

        tg_chat = SimpleNamespace(**incoming)

        updated = chat.update_snapshot(tg_chat)

        # 1. diff contract
        assert set(updated) == set(expected_fields)

        # 2. persistence contract
        chat.refresh_from_db()

        for field, value in expected_state.items():
            assert getattr(chat, field) == value

    @pytest.mark.django_db
    def test_str_representation(self):
        """
        __str__ returns "chat_type: id".
        """
        chat = TelegramChatFactory()
        assert str(chat) == f"{chat.title}: {chat.id}"
