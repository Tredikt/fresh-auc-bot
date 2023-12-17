from get_bot_and_db import get_bot_and_db
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.dispatcher import FSMContext
from states_handlers.bot_states import AdminStates


async def add_lots_for_auc_handler(message: Message, state: FSMContext):
    bot, db = get_bot_and_db()
    chat = message.chat.id
    text = message.text

    draw_code = text.split(",")
    try:
        for code in draw_code:
            code = code.strip()
            db.update_status_draw(code)
    except:
        pass

    await bot.send_message(
        chat_id=chat,
        text=f"Коды: {text} успешно добавлены на завтрашний розыгрыш"
    )

    await state.finish()