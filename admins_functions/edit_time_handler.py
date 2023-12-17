from get_bot_and_db import get_bot_and_db
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.dispatcher import FSMContext


async def edit_time_handler(message: Message, state: FSMContext):
    bot, db = get_bot_and_db()
    chat = message.chat.id
    text = message.text

    try:
        await bot.edit_message_reply_markup(
            chat_id=chat,
            message_id=message.message_id - 1,
            reply_markup=InlineKeyboardMarkup()
        )
    except Exception:
        pass

    if len(text) == 5 and ":" in text:
        async with state.proxy() as data:
            index = data["index"]

        db.update_time_auction(time=text, index=index)

        await bot.send_message(
            chat_id=chat,
            text=f"Время успешно установлено",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="К админке", callback_data="admin_back")
            )
        )
        await state.finish()

    else:
        await bot.send_message(
            chat_id=chat,
            text="Сообщение должно быть вида 10:24",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="К админке", callback_data="admin_back")
            )
        )