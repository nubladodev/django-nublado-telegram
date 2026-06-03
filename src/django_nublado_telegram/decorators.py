from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from django.utils.translation import override

from .utils.language import get_context_language


def with_language(handler):
    @wraps(handler)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        language_code = get_context_language(context)

        with override(language_code):
            return await handler(update, context, *args, **kwargs)

    return wrapper
