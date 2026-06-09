import asyncio
from unittest.mock import AsyncMock

import pytest
from telegram.ext import Application, Defaults

from django_nublado_telegram.bot import create_app, TelegramBot


class TestCreateApp:

    def test_create_app(self):
        app = create_app("fake-token")

        assert isinstance(app, Application)

    def test_create_app_with_defaults(self, mocker):
        builder = mocker.Mock()

        builder.token.return_value = builder
        builder.defaults.return_value = builder
        builder.build.return_value = "app"

        mocker.patch(
            "django_nublado_telegram.bot.Application.builder",
            return_value=builder,
        )

        defaults = Defaults(parse_mode="HTML")

        app = create_app(
            "fake-token",
            defaults=defaults,
        )

        builder.token.assert_called_once_with("fake-token")
        builder.defaults.assert_called_once_with(defaults)
        builder.build.assert_called_once()

        assert app == "app"

    def test_create_app_with_post_init(self):
        async def post_init(app):
            pass

        app = create_app(
            "fake-token",
            post_init=post_init,
        )

        assert app.post_init is post_init


class TestTelegramBot:
    def test_telegram_bot_init(self, mocker):
        app = mocker.Mock()
        bot_name = "test"
        webhook_url = "https://example.com/webhook"

        bot = TelegramBot(
            name=bot_name,
            application=app,
            webhook_url=webhook_url
        )

        assert bot.app is app
        assert bot.name == bot_name
        assert bot.webhook_url == webhook_url
        assert bot.webhook_token is None
        assert bot._initialized is False
        assert bot._webhook_set is False

    @pytest.mark.asyncio
    async def test_ensure_initialized(self, mocker):
        app = mocker.Mock()
        app.initialize = AsyncMock()
        app.start = AsyncMock()

        bot = TelegramBot(
            name="test_bot",
            application=app,
            webhook_url="https://example.com/webhook",
        )

        await bot.ensure_initialized()

        app.initialize.assert_awaited_once()
        app.start.assert_awaited_once()

        assert bot._initialized is True

    @pytest.mark.asyncio
    async def test_ensure_initialized_only_runs_once(self, mocker):
        app = mocker.Mock()
        app.initialize = AsyncMock()
        app.start = AsyncMock()

        bot = TelegramBot(
            name="test_bot",
            application=app,
            webhook_url="https://example.com/webhook",
        )

        await bot.ensure_initialized()
        await bot.ensure_initialized()

        app.initialize.assert_awaited_once()
        app.start.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_ensure_initialized_concurrent(self, mocker):
        app = mocker.Mock()
        app.initialize = AsyncMock()
        app.start = AsyncMock()

        bot = TelegramBot(
            name="test_bot",
            application=app,
            webhook_url="https://example.com/webhook",
        )

        await asyncio.gather(
            bot.ensure_initialized(),
            bot.ensure_initialized(),
            bot.ensure_initialized(),
        )

        app.initialize.assert_awaited_once()
        app.start.assert_awaited_once()

        assert bot._initialized is True

    @pytest.mark.asyncio
    async def test_ensure_webhook(self, mocker):
        app = mocker.Mock()
        app.bot = mocker.Mock()
        app.bot.token = "fake-token"

        mock_bot_class = mocker.patch(
            "django_nublado_telegram.bot.Bot",
            autospec=True,
        )

        bot_instance = mock_bot_class.return_value
        bot_instance.set_webhook = AsyncMock()

        bot = TelegramBot(
            name="test_bot",
            application=app,
            webhook_url="https://example.com/webhook",
            webhook_token="secret",
        )

        await bot.ensure_webhook()

        bot_instance.set_webhook.assert_awaited_once_with(
            url="https://example.com/webhook",
            secret_token="secret",
            drop_pending_updates=False,
        )

        assert bot._webhook_set is True

    @pytest.mark.asyncio
    async def test_ensure_webhook_only_runs_once(self, mocker):
        app = mocker.Mock()
        app.bot = mocker.Mock()
        app.bot.token = "fake-token"

        mock_bot_class = mocker.patch(
            "django_nublado_telegram.bot.Bot",
            autospec=True,
        )

        bot_instance = mock_bot_class.return_value
        bot_instance.set_webhook = AsyncMock()

        bot = TelegramBot(
            name="test_bot",
            application=app,
            webhook_url="https://example.com/webhook",
        )

        await bot.ensure_webhook()
        await bot.ensure_webhook()

        bot_instance.set_webhook.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_process_update(self, mocker):
        update = object()

        app = mocker.Mock()
        app.process_update = AsyncMock()

        bot = TelegramBot(
            name="test_bot",
            application=app,
            webhook_url="https://example.com/webhook",
        )

        bot.ensure_initialized = AsyncMock()

        await bot.process_update(update)

        bot.ensure_initialized.assert_awaited_once()
        app.process_update.assert_awaited_once_with(update)