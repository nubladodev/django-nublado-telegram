import asyncio
import logging
from telegram.ext import Application, Defaults
from telegram import Bot

logger = logging.getLogger("django")


def create_app(
    bot_token, post_init=None, defaults: Defaults | None = None
) -> Application:

    builder = Application.builder().token(bot_token)

    if defaults is not None:
        builder = builder.defaults(defaults)

    if post_init is not None:
        builder = builder.post_init(post_init)

    return builder.build()


class TelegramBot:
    def __init__(
        self,
        name: str,
        application: Application,
        webhook_url: str,
        webhook_token: str | None = None,
    ):
        self.name = name
        self.app = application
        self.webhook_url = webhook_url
        self.webhook_token = webhook_token

        self._lock = asyncio.Lock()
        self._initialized = False
        self._webhook_set = False

    async def ensure_initialized(self):
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            logger.info(f"[{self.name}] Initializing bot...")
            await self.app.initialize()
            await self.app.start()

            self._initialized = True
            logger.info(f"[{self.name}] initialized.")

    async def ensure_webhook(self):
        if self._webhook_set:
            logger.info(f"[{self.name}] webhook already set.")
            return

        logger.info(f"Setting webhook for [{self.name}].")

        bot = Bot(self.app.bot.token)
        await bot.set_webhook(
            url=self.webhook_url,
            secret_token=self.webhook_token,
            drop_pending_updates=False,
        )

        self._webhook_set = True
        logger.info(f"[{self.name}] webhook set")

    async def process_update(self, update):
        await self.ensure_initialized()
        await self.app.process_update(update)
