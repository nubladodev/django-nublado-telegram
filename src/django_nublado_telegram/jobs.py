from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest


async def delete_message_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data.get("chat_id")
    message_ids = job.data.get("message_ids", [])

    if not chat_id:
        return

    for message_id in message_ids:
        try:
            await context.bot.delete_message(chat_id, message_id)
        except BadRequest:
            pass


def schedule_message_cleanup(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    time_seconds: int = 20,
    bot_message_ids: list[int] | None = None,
):
    tg_chat_id = update.effective_chat.id
    tg_command_id = update.effective_message.message_id

    message_ids = [tg_command_id]

    if bot_message_ids:
        message_ids.extend(bot_message_ids)

    context.job_queue.run_once(
        delete_message_job,
        time_seconds,
        data={
            "chat_id": tg_chat_id,
            "message_ids": message_ids,
        },
    )