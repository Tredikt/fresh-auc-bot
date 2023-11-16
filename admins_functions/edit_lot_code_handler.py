from get_bot_and_db import get_bot_and_db
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.dispatcher import FSMContext
from states_handlers.bot_states import AdminStates


async def edit_lot_code_handler(message: Message, state: FSMContext):
    bot, db = get_bot_and_db()
    all_codes = db.get_all_codes()
    chat = message.chat.id
    code = message.text

    if code in all_codes:
        async with state.proxy() as data:
            data["code"] = code

        await AdminStates.edit_lot_price.set()
        await bot.send_message(
            chat_id=chat,
            text=f"Теперь введите новую цену для лота, либо вернитесь назад",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="К админке", callback_data="admin_back")
            )
        )

    else:
        await bot.send_message(
            chat_id=chat,
            text=f"Такого кода нет в базе, попробуйте снова, либо вернитесь в админку",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="К админке", callback_data="admin_back")
            )
        )
