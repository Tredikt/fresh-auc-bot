from get_bot_and_db import get_bot_and_db
from blanks.bot_texts import accept_gender, decline_gender
from blanks.bot_markups import remove_markup
from states_handlers.bot_states import RegistrationStates

async def get_gender_handler(message, state):
    chat = message.chat.id
    text = message.text
    bot, db = get_bot_and_db()

    if text.lower() in ["мужчина", "женщина", "пропустить"]:
        async with state.proxy() as data:
            data["gender"] = text.lower().title()

        await RegistrationStates.next()

        await bot.send_message(
            chat_id=chat,
            text=accept_gender,
            reply_markup=remove_markup
        )

    else:
        await bot.send_message(
            chat_id=chat,
            text=decline_gender,
        )