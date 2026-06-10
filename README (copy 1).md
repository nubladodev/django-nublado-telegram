# django-nublado-telegram

**A reusable Django app for building Telegram bots using `python-telegram-bot`.**

## Overview

After finally figuring out how to get `python-telegram-bot` to work in a Django project, I decided to extract the core setup and features to mitigate further headaches for myself and other developeers who might find themselves in a similar situation.

## What's included

- A bot abstraction that handles setup and lifecycle.
- Telegram models for persisting data in the db.
- A simple bot-registry system for multiple bots in the same project.
- Webhook and polling support.
- Async functionality
- Handler policies for access-control.
- Job utilities such as timed message cleanup in chat.

---

## Requirements

- Python 3.12+
- Django 5+
- python-telegram-bot 22+

---

## Installation

```bash
pip install django-nublado-telegram
```

Add the app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_nublado_telegram",
]
```

Run migrations:

```bash
python manage.py migrate
```

---

## Configuration

Configure the app through Django settings.

```python
DJANGO_NUBLADO_TELEGRAM = {
    "BOT_MODE": "webhook",
}
```

Available modes:

```python
"webhook"
"polling"
```

Example:

```python
DJANGO_NUBLADO_TELEGRAM = {
    "BOT_MODE": "polling",
}
```

---

## Creating a Telegram Application

```python
from django_nublado_telegram.bot import create_app

app = create_app(
    bot_token="YOUR_BOT_TOKEN",
)
```

With defaults:

```python
from telegram.ext import Defaults

app = create_app(
    bot_token="YOUR_BOT_TOKEN",
    defaults=Defaults(parse_mode="HTML"),
)
```

---

## Creating a TelegramBot

```python
from django_nublado_telegram.bot import TelegramBot

bot = TelegramBot(
    name="my-bot",
    application=app,
    webhook_url="https://example.com/webhook/my-bot/",
)
```

---

## Registering Bots

Bots are registered through the global registry.

```python
from django_nublado_telegram.bot_registry import registry

registry.register(
    "my-bot",
    bot,
)
```

Retrieve a bot:

```python
bot = registry.get("my-bot")
```

Retrieve all registered bots:

```python
for bot in registry.all():
    print(bot.name)
```

---

## Webhook Integration

Expose the webhook view in your URL configuration.

```python
from django.urls import path

from django_nublado_telegram.views import BotWebhookView

urlpatterns = [
    path(
        "webhook/<str:bot_id>/",
        BotWebhookView.as_view(),
        name="telegram-webhook",
    ),
]
```

The view:

1. Locates the bot in the registry
2. Parses the Telegram update
3. Processes the update through the bot application

---

## Polling Mode

Run registered bots in polling mode:

```bash
python manage.py runbot
```

Run a specific bot:

```bash
python manage.py runbot --name my-bot
```

---

## Handler Policies

Policies provide reusable access-control rules for handlers.

### GroupOnly

```python
from django_nublado_telegram.policies import GroupOnly, with_policies

@with_policies(GroupOnly)
async def handler(update, context):
    ...
```

### PrivateOnly

```python
@with_policies(PrivateOnly)
async def handler(update, context):
    ...
```

### AdminOnly

```python
@with_policies(AdminOnly)
async def handler(update, context):
    ...
```

### GroupOwnerOnly

```python
@with_policies(GroupOwnerOnly)
async def handler(update, context):
    ...
```

Multiple policies may be combined:

```python
@with_policies(GroupOnly, AdminOnly)
async def handler(update, context):
    ...
```

---

## Jobs

Utility functions are provided for common Telegram tasks.

### Schedule Message Cleanup

Delete command messages and bot responses after a delay.

```python
from django_nublado_telegram.jobs import schedule_message_cleanup

schedule_message_cleanup(
    update,
    context,
    time_seconds=20,
    bot_message_ids=[reply.message_id],
)
```

---

## Testing

Install test dependencies:

```bash
pip install -e .[test]
```

Run tests:

```bash
pytest
```

Generate coverage reports:

```bash
pytest --cov
```

---

## Related Projects

- django-nublado-core
- django-nublado-translation

---

## License

BSD 3-Clause License.