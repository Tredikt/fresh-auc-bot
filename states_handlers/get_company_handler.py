from get_bot_and_db import get_bot_and_db
from blanks.bot_examinations import examination_symbols
from blanks.bot_texts import accept_company, decline_company

from states_handlers.bot_states import RegistrationStates


async def get_company_handler(message, state):
    chat = message.chat.id
    bot, db = get_bot_and_db()
    text = message.text

    if text == "Я не работаю в компании":
        async with state.proxy() as data:
            data["company"] = "-"

    else:
        for symbol in text:
            if symbol.lower() not in examination_symbols:
                await bot.send_message(
                    chat_id=chat,
                    text=decline_company
                )
                break
        else:
            async with state.proxy() as data:
                phone = data["phone"]
                fullname = data["fullname"]
                age = data["age"]
                gender = data["gender"]
                avatar_name = data["avatar_name"]
                region = data["region"]
                company = text.lower().title()

                db.add_user(
                    phone=phone,
                    tg_id=message.from_user.id,
                    gender=gender,
                    age=age,
                    fullname=fullname,
                    avatar_name=avatar_name,
                    region=region,
                    company=company
                )

            await bot.send_message(
                chat_id=chat,
                text=accept_company,
            )


            await state.finish()

