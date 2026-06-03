from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import BotWebhookView

app_name = "django_telegram"

urlpatterns = [
    path(
        "<bot_id>/webhook/",
        csrf_exempt(BotWebhookView.as_view()),
        name="bot_webhook_view",
    ),
]
