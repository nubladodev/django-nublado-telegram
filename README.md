
# django-nublado-telegram

An app for Telegram bots in Django using the python-telegram-bot library.

---

## Features


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
