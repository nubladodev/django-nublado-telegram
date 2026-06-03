from telegram import Update, Message
from telegram.error import BadRequest, Forbidden


async def safe_delete_message(message: Message):
    try:
        await message.delete()
    except (BadRequest, Forbidden):
        pass


async def delete_command(update: Update):
    """
    Delete the command message (e.g, /some_command in the chat).
    This is typically called at the  end of a handler once it has done its work
    and the lingering command isn't desired in the chat.
    """

    await safe_delete_message(update.effective_message)





