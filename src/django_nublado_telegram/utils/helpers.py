from telegram import Chat, ChatMember, User
from telegram.constants import ChatType, ChatMemberStatus

from django.conf import settings


# Helper functions
def is_group(tg_chat: Chat):
    return tg_chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}


def is_private(tg_chat: Chat):
    return tg_chat.type == ChatType.PRIVATE


def is_admin(tg_member: ChatMember):
    return tg_member.status in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ]


def is_group_owner(tg_member: ChatMember):
    return tg_member.status == ChatMemberStatus.OWNER


def is_bot_owner(tg_user: User):
    return tg_user.id == settings.NUBLADO_BOT_OWNER_ID


def message_link(tg_chat_id: str, tg_message_id: str):
    tg_chat_id = str(tg_chat_id)

    if tg_chat_id.startswith("-100"):
        tg_chat_id = tg_chat_id[4:]

    return f"https://t.me/c/{tg_chat_id}/{tg_message_id}"
