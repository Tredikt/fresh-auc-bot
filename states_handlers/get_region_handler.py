from get_bot_and_db import get_bot_and_db
from blanks.bot_markups import markups_regions_list, company_markup
from blanks.bot_texts import accept_region
from states_handlers.bot_states import RegistrationStates


async def get_region_handler(call, state):
    chat = call.message.chat.id
    bot, db = get_bot_and_db()
    callback = call.data

    print(111)
    if callback[:9] == "next_page":
        await bot.edit_message_reply_markup(
            chat_id=chat,
            message_id=call.message.message_id,
            reply_markup=markups_regions_list[int(callback[9:])]
        )

    elif callback[:9] == "prev_page":
        await bot.edit_message_reply_markup(
            chat_id=chat,
            message_id=call.message.message_id,
            reply_markup=markups_regions_list[int(callback[9:])]
        )

    elif callback.isdigit():
        inline_list = call.message.reply_markup.inline_keyboard

        for elem in inline_list:
            if elem[0].callback_data == callback:
                async with state.proxy() as data:
                    data["region"] = elem[0].text

                await bot.delete_message(
                    chat_id=chat,
                    message_id=call.message.message_id
                )

                await bot.send_message(
                    chat_id=chat,
                    text=accept_region,
                    reply_markup=company_markup
                )

                await RegistrationStates.next()