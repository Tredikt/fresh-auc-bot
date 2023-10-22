from get_bot_and_db import get_bot_and_db
from blanks.bot_examinations import examination_symbols
from blanks.bot_texts import accept_company, decline_company

from states_handlers.bot_states import RegistrationStates
from config import channel_id

async def get_company_handler(message, state):
    chat = message.chat.id
    bot, db = get_bot_and_db()
    text = message.text

    if text.lower() == "я не работаю в компании":
        async with state.proxy() as data:
            phone = data["phone"]
            email = data["email"]
            fullname = data["fullname"]
            age = data["age"]
            gender = data["gender"]
            avatar_name = data["avatar_name"]
            region = data["region"]
            company = "-"

            db.add_user(
                phone=phone,
                email=email,
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

        link = await bot.export_chat_invite_link(
            chat_id=channel_id,
        )

        await bot.send_message(
            chat_id=chat,
            text="Вы добавлены в закрытый канал FRESH — Шинный аукцион!\n"
                 "Переходите по ссылке, регистрируйтесь и делайте свои ставки. Приятных торгов!\n" + str(link)
        )

        await state.finish()
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
                email = data["email"]
                fullname = data["fullname"]
                age = data["age"]
                gender = data["gender"]
                avatar_name = data["avatar_name"]
                region = data["region"]
                company = text.lower().title()

                db.add_user(
                    phone=phone,
                    email=email,
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

            link = await bot.export_chat_invite_link(
                chat_id=channel_id,
            )

            await bot.send_message(
                chat_id=chat,
                text="Вы добавлены в закрытый канал FRESH — Шинный аукцион!\n"
                     "Переходите по ссылке, регистрируйтесь и делайте свои ставки. Приятных торгов!\n" + str(link)
            )

            await state.finish()

