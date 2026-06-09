import pytest

from django_nublado_telegram.bot_registry import BotRegistry


class TestBotRegistry:

    def test_register_and_get(self):
        registry = BotRegistry()

        bot = object()

        registry.register("banana", bot)

        assert registry.get("banana") is bot

    def test_get_missing_bot_raises(self):
        registry = BotRegistry()

        with pytest.raises(ValueError):
            registry.get("foo")

    def test_register_overwrites_existing_bot(self):
        registry = BotRegistry()

        bot1 = object()
        bot2 = object()

        registry.register("foo", bot1)
        registry.register("foo", bot2)

        assert registry.get("foo") is bot2

    def test_all_returns_registered_bots(self):
        registry = BotRegistry()

        bot1 = object()
        bot2 = object()

        registry.register("one", bot1)
        registry.register("two", bot2)

        assert set(registry.all()) == {bot1, bot2}