from get_bot_and_db import get_bot_and_db
from blanks.bot_examinations import examination_symbols
from blanks.bot_texts import accept_fi, decline_fi
from blanks.bot_markups import gender_markup
from states_handlers.bot_states import RegistrationStates


async def get_fullname_handler(message, state):
    chat = message.chat.id
    text = message.text
    bot, db = get_bot_and_db()

    for symbol in text:
        if symbol.lower() not in examination_symbols:
            await bot.send_message(
                chat_id=chat,
                text=decline_fi
            )
            break
    else:
        async with state.proxy() as data:
            data["fullname"] = text

        await bot.send_message(
            chat_id=chat,
            text=accept_fi,
            reply_markup=gender_markup
        )

        await RegistrationStates.next()