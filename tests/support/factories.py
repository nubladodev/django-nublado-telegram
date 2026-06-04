import factory

from django.utils import timezone

from django_nublado_telegram.models import (
    TelegramUser,
    TelegramChat,
    TelegramGroupMember,
)


class TelegramUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TelegramUser

    id = factory.Sequence(lambda n: 10**12 + n)
    username = factory.Sequence(lambda n: f"foouser{n}")


class TelegramChatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TelegramChat

    id = factory.Sequence(lambda n: 10**12 + n)  # safe, deterministic uniqueness

    chat_type = TelegramChat.ChatType.GROUP
    title = factory.Sequence(lambda n: f"Test Chat {n}")


class TelegramGroupMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TelegramGroupMember

    user = factory.SubFactory(TelegramUserFactory)
    chat = factory.SubFactory(TelegramChatFactory)

    role = TelegramGroupMember.GroupRole.MEMBER
    is_active = True

    joined_at = factory.LazyFunction(timezone.now)
    left_at = None
    points = 0