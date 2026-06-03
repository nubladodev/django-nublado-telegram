import pytest

from django.conf import settings

from django_telegram.services.language import (
    resolve_chat_language,
    set_chat_language,
)
from django_telegram.utils.language import (
    get_context_language,
    set_context_language,
    validate_language_code,
    normalize_language_code,
)
from django_telegram.constants import CONTEXT_LANGUAGE_KEY

pytestmark = pytest.mark.asyncio


class TestLanguageUtils:
    def test_get_context_language(self, context):
        lang = "es"
        assert CONTEXT_LANGUAGE_KEY not in context.chat_data
        language_code = get_context_language(context)
        assert language_code == settings.LANGUAGE_CODE

        assert settings.LANGUAGE_CODE != lang
        context.chat_data[CONTEXT_LANGUAGE_KEY] = lang
        language_code = get_context_language(context)
        assert language_code == lang

    def test_set_context_language(self, context):
        lang = "es"
        assert CONTEXT_LANGUAGE_KEY not in context.chat_data
        set_context_language(context, lang)
        assert context.chat_data[CONTEXT_LANGUAGE_KEY] == lang

    def test_validate_language_code(self):
        assert validate_language_code("xx") is False
        assert validate_language_code(settings.LANGUAGE_CODE) is True

    def test_normalize_language_code(self):
        assert normalize_language_code("EN") == "en"
        assert normalize_language_code("en") == "en"
        assert normalize_language_code("eN") == "en"
        assert normalize_language_code("XX") is None


class TestLanguageServices:
    @pytest.mark.django_db
    async def test_resolve_chat_language_sets_context(self, update, context):
        language_code = await resolve_chat_language(update, context)

        assert CONTEXT_LANGUAGE_KEY in context.chat_data
        assert language_code == context.chat_data[CONTEXT_LANGUAGE_KEY]
        assert language_code == settings.LANGUAGE_CODE

    @pytest.mark.django_db
    async def test_resolver_uses_cached_context(self, update, context):
        context.chat_data[CONTEXT_LANGUAGE_KEY] = "es"

        language_code = await resolve_chat_language(update, context)

        assert language_code == "es"

    @pytest.mark.django_db
    async def test_language_persists_across_calls(self, update, context):
        # simulate setting language
        await set_chat_language(update, context, "es")

        # simulate a new handler call using resolver
        language_code = await resolve_chat_language(update, context)

        assert language_code == "es"
