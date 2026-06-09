import json

import pytest

from django.http import Http404

from django_nublado_telegram.views import BotWebhookView
from django_nublado_telegram.bot_registry import registry


class TestBotWebhookView:

    @pytest.mark.asyncio
    async def test_webhook_success(self, mocker, rf):
        bot = mocker.Mock()
        bot.app.bot = mocker.Mock()
        bot.process_update = mocker.AsyncMock()
        bot_slug = "test-id"
        registry.get = mocker.Mock(return_value=bot)

        payload = {"update_id": 1}

        request = rf.post(
            f"/webhook/{bot_slug}/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        response = await BotWebhookView.as_view()(request, bot_id=bot_slug)

        bot.process_update.assert_awaited_once()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_webhook_unknown_bot(self, mocker, rf):
        registry.get = mocker.Mock(side_effect=ValueError)

        request = rf.post(
            "/webhook/test/",
            data="{}",
            content_type="application/json",
        )

        with pytest.raises(Http404):
           await BotWebhookView.as_view()(request, bot_id="test")

    @pytest.mark.asyncio
    async def test_webhook_invalid_json(self, mocker, rf):
        bot = mocker.Mock()
        registry.get = mocker.Mock(return_value=bot)

        request = rf.post(
            "/webhook/test/",
            data="not-json",
            content_type="application/json",
        )

        with pytest.raises(Http404):
           await BotWebhookView.as_view()(request, bot_id="test")