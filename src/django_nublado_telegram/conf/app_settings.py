from dataclasses import dataclass
from enum import StrEnum


from django_nublado_core.conf.base import AppSettings


class BotMode(StrEnum):
    POLLING = "polling"
    WEBHOOK = "webhook"


# The app's settings dict name
SETTINGS_DICT_NAME = "DJANGO_NUBLADO_TELEGRAM"

# The app settings default values.
SETTINGS_DEFAULTS = {
    "BOT_MODE": BotMode.POLLING,
}


@dataclass(frozen=True)
class AppData:
    BOT_MODE: BotMode

    def __post_init__(self):
        try:
            object.__setattr__(
                self,
                "BOT_MODE",
                BotMode(self.BOT_MODE),
            )
        except ValueError as e:
            raise ImproperlyConfigured(
                f"Invalid BOT_MODE: {self.BOT_MODE}"
            ) from e


app_settings = AppSettings(
    defaults=SETTINGS_DEFAULTS,
    settings_dict_name=SETTINGS_DICT_NAME,
    cls=AppData,
)
