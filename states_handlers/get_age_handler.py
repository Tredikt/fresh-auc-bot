from get_bot_and_db import get_bot_and_db
from blanks.bot_texts import accept_age, decline_age
from states_handlers.bot_states import RegistrationStates

async def get_age_handler(message, state):
    chat = message.chat.id
    text = message.text
    bot, db = get_bot_and_db()

    if len(text) == 2:
        try:
            age = int(text)
            async with state.proxy() as data:
                data["age"] = age

            await bot.send_message(
                chat_id=chat,
                text=accept_age
            )

            await RegistrationStates.next()
            
        except ValueError:
            await bot.send_message(
                chat_id=chat,
                text=decline_age
            )
    else:
        await bot.send_message(
            chat_id=chat,
            text=decline_age
        )