from django.core.management.base import BaseCommand
from django.conf import settings

from ...bot_registry import registry


class Command(BaseCommand):
    help = "Run telegram bots in polling mode"

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str)

    def handle(self, *args, **options):
        if settings.DJANGO_TELEGRAM_BOT_MODE == settings.BOT_MODE_POLLING:
            if options["name"]:
                bot_name = options["name"]
                bot = registry.get(bot_name)
                self.stdout.write(
                    self.style.SUCCESS(f"Now starting bot {bot.name} in polling mode.")
                )
                bot.app.run_polling()
            else:
                for bot in registry.all():
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Now starting bot {bot.name} in polling mode."
                        )
                    )
                    bot.app.run_polling()
