from email_validate import validate
from get_bot_and_db import get_bot_and_db
from blanks.bot_texts import accept_email, decline_email
from states_handlers.bot_states import RegistrationStates


async def get_email_handler(message, state):
    bot, db = get_bot_and_db()
    email_address = message.text
    chat = message.chat.id

    if "@" in email_address:
        async with state.proxy() as data:
            data["email"] = email_address

        await bot.send_message(
            chat_id=chat,
            text=accept_email
        )
        await RegistrationStates.next()

    elif "@" not in email_address:
        await bot.send_message(
            chat_id=chat,
            text=decline_email
        )
