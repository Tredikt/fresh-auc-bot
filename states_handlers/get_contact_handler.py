from get_bot_and_db import get_bot_and_db
from blanks.bot_texts import accept_text, decline_text, accept_admin
from blanks.bot_markups import remove_markup
from states_handlers.bot_states import RegistrationStates


async def get_contact_handler(message, state):
    print(1)
    chat = message.chat.id
    contact = message.contact.phone_number
    bot, db = get_bot_and_db()

    contact = str(contact)
    if contact[0] == "8":
        contact.replace("8", "7", 1)


    phones = db.get_phones()
    admin_phones = db.get_admin_phones()
    # print(phones, contact, contact in phones)

    if contact in admin_phones:
        await bot.send_message(
            chat_id=chat,
            text=accept_admin
        )

        db.add_admin_id(
            tg_id=message.from_user.id,
            phone=contact
        )

        await state.finish()
        pass

    elif contact in phones:
        async with state.proxy() as data:
            data["phone"] = contact

        await bot.send_message(
            chat_id=chat,
            text=accept_text,
            reply_markup=remove_markup,
        )

        await RegistrationStates.next()

    else:
        await bot.send_message(
            chat_id=chat,
            text=decline_text,
            reply_markup=remove_markup,
            parse_mode="html",
            disable_web_page_preview=True
        )