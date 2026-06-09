import asyncio

import pytest
from telegram.error import BadRequest

from django_nublado_telegram.jobs import (
    schedule_message_cleanup,
    delete_message_job,
)


def test_schedule_message_cleanup_schedules_job(mocker):
    chat_id = 123
    cmd_message_id = 999
    bot_message_ids = [111, 222]
    job_queue = mocker.Mock()
    context = mocker.Mock()
    context.job_queue = job_queue

    update = mocker.Mock()
    update.effective_chat.id = chat_id
    update.effective_message.message_id = cmd_message_id

    schedule_message_cleanup(
        update,
        context,
        time_seconds=10,
        bot_message_ids=bot_message_ids,
    )

    job_queue.run_once.assert_called_once()

    args, kwargs = job_queue.run_once.call_args
    # Include command message with message ids.
    bot_message_ids.append(cmd_message_id)

    assert kwargs["data"]["chat_id"] == chat_id
    assert set(kwargs["data"]["message_ids"]) == set(bot_message_ids)


@pytest.mark.asyncio
async def test_delete_message_job_ignores_bad_request(mocker):
    bot = mocker.Mock()
    bot.delete_message = mocker.AsyncMock(side_effect=BadRequest("fail"))

    job = mocker.Mock()
    job.data = {
        "chat_id": 123,
        "message_ids": [1, 2, 3],
    }

    context = mocker.Mock()
    context.job = job
    context.bot = bot

    # should not raise
    await delete_message_job(context)

    assert bot.delete_message.await_count == 3


def test_delete_message_job_missing_chat_id(mocker):
    context = mocker.Mock()
    context.job = mocker.Mock()
    context.job.data = {"message_ids": [1, 2, 3]}

    # should not crash
    asyncio.run(delete_message_job(context))