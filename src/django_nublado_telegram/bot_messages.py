from django.utils.translation import gettext_lazy as _

BOT_MESSAGES = {
    "error.group_only": _("django_telegram.bot.error.group_only"),
    "error.private_only": _("django_telegram.bot.error.private_only"),
    "error.admin_access": _("django_telegram.bot.error.admin_access"),
    "error.group_owner_access": _("django_telegram.bot.error.group_owner_access"),
    "error.bot_owner_access": _("django_telegram.bot.error.bot_owner_access"),
}
