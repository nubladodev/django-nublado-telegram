from telegram.ext import ContextTypes

from django.conf import settings

from ..constants import CONTEXT_LANGUAGE_KEY


def get_context_language(context: ContextTypes.DEFAULT_TYPE):
    return context.chat_data.get(CONTEXT_LANGUAGE_KEY, settings.LANGUAGE_CODE)


def set_context_language(context: ContextTypes.DEFAULT_TYPE, language_code: str):
    context.chat_data[CONTEXT_LANGUAGE_KEY] = language_code


def validate_language_code(language_code: str):
    return language_code in settings.LANGUAGES_DICT


def normalize_language_code(language_code: str):
    language_code = language_code.lower()
    return language_code if validate_language_code(language_code) else None
