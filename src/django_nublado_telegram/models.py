from html import escape
from telegram import User, Chat, ChatMember
from telegram.constants import ChatType, ChatMemberStatus

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_nublado_core.models import TimestampModel, LanguageModel
from .managers import (
    TelegramUserManager,
    TelegramChatManager,
    TelegramGroupMemberManager,
)


class TelegramUser(TimestampModel):
    """
    Model for a Telegram user.
    """
    # Telegram id
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_bot = models.BooleanField(default=False)

    objects = TelegramUserManager()

    def __str__(self):
        return f"{self.display_name} : {str(self.id)}"

    @property
    def display_name(self):
        if self.username:
            name = f"@{self.username}"
        else:
            if self.last_name:
                name = f"{self.first_name} {self.last_name}"
            else:
                name = self.first_name
        return name

    def update_snapshot(self, tg_user: User) -> list[str]:
        """
        Update fields derived from telegram user and return a list
        of the field names that have been updated.
        """
        updated_fields = []

        if self.username != tg_user.username:
            self.username = tg_user.username
            updated_fields.append("username")

        if self.first_name != tg_user.first_name:
            self.first_name = tg_user.first_name
            updated_fields.append("first_name")

        if self.last_name != tg_user.last_name:
            self.last_name = tg_user.last_name
            updated_fields.append("last_name")

        if self.is_bot != tg_user.is_bot:
            self.is_bot = tg_user.is_bot
            updated_fields.append("is_bot")

        if updated_fields:
            self.save(update_fields=updated_fields)

        return updated_fields


class TelegramChat(TimestampModel):
    """
    Model for a Telegram chat
    """

    class ChatType(models.TextChoices):
        UNKNOWN = "unknown", _("Unknown")
        PRIVATE = ChatType.PRIVATE, _("private")
        GROUP = ChatType.GROUP, _("group")
        SUPERGROUP = ChatType.SUPERGROUP, _("supergroup")
        CHANNEL = ChatType.CHANNEL, _("channel")

    # Telegram id
    id = models.BigIntegerField(primary_key=True)

    # These fields are "snapshots" of their respective values derived from Telegram.
    chat_type = models.CharField(max_length=20, choices=ChatType)
    title = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    objects = TelegramChatManager()

    def __str__(self):
        return f"{self.title}: {self.id}"

    def update_snapshot(self, tg_chat: Chat) -> list[str]:
        """
        Update fields derived from telegram chat and return a list
        of the field names that have been updated.
        """
        updated_fields = []

        if self.chat_type != tg_chat.type:
            self.chat_type = tg_chat.type
            updated_fields.append("chat_type")

        if self.title != tg_chat.title:
            self.title = tg_chat.title
            updated_fields.append("title")

        if self.username != tg_chat.username:
            self.username = tg_chat.username
            updated_fields.append("username")

        if updated_fields:
            self.save(update_fields=updated_fields)

        return updated_fields


class TelegramGroupSettings(LanguageModel, TimestampModel):
    chat = models.OneToOneField(
        TelegramChat,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    def __str__(self):
        return f"Settings: {self.chat} (language={self.language})"


class TelegramGroupMember(TimestampModel):
    """
    Model for a member of a Telegram group.
    """

    class GroupRole(models.TextChoices):
        MEMBER = ChatMemberStatus.MEMBER, _("member")
        ADMIN = ChatMemberStatus.ADMINISTRATOR, _("admin")
        OWNER = ChatMemberStatus.OWNER, _("owner")

    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    chat = models.ForeignKey(
        TelegramChat,
        on_delete=models.CASCADE,
        related_name="members",
    )

    # This is just a "snapshot" of the group member's role. Don't
    # use it for permissions. Rather, use the role data from Telegram
    # that this field is derived from.
    role = models.CharField(max_length=20, choices=GroupRole)

    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    # Optional for group "karma points." This can be extracted to its own
    # table if more elaborate point features are needed.
    points = models.IntegerField(default=0)

    objects = TelegramGroupMemberManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "chat"], name="unique_group_membership"
            )
        ]
        indexes = [
            models.Index(fields=["chat", "-points"]),
        ]

    def __str__(self):
        return f"{self.user} in {self.chat} ({self.role})"

    @property
    def mention_html(self):
        display_name = escape(self.user.display_name)
        return f'<a href="tg://user?id={self.user.id}">{display_name}</a>'


    def update_snapshot(self, tg_member: ChatMember) -> list[str]:
        updated_fields = []

        role = tg_member.status
        is_active = True

        if role not in self.GroupRole.values:
            is_active = False
            role = self.GroupRole.MEMBER

        if self.role != role:
            self.role = role
            updated_fields.append("role")

        if self.is_active != is_active:
            self.is_active = is_active
            updated_fields.append("is_active")

            if not is_active and self.left_at is None:
                self.left_at = timezone.now()
                updated_fields.append("left_at")

            if is_active:
                self.left_at = None
                updated_fields.append("left_at")

        if updated_fields:
            self.save(update_fields=updated_fields)

        return updated_fields