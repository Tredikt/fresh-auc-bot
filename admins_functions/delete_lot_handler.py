from get_bot_and_db import get_bot_and_db

from aiogram.types import Message
from aiogram.dispatcher.dispatcher import FSMContext


async def delete_lot_handler(message: Message, state: FSMContext):
    bot, db = get_bot_and_db()
    chat = message.chat.id
    text = message.text
    codes = db.get_all_codes()

    if text in codes:
        db.delete_info_about_lot(text)
        await bot.send_message(
            chat_id=chat,
            text=f"Лот №{text} был успешно удалён"
        )
        await bot.delete_message(
            chat_id=chat,
            message_id=message.message_id
        )

    else:
        await bot.send_message(
            chat_id=chat,
            text="Данного лота нет в базе"
        )
