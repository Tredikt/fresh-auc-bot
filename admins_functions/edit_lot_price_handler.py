from get_bot_and_db import get_bot_and_db
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.dispatcher import FSMContext
from edit_lot_and_lot_price import edit_lot_and_lot_price


async def edit_lot_price_handler(message: Message, state: FSMContext):
    bot, db = get_bot_and_db()
    chat = message.chat.id
    new_price = message.text

    try:
        async with state.proxy() as data:
            code = data["code"]
            mode = data.get("mode")

        new_price = int(new_price)
        if mode == "preview":
            await edit_lot_and_lot_price(code, new_price)
        db.edit_lot_price(code=code, new_price=new_price)

        await bot.send_message(
            chat_id=chat,
            text=f"Для лота №{code} успешно установлена цена {new_price}",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="К админке", callback_data="admin_back")
            )
        )
        await state.finish()

    except ValueError:
        await bot.send_message(
            chat_id=chat,
            text="Сообщением должно быть целое число, попробуйте снова, либо вернитесь в админку",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="К админке", callback_data="admin_back")
            )
        )
