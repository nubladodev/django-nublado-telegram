import pytest

from django.core.exceptions import ImproperlyConfigured

from django_nublado_telegram.conf.app_settings import (
    AppData,
    BotMode,
    app_settings
)


class TestAppData:

    def test_bot_mode_string_converted_to_enum(self):
        data = AppData(BOT_MODE="webhook")

        assert data.BOT_MODE is BotMode.WEBHOOK

    def test_bot_mode_accepts_enum(self):
        data = AppData(BOT_MODE=BotMode.POLLING)

        assert data.BOT_MODE is BotMode.POLLING

    def test_invalid_bot_mode(self):
        with pytest.raises(ImproperlyConfigured):
            AppData(BOT_MODE="foo")


class TestAppSettings:

    def test_default_bot_mode(self):
        app_settings.reload()

        assert app_settings.BOT_MODE is BotMode.POLLING

    def test_override_bot_mode(self, settings):
        settings.DJANGO_NUBLADO_TELEGRAM["BOT_MODE"] = "webhook"
        app_settings.reload()

        assert app_settings.BOT_MODE is BotMode.WEBHOOK

    def test_invalid_override(self, settings):
        settings.DJANGO_NUBLADO_TELEGRAM["BOT_MODE"] = "foo"

        with pytest.raises(ImproperlyConfigured):
            app_settings.reload()

