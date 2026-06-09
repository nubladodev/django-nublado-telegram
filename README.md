
# django-nublado-telegram

A Django app for building Telegram bots using [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot).

---

## Features
- Bot registry system
- Webhook Django view
- Bot lifecycle management
- Handler policy system
- Async-safe
- Job utilities (scheduled message cleanup)

---

## Installation

```bash
pip install django-nublado-telegram
```

```python
INSTALLED_APPS = [
    ...,
    "django_nublado_telegram",
]
```
---

## Requirements
- Python 3.12
- python-telegram-bot
- django-nublado-core

## Models

### TelegramUser

A model for Telegram.

---

## App settings

```python
from django_nublado_translation.conf.app_settings import app_settings

app_settings.BOT_MODE
```

### Available settings

| Setting | Default |
|-------|---------|
| `BOT_MODE` | `"polling"` |

### Override

```python
DJANGO_NUBLADO_TELEGRAM = {
    "BOT_MODE": "webhook",
}
```

---

## Testing

```bash
pytest
```

Requires `pytest-django`.
