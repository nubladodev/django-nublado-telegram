from telegram import User, Chat

from django.db import models


class TelegramUserQuerySet(models.QuerySet):
    """
    QuerySet for TelegramUserManager
    """


class TelegramUserManager(models.Manager.from_queryset(TelegramUserQuerySet)):
    """
    Manager for TelegramUser
    """
    def get_or_create_from_user(self, tg_user: User):
        """
        Get or create a TelegramUser object from telegram.User.
        """
        user, created = self.get_or_create(
            id=tg_user.id,
            defaults={
                "username": tg_user.username,
                "first_name": tg_user.first_name,
                "last_name": tg_user.last_name,
                "is_bot": tg_user.is_bot,
            },
        )
        if not created:
            # Update snapshot fields in db.
            updated_fields = user.update_snapshot(tg_user)

        return user, created


class TelegramChatQuerySet(models.QuerySet):
    """
    QuerySet for TelegramChatManager
    """


class TelegramChatManager(models.Manager.from_queryset(TelegramChatQuerySet)):
    """
    Manager for TelegramChat
    """
    def get_or_create_from_chat(self, tg_chat: Chat):
        """
        Get or create a TelegramChat object from telegram.Chat.
        """

        chat, created = self.get_or_create(
            id=tg_chat.id,
            defaults={
                "chat_type": tg_chat.type,
                "title": tg_chat.title,
                "username": tg_chat.username,
            },
        )
        if not created:
            # Update snapshot fields in db.
            updated_fields = chat.update_snapshot(tg_chat)

        return chat, created


    def get_or_create_from_chat_id(self, chat_id: int):
        """
        Get or create a TelegramChat object from a chat_id.
        """

        chat, created = self.get_or_create(
            id=chat_id,
            defaults={
                "chat_type": self.model.ChatType.UNKNOWN,
                "title": None,
                "username": None,
            },
        )
        return chat, created


class TelegramGroupMemberQuerySet(models.QuerySet):
    """
    QuerySet for TelegramGroupMemberManager
    """


class TelegramGroupMemberManager(
    models.Manager.from_queryset(TelegramGroupMemberQuerySet)
):
    """
    Manager for TelegramGroupMember
    """
    def get_or_create_from_chat_member(self, tg_member, tg_chat):
        from django_telegram.models import (
            TelegramUser,
            TelegramChat,
            TelegramGroupMember,
        )

        role = tg_member.status
        is_active = True

        if role not in TelegramGroupMember.GroupRole.values:
            is_active = False
            role = TelegramGroupMember.GroupRole.MEMBER

        tg_user = tg_member.user

        # This updates snapshot fields in the ORM.
        user, created = TelegramUser.objects.get_or_create_from_user(tg_user)
        chat, created = TelegramChat.objects.get_or_create_from_chat(tg_chat)

        member, created = self.get_or_create(
            user=user,
            chat=chat,
            defaults={
                "role": role,
                "is_active": is_active,
            },
        )

        # Update snapshot fields.
        if not created:
            updated_fields = member.update_snapshot(tg_member)

        return member, created
