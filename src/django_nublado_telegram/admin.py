from import_export.admin import ImportExportModelAdmin

from django.contrib import admin

from .models import (
    TelegramUser,
    TelegramChat,
    TelegramGroupMember,
    TelegramGroupSettings,
)


@admin.register(TelegramChat)
class TelegramChatAdmin(ImportExportModelAdmin):

    list_display = (
        "id",
        "title",
        "username",
        "chat_type",
        "created_at",
    )

    search_fields = (
        "id",
        "title",
        "username",
    )

    readonly_fields = (
        "id",
        "chat_type",
        "created_at",
        "title",
        "username",
    )

    ordering = ("-created_at",)


@admin.register(TelegramUser)
class TelegramUserAdmin(ImportExportModelAdmin):
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "is_bot",
        "created_at",
        "updated_at",
    ]

    search_fields = (
        "id",
        "username",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "id",
        "is_bot",
        "created_at",
        "updated_at",
    )

    list_filter = ("is_bot",)


@admin.register(TelegramGroupSettings)
class TelegramGroupSettingsAdmin(ImportExportModelAdmin):
    list_display = (
        "chat",
        "language",
    )

    list_editable = ("language",)

    search_fields = (
        "chat__id",
        "chat__title",
    )


@admin.register(TelegramGroupMember)
class TelegramGroupMemberAdmin(ImportExportModelAdmin):
    list_display = (
        "chat",
        "user",
        "points",
        "created_at",
    )

    list_filter = ("chat",)

    search_fields = (
        "chat__title",
        "user__username",
        "user__id",
    )

    ordering = ("-points",)
