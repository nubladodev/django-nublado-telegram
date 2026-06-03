from html import escape
from telegram import User


def user_display_name(
    tg_user: User, prefer_username: bool = True, clickable: bool = True
) -> str:
    """
    Return user's @username or first and last names, if available.
    Format the display name as a link if clickable == True.
    """
    # Display username with @ if preferred and user has a username.
    if prefer_username and tg_user.username:
        display_name = f"@{tg_user.username}"
    else:
        # Display the user's first and last names, if available, or fall back to
        # the user's first name.
        if tg_user.last_name:
            display_name = f"{tg_user.first_name} {tg_user.last_name}"
        else:
            display_name = tg_user.first_name

    display_name = escape(display_name)

    if clickable:
        return f'<a href="tg://user?id={tg_user.id}">{display_name}</a>'

    return display_name
