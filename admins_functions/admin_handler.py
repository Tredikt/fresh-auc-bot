from get_bot_and_db import get_bot_and_db
from blanks.bot_markups import admin_markup
from blanks.bot_texts import admin_text


async def admin_handler(message, state):
    bot, db = get_bot_and_db()
    admins = db.get_admins()
    tg_id = message.from_user.id

    if tg_id in admins:
        await state.finish()

        await bot.send_message(
            chat_id=tg_id,
            text=admin_text,
            reply_markup=admin_markup
        )