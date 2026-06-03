import pytest
from types import SimpleNamespace

from django_telegram.utils.formatting import user_display_name


@pytest.mark.parametrize(
    "user_data, prefer_username, clickable, expected",
    [
        # prefers username, has username
        (
            {"id": 1, "username": "alice", "first_name": "Alice", "last_name": "Smith"},
            True,
            True,
            '<a href="tg://user?id=1">@alice</a>',
        ),
        # prefers username, no username → uses first+last
        (
            {"id": 2, "username": None, "first_name": "Bob", "last_name": "Jones"},
            True,
            True,
            '<a href="tg://user?id=2">Bob Jones</a>',
        ),
        # prefers username, no username → no last name
        (
            {"id": 3, "username": None, "first_name": "Charlie", "last_name": None},
            True,
            True,
            '<a href="tg://user?id=3">Charlie</a>',
        ),
        # prefers first/last name even if username exists
        (
            {"id": 4, "username": "dave", "first_name": "Dave", "last_name": "Lee"},
            False,
            True,
            '<a href="tg://user?id=4">Dave Lee</a>',
        ),
        # not clickable → returns plain text
        (
            {"id": 5, "username": "eve", "first_name": "Eve", "last_name": "Adams"},
            True,
            False,
            "@eve",
        ),
        # escape HTML in names
        (
            {"id": 6, "username": None, "first_name": "<Foo>", "last_name": "&Bar"},
            True,
            True,
            '<a href="tg://user?id=6">&lt;Foo&gt; &amp;Bar</a>',
        ),
    ],
)
def test_user_display_name(user_data, prefer_username, clickable, expected):
    # Use SimpleNamespace instead of real User
    tg_user = SimpleNamespace(**user_data)
    result = user_display_name(
        tg_user, prefer_username=prefer_username, clickable=clickable
    )
    assert result == expected
