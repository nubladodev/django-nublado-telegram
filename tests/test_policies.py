import pytest

from telegram.ext import ContextTypes, ApplicationHandlerStop

from django_nublado_telegram.policies import (
    GroupOnly,
    AdminOnly,
    GroupOwnerOnly,
    with_policies
)


class TestGroupOnly:

    @pytest.mark.asyncio
    async def test_allows_group(self, mocker):
        policy = GroupOnly()

        update = mocker.Mock()
        update.effective_chat = mocker.Mock(id=1)

        context = mocker.Mock()

        mocker.patch(
            "django_nublado_telegram.policies.is_group",
            return_value=True,
        )

        result = await policy.check(update, context)

        assert result is True

    @pytest.mark.asyncio
    async def test_blocks_non_group(self, mocker):
        policy = GroupOnly()

        update = mocker.Mock()
        update.effective_chat = mocker.Mock(id=1)

        context = mocker.Mock()
        context.bot.send_message = mocker.AsyncMock()

        mocker.patch(
            "django_nublado_telegram.policies.is_group",
            return_value=False,
        )

        result = await policy.check(update, context)

        assert result is False
        context.bot.send_message.assert_awaited()


class TestAdminOnly:

    @pytest.mark.asyncio
    async def test_admin_allowed(self, mocker):
        policy = AdminOnly()

        update = mocker.Mock()
        update.effective_chat = mocker.Mock(id=1)
        update.effective_user = mocker.Mock(id=2)

        context = mocker.Mock()
        context.bot.get_chat_member = mocker.AsyncMock()

        member = mocker.Mock()
        context.bot.get_chat_member.return_value = member

        mocker.patch(
            "django_nublado_telegram.policies.is_admin",
            return_value=True,
        )

        result = await policy.check(update, context)

        assert result is True

    @pytest.mark.asyncio
    async def test_non_admin_blocked(self, mocker):
        policy = AdminOnly()

        update = mocker.Mock()
        update.effective_chat = mocker.Mock(id=1)
        update.effective_user = mocker.Mock(id=2)

        context = mocker.Mock()
        context.bot.send_message = mocker.AsyncMock()
        context.bot.get_chat_member = mocker.AsyncMock()

        member = mocker.Mock()
        context.bot.get_chat_member.return_value = member

        mocker.patch(
            "django_nublado_telegram.policies.is_admin",
            return_value=False,
        )

        result = await policy.check(update, context)

        assert result is False
        context.bot.send_message.assert_awaited()


class TestGroupOwnerOnly:

    @pytest.mark.asyncio
    async def test_group_owner_allowed(self, mocker):
        policy = GroupOwnerOnly()

        update = mocker.Mock()
        update.effective_chat = mocker.Mock(id=1)
        update.effective_user = mocker.Mock(id=2)

        context = mocker.Mock()
        context.bot.get_chat_member = mocker.AsyncMock()

        member = mocker.Mock()
        context.bot.get_chat_member.return_value = member

        mocker.patch(
            "django_nublado_telegram.policies.is_group",
            return_value=True,
        )
        mocker.patch(
            "django_nublado_telegram.policies.is_group_owner",
            return_value=True,
        )

        result = await policy.check(update, context)

        assert result is True

    @pytest.mark.asyncio
    async def test_non_group_owner_blocked(self, mocker):
        policy = GroupOwnerOnly()

        update = mocker.Mock()
        update.effective_chat = mocker.Mock(id=1)
        update.effective_user = mocker.Mock(id=2)

        context = mocker.Mock()
        context.bot.send_message = mocker.AsyncMock()
        context.bot.get_chat_member = mocker.AsyncMock()

        member = mocker.Mock()
        context.bot.get_chat_member.return_value = member

        mocker.patch(
            "django_nublado_telegram.policies.is_group",
            return_value=True,
        )
        mocker.patch(
            "django_nublado_telegram.policies.is_group_owner",
            return_value=False,
        )

        result = await policy.check(update, context)

        assert result is False
        context.bot.send_message.assert_awaited()


class TestWithPolicies:

    @pytest.mark.asyncio
    async def test_with_policies_allows(self, mocker):
        @with_policies(GroupOnly)
        async def handler(update, context):
            return "ok"

        update = mocker.Mock()
        context = mocker.Mock()

        mocker.patch(
            "django_nublado_telegram.policies.GroupOnly.check",
            return_value=True,
        )

        result = await handler(update, context)

        assert result == "ok"

    @pytest.mark.asyncio
    async def test_with_policies_blocks(self, mocker):
        @with_policies(GroupOnly)
        async def handler(update, context):
            return "should_not_run"

        update = mocker.Mock()
        context = mocker.Mock()

        mocker.patch(
            "django_nublado_telegram.policies.GroupOnly.check",
            return_value=False,
        )

        with pytest.raises(ApplicationHandlerStop):
            await handler(update, context)