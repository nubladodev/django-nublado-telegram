from abc import ABC, abstractmethod
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop

from .utils.helpers import is_group, is_private, is_admin, is_group_owner, is_bot_owner
from .bot_messages import BOT_MESSAGES


class HandlerPolicy(ABC):
    async def _reply(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str
    ):
        tg_chat = update.effective_chat
        tg_message = update.effective_message

        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(message),
            reply_to_message_id=tg_message.message_id,
        )

    async def _reply_and_block(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str
    ) -> bool:
        tg_chat = update.effective_chat
        tg_message = update.effective_message

        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(message),
            reply_to_message_id=tg_message.message_id,
        )
        return False

    @abstractmethod
    async def check(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:
        """
        Return True to allow execution, False to block it.
        Policies may send replies before returning False.
        """
        ...


class GroupOnly(HandlerPolicy):
    async def check(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:
        tg_chat = update.effective_chat
        if not tg_chat or not is_group(tg_chat):
            return await self._reply_and_block(
                update, context, BOT_MESSAGES["error.group_only"]
            )
        return True


class PrivateOnly(HandlerPolicy):
    async def check(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:
        tg_chat = update.effective_chat
        if not tg_chat or not is_private(tg_chat):
            return await self._reply_and_block(
                update, context, BOT_MESSAGES["error.private_only"]
            )
        return True


class BotOwnerOnly(HandlerPolicy):
    async def check(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:

        tg_chat = update.effective_chat
        tg_user = update.effective_user

        if not tg_chat or not tg_user:
            return False

        if not is_bot_owner(tg_user):
            return await self._reply_and_block(
                update,
                context,
                BOT_MESSAGES["error.bot_owner_access"],
            )

        return True


class AdminOnly(HandlerPolicy):
    async def check(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:

        tg_chat = update.effective_chat
        tg_user = update.effective_user

        if not tg_chat or not tg_user:
            return False

        try:
            tg_member = await context.bot.get_chat_member(tg_chat.id, tg_user.id)
        except Exception:
            return await self._reply_and_block(
                update,
                context,
            )

        if not is_admin(tg_member):
            return await self._reply_and_block(
                update,
                context,
                BOT_MESSAGES["error.admin_access"],
            )

        return True


class GroupOwnerOnly(HandlerPolicy):
    async def check(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:

        tg_chat = update.effective_chat
        tg_user = update.effective_user

        if not tg_chat or not is_group(tg_chat):
            return await self._reply_and_block(
                update, context, BOT_MESSAGES["error.group_only"]
            )

        if not tg_user:
            return False

        try:
            tg_member = await context.bot.get_chat_member(tg_chat.id, tg_user.id)
        except Exception:
            return await self._reply_and_block(
                update, context, "Could not verify owner status."
            )

        if not is_group_owner(tg_member):
            return await self._reply_and_block(
                update,
                context,
                BOT_MESSAGES["error.group_owner_access"],
            )

        return True


def with_policies(*policy_classes):
    def decorator(callback):

        policies = [p() for p in policy_classes]

        @wraps(callback)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):

            for policy in policies:
                allowed = await policy.check(update, context)
                if not allowed:
                    raise ApplicationHandlerStop

            return await callback(update, context)

        return wrapped

    return decorator
