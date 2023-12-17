from get_bot_and_db import get_bot_and_db
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.dispatcher import FSMContext
from states_handlers.bot_states import AdminStates


async def edit_lot_code_handler(message: Message, state: FSMContext):
    bot, db = get_bot_and_db()
    all_codes = db.get_all_codes()
    chat = message.chat.id
    code = message.text
    far = True

    try:
        await bot.edit_message_reply_markup(
            chat_id=chat,
            message_id=message.message_id - 1,
            reply_markup=InlineKeyboardMarkup()
        )
    except Exception:
        pass

    if code in all_codes:
        async with state.proxy() as data:
            data["code"] = code
            mode = data.get("mode")

        if mode == "preview":
            lot_codes = db.get_lots_codes()
            if code not in lot_codes:
                await bot.send_message(
                    chat_id=chat,
                    text=f"Лот с таким кодом не разыгрывается, попробуйте снова, либо вернитесь в админку",
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(text="К админке", callback_data="admin_back")
                    )
                )
                far = False

        if far:
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
