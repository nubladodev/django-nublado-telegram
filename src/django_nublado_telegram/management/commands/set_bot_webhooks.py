import asyncio
import logging

from django.core.management.base import BaseCommand

from django_telegram.bot_registry import registry

logger = logging.getLogger("django")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        asyncio.run(self.run())

    async def run(self):
        for bot in registry.all():
            await bot.ensure_webhook()
