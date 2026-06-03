import json
import logging

from telegram import Update

from django.http import Http404, JsonResponse
from django.views import View

from .bot_registry import registry

logger = logging.getLogger("django")


class BotWebhookView(View):
    async def post(self, request, *args, **kwargs):
        bot_id = kwargs["bot_id"]

        try:
            bot = registry.get(bot_id)
        except ValueError:
            raise Http404

        try:
            data = json.loads(request.body.decode("utf-8"))
            update = Update.de_json(data, bot.app.bot)
        except Exception:
            raise Http404

        await bot.process_update(update)

        return JsonResponse({"ok": True})
