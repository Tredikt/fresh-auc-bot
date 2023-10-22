from get_bot_and_db import get_bot_and_db
from blanks.bot_texts import admin_partner_also_is, admin_partner_accept, admin_text, admin_partner_wrong_format
from blanks.bot_markups import admin_markup


async def add_partner_handler(message, state):
    print("partner")
    bot, db = get_bot_and_db()
    phones = db.get_phones()
    chat = message.chat.id
    text = message.text

    print(text, message.contact)
    if message.contact:
        phone = str(message.contact.phone_number)
        if phone[0] == "8":
            phone =phone.replace("8", "7", 1)

        elif phone[0] == "+":
            phone = phone.replace("+7", "7", 1)

        if phone in phones:
            await bot.send_message(
                chat_id=chat,
                text=admin_partner_also_is
            )

        else:
            db.add_partner(
                phone=phone
            )

            await bot.send_message(
                chat_id=chat,
                text=admin_partner_accept
            )

            await state.finish()

            await bot.send_message(
                chat_id=chat,
                text=admin_text,
                reply_markup=admin_markup
            )

    elif text is None or len(text) != 11:
        await bot.send_message(
            chat_id=chat,
            text=admin_partner_wrong_format
        )

    else:
        if text is not None and text[0] == "+":
            text = text.replace("+7", "7", 1)

        phone = text
        print(phone)
        if phone[0] == "8":
            phone = phone.replace("8", "7", 1)

        db.add_partner(
            phone=phone
        )

        await bot.send_message(
            chat_id=chat,
            text=admin_partner_accept
        )

        await state.finish()

        await bot.send_message(
            chat_id=chat,
            text=admin_text,
            reply_markup=admin_markup
        )
