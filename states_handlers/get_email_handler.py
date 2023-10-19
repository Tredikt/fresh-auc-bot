from email_validate import validate
from get_bot_and_db import get_bot_and_db
from blanks.bot_texts import accept_email, decline_email
from states_handlers.bot_states import RegistrationStates


async def get_email_handler(message, state):
    bot, db = get_bot_and_db()
    email_address = message.text
    chat = message.chat.id

    validation = validate(
        email_address=email_address,
        check_format=True,
        check_blacklist=True,
        check_dns=True,
        dns_timeout=10,
        check_smtp=False,
        smtp_debug=False)

    if validation:
        async with state.proxy() as data:
            data["email"] = email_address

        await bot.send_message(
            chat_id=chat,
            text=accept_email
        )
        await RegistrationStates.next()

    elif not validation:
        await bot.send_message(
            chat_id=chat,
            text=decline_email
        )
