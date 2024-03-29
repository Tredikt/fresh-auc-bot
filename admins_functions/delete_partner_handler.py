from get_bot_and_db import get_bot_and_db
from blanks.bot_texts import admin_partner_delete, admin_text, admin_partner_wrong_format, admin_partner_isnot
from blanks.bot_markups import admin_markup


async def delete_partner_handler(message, state):
    bot, db = get_bot_and_db()
    phones = db.get_phones()
    chat = message.chat.id
    text = message.text

    if message.contact:
        phone = str(message.contact.phone_number)
        if phone[0] == "8":
            phone.replace("8", "7", 1)

        if phone not in phones:
            await bot.send_message(
                chat_id=chat,
                text=admin_partner_isnot
            )

        else:
            db.delete_partner(
                phone=phone
            )

            await bot.send_message(
                chat_id=chat,
                text=admin_partner_delete
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
            text.replace("+7", "7", 1)

        phone = text
        if phone[0] == "8":
            phone.replace("8", "7", 1)

        db.delete_partner(
            phone=phone
        )

        await bot.send_message(
            chat_id=chat,
            text=admin_partner_delete
        )

        await state.finish()

        await bot.send_message(
            chat_id=chat,
            text=admin_text,
            reply_markup=admin_markup
        )
