import pytest

from django_telegram.models import TelegramChat


class TestTelegramChat:
    """
    Tests for the TelegramChat model.
    """

    pytestmark = pytest.mark.django_db

    def test_pk(self):
        """
        id is the primary key
        """
        assert TelegramChat._meta.pk.name == "id"

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

    def test_create_chat(self):
        """
        Create a TelegramChat object and check its attribute values.
        """
        chat = TelegramChat.objects.create(
            id=456,
            chat_type=TelegramChat.ChatType.GROUP,
            title="Foo Group",
        )
        assert chat.id == 456
        assert chat.title == "Foo Group"
        assert chat.chat_type == TelegramChat.ChatType.GROUP
        assert chat.created_at is not None
        assert chat.updated_at is not None

    def test_str_representation(self):
        """
        __str__ returns "chat_type: id".
        """
        chat = TelegramChat.objects.create(
            id=456,
            chat_type=TelegramChat.ChatType.GROUP,
            title="Foo Group",
        )
        assert str(chat) == f"{chat.title}: {chat.id}"
