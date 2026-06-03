import logging


from .bot import TelegramBot

logger = logging.getLogger("django")


class BotRegistry:
    def __init__(self):
        self._bots: dict[str, TelegramBot] = {}

    def register(self, name: str, bot: TelegramBot):
        self._bots[name] = bot

    def get(self, name: str) -> TelegramBot:
        try:
            return self._bots[name]
        except KeyError:
            raise ValueError(f"Bot '{name}' not found")

    def all(self):
        return self._bots.values()


registry = BotRegistry()
