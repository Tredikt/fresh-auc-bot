from get_bot_and_db import get_bot_and_db
from states_handlers.bot_states import AdminStates
from blanks.bot_texts import admin_add_partner, admin_add_admin, admin_text, admin_delete_partner, admin_delete_admin
from blanks.bot_markups import admin_back, admin_markup
from datetime import datetime
from admins_functions.winner_places import winner_places
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .users_statistics import get_users_statistics
from .lots_statistics import get_lots_statistics
from .auction_statistics import get_auction_statistics
from .upload_lots import upload_lots
from config import channel_id, admin_group
import aiogram


async def admin_callback_handler(call, state):
    # print(call.message.reply_markup.inline_keyboard[0][0].text)
    print("this is")
    chat = call.message.chat.id
    m_id = call.message.message_id
    bot, db = get_bot_and_db()
    callback = call.data
    print(callback)
    tg_id = None
    if call.message.chat.type == "private":
        tg_id = call.message.chat.id
    elif call.message.chat.type == "channel":
        tg_id = call["from"]["id"]
    username = call["from"]["username"]
    if username is None:
        if call["from"]["last_name"] is None:
            username = call["from"]["first_name"]
        else:
            username = call["from"]["first_name"] + call["from"]["last_name"]
    print(call)

    blocked_users = db.get_blocked_users()
    users = db.get_users_ids()
    admins = db.get_admins()

    if tg_id in blocked_users:
        await bot.send_message(
            chat_id=tg_id,
            text="К сожалению вы заблокированы"
        )

    elif tg_id in users or tg_id in admins or call.message.chat.id == admin_group:
        if callback[:7] == "confirm":
            await bot.delete_message(
                chat_id=tg_id,
                message_id=m_id
            )

            try:
                await bot.delete_message(
                    chat_id=tg_id,
                    message_id=m_id - 1
                )
            except:
                pass

            link = await bot.export_chat_invite_link(chat_id=channel_id)

            await bot.send_message(
                chat_id=tg_id,
                text="Ваша ставка принята",
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(
                        text="Обратно в канал", url=link
                    )
                )
            )
            code = callback.split("_")[1]
            name, model, code, storage, season, tires, disks, price, photo, status = db.get_lot(code)

            try:
                if int(tires[-2:]) >= 18:
                    auc_price = "+ 500р."
                else:
                    auc_price = "+ 250р."
            except ValueError:
                auc_price = "+ 250р."

            db.update_price(code=code, price=int(auc_price[2:5]))
            photo = db.get_photo_by_code(code)
            lot_id, lot_text, lot_price = db.get_selling_lot(code)
            saved_chats = db.get_saved_lots(code=code)
            saved_chats.insert(0, (lot_id, channel_id))
            db.add_bid(tg_id, username, lot_price, code)

            # await asyncio.sleep(5)
            winners = winner_places(code, text=True)

            print("callback", winners)

            bot_info = await bot.me
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    text=auc_price, url=f"https://t.me/{bot_info.username}?start=raiseprice_{code}"
                )
            ).add(
                InlineKeyboardButton(
                    text="💾", url=f"https://t.me/{bot_info.username}?start=save_{code}"
                ),
                InlineKeyboardButton(
                    text="⏳", callback_data=f"time_{code}"
                ),
                InlineKeyboardButton(
                    text="⚠️", callback_data="warning"
                ),
                InlineKeyboardButton(
                    text="БОТ", url=f"https://t.me/{bot_info.username}"
                )
            )

            for elem in saved_chats:
                lot_id, chat_id = elem
                await bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=lot_id,
                    # photo=photo,
                    caption=lot_text + f"\n{winners}" + f"💰 ТЕКУЩАЯ ЦЕНА: {lot_price}",
                    reply_markup=markup
                )

        elif callback[:9] == "blockuser":
            user_tg = int(callback.split("_")[1])

            phone, fullname = db.user_by_id(tg_id=user_tg)
            await bot.edit_message_text(
                text=f"Пользоватеть ({phone} {fullname}) заблокирован",
                chat_id=channel_id,
                message_id=m_id
            )

        elif callback[:10] == "unlockuser":
            user_tg = int(callback.split("_")[1])

            db.unlock_user_by_tg(user_tg)
            phone, fullname = db.user_by_id(tg_id=user_tg)
            await bot.edit_message_text(
                text=f"Пользоватеть (+{phone} {fullname}) разблокирован",
                chat_id=admin_group,
                message_id=m_id
            )

        elif callback[:10] == "declinedel":
            await bot.delete_message(
                chat_id=tg_id,
                message_id=m_id
            )

        elif callback[:7] == "decline":
            await bot.delete_message(
                chat_id=tg_id,
                message_id=m_id
            )
            await bot.send_message(
                chat_id=tg_id,
                text="Всего доброго."
            )

        elif callback[:10] == "raiseprice":
            code = callback.split("_")[1]
            await bot.send_message(
                chat_id=tg_id,
                text="Вы уверены, что хотите повысить ставку?",
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text="Да", callback_data=f"confirm_{code}")
                ).add(InlineKeyboardButton(
                    text="Нет", callback_data=f"decline_{code}"
                ))
            )

        elif callback == "warning":
            await call.answer(text="Если победитель откажется от лота, он передается следующему участнику", show_alert=True)

        elif callback[:4] == "time":
            code = callback.split("_")[1]
            # minutes, hours = db.get_start_lot_time(code)
            now_minutes = datetime.now().minute
            now_hours = datetime.now().hour

            time = (13 * 60) - (now_hours * 60 + now_minutes)
            await call.answer(text=f"До конца аукциона {time} минут", show_alert=True)

        elif callback[:4] == "save":
            code = callback.split("_")[1]
            name, model, code, storage, season, tires, disks, price, photo, status = db.get_lot(code)

            try:
                if int(tires[-2:]) >= 18:
                    auc_price = "+ 500р."
                else:
                    auc_price = "+ 250р."
            except ValueError:
                auc_price = "+ 250р."

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(
                    text=auc_price, callback_data=f"raiseprice_{code}"
                )
            ).add(
                InlineKeyboardButton(
                    text="⏳", callback_data=f"time_{code}"
                ),
                InlineKeyboardButton(
                    text="⚠️", callback_data="warning"
                )
            )

            if tg_id in admins:
                markup.add(
                    InlineKeyboardButton(text="❌", callback_data=f"deletelot_{code}")
                )

            saved_lot = await bot.copy_message(
                chat_id=tg_id,
                from_chat_id=channel_id,
                message_id=m_id,
                reply_markup=markup
            )
            db.save_lot(lot_id=saved_lot.message_id, chat_id=tg_id, code=code)

        elif callback[:6] == "delete" and callback not in ["delete_partner", "delete_admin"]:
            await bot.delete_message(
                chat_id=tg_id,
                message_id=m_id
            )

            code = callback.split("_")[1]
            db.delete_saved_lots(code)
            await bot.send_message(
                chat_id=admin_group,
                text=f"Админ: {username} снял(а) лот №{code}\n"
            )

            lot = db.get_lot(code)
            if lot is not None:
                name, model, code, storage, season, tires, disks, price, photo, status = lot
            lot_id, lot_text, lot_price = db.get_selling_lot(code)
            saved_chats = db.get_saved_lots(code=code)
            saved_chats.insert(0, (lot_id, channel_id))
            db.add_bid(tg_id, username, lot_price, code)
            winners = winner_places(code, text=True)
            db.delete_bids(code=code)
            db.delete_now_lots(code=code)
            db.update_status_stock(code=code)

            for elem in saved_chats:
                lot_id, chat_id = elem
                await bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=lot_id,
                    caption="Лот снят с аукциона админом" + lot_text + f"\n{winners}" + f"💰 ИТОГОВАЯ ЦЕНА: {lot_price}",
                )

                try:
                    await bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=lot_id,
                        reply_markup=InlineKeyboardMarkup()
                    )
                except aiogram.exceptions.MessageNotModified:
                    continue


        elif callback[:9] == "deletelot":
            code = callback.split("_")[1]

            await bot.send_message(
                chat_id=tg_id,
                text="Вы уверены, что хотите снять лот с аукциона?",
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text="Да", callback_data=f"delete_{code}")
                ).add(InlineKeyboardButton(
                    text="Нет", callback_data=f"declinedel_{code}"
                ))
            )

        elif callback == "admin_back":
            await bot.delete_message(
                chat_id=chat,
                message_id=m_id
            )

            await bot.send_message(
                chat_id=chat,
                text=admin_text,
                reply_markup=admin_markup
            )

        elif callback == "upload_lots":
            await upload_lots(chat=chat)

        elif callback == "add_partner":
            await bot.delete_message(
                chat_id=chat,
                message_id=m_id
            )
            await AdminStates.add_partner.set()
            await bot.send_message(
                chat_id=chat,
                text=admin_add_partner,
                reply_markup=admin_back
            )

        elif callback == "add_admin":
            await bot.delete_message(
                chat_id=chat,
                message_id=m_id
            )

            await bot.send_message(
                chat_id=chat,
                text=admin_add_admin,
                reply_markup=admin_back
            )
            await AdminStates.add_admin.set()

        elif callback == "delete_partner":
            await bot.delete_message(
                chat_id=chat,
                message_id=m_id
            )

            await bot.send_message(
                chat_id=chat,
                text=admin_delete_partner,
                reply_markup=admin_back
            )
            await AdminStates.delete_partner.set()

        elif callback == "delete_admin":
            await bot.delete_message(
                chat_id=chat,
                message_id=m_id
            )

            await bot.send_message(
                chat_id=chat,
                text=admin_delete_admin,
                reply_markup=admin_back
            )
            await AdminStates.delete_admin.set()

        elif callback == "statistics_users":
            await get_users_statistics(tg_id=tg_id)

        elif callback == "statistics_lots":
            await get_lots_statistics(tg_id=tg_id)

        elif callback == "statistics_auction":
            await get_auction_statistics(tg_id=tg_id)

    else:
        await call.answer(text="Чтобы участвовать в аукционе зарегистрируйтесь в @FreshTyresBot")