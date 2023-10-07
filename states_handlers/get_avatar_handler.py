from get_bot_and_db import get_bot_and_db
from blanks.bot_texts import accept_avatar, decline_avatar, decline_text_avatar
from blanks.bot_markups import markups_regions_list
from states_handlers.bot_states import RegistrationStates


async def get_avatar_handler(message, state):
    chat = message.chat.id
    bot, db = get_bot_and_db()
    print(message)

    if message.document:
        await bot.send_message(
            chat_id=chat,
            text=decline_avatar
        )

    elif message.photo:
        await message.photo[-1].download(f"avatars/{chat}_avatar")
        async with state.proxy() as data:
            data["avatar_name"] = f"avatars/{chat}_avatar"

        await bot.send_message(
            chat_id=chat,
            text=accept_avatar,
            reply_markup=markups_regions_list[0]
        )

        await RegistrationStates.next()

    else:
        await bot.send_message(
            chat_id=chat,
            text=decline_text_avatar
        )

