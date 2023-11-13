import aioschedule
from states_handlers.bot_states import AuctionStates
from get_bot_and_db import get_bot_and_db
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
import asyncio
from admins_functions.winner_places import winner_places
from blanks.bot_markups import winner_markup
from auction import auc_bot
import aiogram
from datetime import datetime
from config import channel_id, admin_group


async def start_auction():
    weekday = datetime.now().weekday() + 1
    if weekday in [1, 2, 3, 4, 5, 6]:
        bot, db = get_bot_and_db()
        five_lots = db.get_five_lots()
        relots_codes = db.get_re_lot()

        lots_for_auc = []
        for num, code in enumerate(relots_codes):
            if num == 5:
                break
            lots_for_auc.append(
                db.get_lot(code)
            )

        if len(lots_for_auc) < 5:
            for num, elem in enumerate(five_lots):
                if 5 - len(lots_for_auc) == 0:
                    break
                if elem not in lots_for_auc:
                    lots_for_auc.append(elem)

        for elem in lots_for_auc:
            name, model, code, storage, season, tires, disks, price, photo, status = elem
            #
            # if int(tires[-2:]) >= 18:
            #     auc_price = "+ 500р."
            # else:
            #     auc_price = "+ 250р."

            # markup = InlineKeyboardMarkup()
            # markup.add(
            #     InlineKeyboardButton(
            #         text=auc_price, callback_data=f"raiseprice_{code}"
            #     )
            # ).add(
            #     InlineKeyboardButton(
            #         text="💾", callback_data=f"save_{code}"
            #     ),
            #     InlineKeyboardButton(
            #         text="⏳", callback_data=f"time_{code}"
            #     ),
            #     InlineKeyboardButton(
            #         text="⚠️", callback_data="warning"
            #     )
            # )

            if disks is not None and disks.lower() not in ["хорошее", "плохое", "среднее", "отличное", "мало шипов. плохое"]:
                text = f"🔥 СТАРТ {price} ₽🔥\n\n" \
                       f"✅ {model}\n" \
                       f"✅ Шины {disks}\n" \
                       f"✅ {tires}\n" \
                       f"✅ {season}\n" \
                       f"🌍 Место склада {storage}\n\n" \
                        f"❗️ Продолжительность аукциона - 1 час ❗️ \n\n" \
                        f"Администратор аукциона: @akulovrus\n\n" \
                        f"📌 Лот № {code}\n"
            else:
                text = f"🔥 СТАРТ {price} ₽🔥\n\n" \
                       f"✅ {model}\n" \
                       f"✅ {tires}\n" \
                       f"✅ {season}\n" \
                       f"🌍 Место склада {storage}\n\n" \
                       f"❗️ Продолжительность аукциона - 1 час ❗️\n\n" \
                       f"Администратор аукциона: @akulovrus\n\n" \
                       f"📌 Лот № {code}\n"
            db.update_status_auction(code)

            lot_message = f"Данный лот будет разыгран завтра в 12:00!!!\n"
            if datetime.now().weekday() == 5:
                lot_message = "Добрый день! Данный лот будет разыгран в понедельник в 12:00\n"

            auc_message = await bot.send_photo(
                chat_id=channel_id,
                photo=photo,
                caption=lot_message + text + f"💰 ТЕКУЩАЯ ЦЕНА: {price}",
                # reply_markup=markup
            )

            db.add_auc_lot(lot_id=auc_message.message_id, lot_text=text, lot_price=price, code=code)
            await asyncio.sleep(3 * 60)


async def edit_lots():
    weekday = datetime.now().weekday() + 1
    # if True:
    if weekday in [1, 2, 3, 4, 5, 6, 7]:
        bot, db = get_bot_and_db()

        try:
            reminder_begin_msg = db.get_reminder_id(stage="begin")
            await bot.delete_message(
                chat_id=channel_id,
                message_id=reminder_begin_msg
            )
            db.delete_reminder_id(stage="begin")
        except Exception:
            pass

        codes = db.get_lots_codes()
        for code in codes:
            name, model, code, storage, season, tires, disks, price, photo, status = db.get_lot(code)
            lot_id, lot_text, lot_price = db.get_selling_lot(code)

            try:
                if int(tires[-2:]) >= 18:
                    auc_price = "+ 500р."
                else:
                    auc_price = "+ 250р."
            except ValueError:
                auc_price = "+ 250р."

            bot_info = await bot.me
            try:
                await bot.edit_message_caption(
                    chat_id=channel_id,
                    message_id=lot_id,
                    caption=lot_text + f"💰 ТЕКУЩАЯ ЦЕНА: {lot_price}",
                    reply_markup=InlineKeyboardMarkup().add(
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
                )
            except aiogram.exceptions.MessageIdInvalid:
                continue
    return


async def edit_markups():
    global reminder_end_msg
    weekday = datetime.now().weekday() + 1
    # if True:
    if weekday in [1, 2, 3, 4, 5, 6, 7]:
        bot, db = get_bot_and_db()
        try:
            reminder_end_msg = db.get_reminder_id(stage="end")
            await bot.delete_message(
                chat_id=channel_id,
                message_id=reminder_end_msg
            )
            db.delete_reminder_id(stage="end")
        except Exception:
            pass
        codes = db.get_lots_codes()
        for code in codes:
            name, model, code, storage, season, tires, disks, price, photo, status = db.get_lot(code)
            lot_id, lot_text, lot_price = db.get_selling_lot(code)
            winners = winner_places(code, winner=True)

            if len(winners) != 0:
                first_place = winners
                winner = winner_places(code)[0][0]
                winners = winner_places(code)

                place_number = 0
                for elem in winners:
                    place_number += 1
                    db.add_place(tg_id=elem[0], code=code, place=place_number)

                admins = db.get_admins()

                if winner in admins:
                    fail_text = f"Лот №{code} не был никем выкуплен и будет выставлен позже"
                    next_place = db.get_tg_id_by_place(code=code, place=2)
                    db.add_winner(tg_id=winner, phone="admin", fullname="admin", code=code)

                    if next_place in admins:
                        next_place = db.get_tg_id_by_place(code=code, place=3)

                    if next_place is None:
                        await bot.send_message(
                            chat_id=admin_group,
                            text=fail_text
                        )
                        db.delete_now_lots(code)
                        db.delete_bids(code)
                        db.delete_saved_chats(code)
                        db.delete_places(code)
                        saved_chats = db.get_saved_lots(code=code)

                        repetition_count = db.get_repetition(code)

                        if repetition_count is None:
                            db.update_status_stock(code)
                            db.add_re_lot(code)
                        elif repetition_count in [1, 2]:
                            db.update_status_stock(code)
                            db.update_repetition(code)
                        elif repetition_count == 3:
                            db.update_status_deleted(code)
                            await bot.send_message(
                                chat_id=admin_group,
                                text=f"Лот №{code} удалён, так как никто не выкупил его в течении 3 дней."
                            )

                        if len(saved_chats) >= 0:
                            saved_chats.insert(0, (lot_id, channel_id))

                        for elem in saved_chats:
                            lot_id, chat_id = elem
                            try:
                                await bot.edit_message_caption(
                                    chat_id=chat_id,
                                    message_id=lot_id,
                                    caption=lot_text + f" 💰 ИТОГОВАЯ ЦЕНА: {lot_price}",
                                )

                                await bot.edit_message_reply_markup(
                                    chat_id=chat_id,
                                    message_id=lot_id,
                                    reply_markup=InlineKeyboardMarkup()
                                )
                            except aiogram.exceptions.MessageNotModified:
                                pass

                    else:
                        user_bids = db.get_bids_by_tg_id_and_code(tg_id=next_place[0], code=code)
                        best_bid = max(user_bids, key=lambda x: x[1])

                        first_place = list(best_bid[0])
                        first_place[-1] = "*"
                        first_place[-2] = "*"
                        first_place = "".join(first_place)

                        saved_chats = db.get_saved_lots(code=code)
                        if len(saved_chats) >= 0:
                            saved_chats.insert(0, (lot_id, channel_id))

                        await bot.send_message(
                            chat_id=next_place[0],
                            text=f"Прошлый победитель отказался выкупать лот.\n"
                                 f"Поздравляем! Ваша ставка сыграла. ЛОТ №{code} продан вам за {best_bid[1]} руб."
                                 "В ближайшее время с Вами свяжется Менеджер Аукциона и согласует условия оплаты, время и место, "
                                 "где Вы сможете забрать выигранный лот. "
                                 "Также Вы сможете обсудить условия доставки. Благодарим Вас за участие в Аукционе FRESH",
                            reply_markup=winner_markup
                        )

                        db.add_id_and_code(tg_id=next_place[0], code=code)
                        for elem in saved_chats:
                            lot_id, chat_id = elem
                            try:
                                await bot.edit_message_caption(
                                    chat_id=chat_id,
                                    message_id=lot_id,
                                    caption=lot_text + f"\n🥇{first_place}" + f"💰 ИТОГОВАЯ ЦЕНА: {best_bid[1]}",
                                )

                                await bot.edit_message_reply_markup(
                                    chat_id=chat_id,
                                    message_id=lot_id,
                                    reply_markup=InlineKeyboardMarkup()
                                )
                            except aiogram.exceptions.MessageNotModified:
                                pass




                else:

                    phone, fullname = db.user_by_id(tg_id=winner)
                    db.add_winner(tg_id=winner, phone=phone, fullname=fullname, code=code)
                    saved_chats = db.get_saved_lots(code=code)

                    await bot.send_message(
                        chat_id=winner,
                        text=f"Поздравляем! Ваша ставка сыграла. ЛОТ №{code} продан вам за {lot_price} руб."
                             "В ближайшее время с Вами свяжется Менеджер Аукциона и согласует условия оплаты, время и место, "
                             "где Вы сможете забрать выигранный лот. "
                             "Также Вы сможете обсудить условия доставки. Благодарим Вас за участие в Аукционе FRESH",
                        reply_markup=winner_markup
                    )

                    db.add_id_and_code(tg_id=winner, code=code)

                    if len(saved_chats) >= 0:
                        saved_chats.insert(0, (lot_id, channel_id))

                    winner = winner_places(code, winner=True)
                    for elem in saved_chats:
                        lot_id, chat_id = elem
                        try:
                            await bot.edit_message_caption(
                                chat_id=chat_id,
                                message_id=lot_id,
                                caption=lot_text + f"{winner}" + f"💰 ИТОГОВАЯ ЦЕНА: {lot_price}"
                            )

                            await bot.edit_message_reply_markup(
                                chat_id=chat_id,
                                message_id=lot_id,
                                reply_markup=InlineKeyboardMarkup()
                            )
                        except aiogram.exceptions.MessageNotModified:
                            continue


            else:
                db.delete_bids(code)
                db.delete_saved_chats(code)
                db.delete_places(code)
                await bot.send_message(
                    chat_id=admin_group,
                    text=f"Лот №{code} не был никем выкуплен и будет выставлен позже"
                )

                db.delete_now_lots(code)
                saved_chats = db.get_saved_lots(code=code)
                repetition_count = db.get_repetition(code)
                if repetition_count is None:
                    db.update_status_stock(code)
                    db.add_re_lot(code)
                elif repetition_count in [1, 2]:
                    db.update_status_stock(code)
                    db.update_repetition(code)
                elif repetition_count == 3:
                    db.update_status_deleted(code)
                    await bot.send_message(
                        chat_id=admin_group,
                        text=f"Лот №{code} удалён, так как никто не выкупил его в течении 3 дней."
                    )

                if len(saved_chats) >= 0:
                    saved_chats.insert(0, (lot_id, channel_id))

                try:
                    for elem in saved_chats:
                        lot_id, chat_id = elem
                        await bot.edit_message_caption(
                            chat_id=chat_id,
                            message_id=lot_id,
                            caption=lot_text + f" 💰 ИТОГОВАЯ ЦЕНА: {lot_price}",
                        )
                        await bot.edit_message_reply_markup(
                            chat_id=chat_id,
                            message_id=lot_id,
                            reply_markup=InlineKeyboardMarkup()
                        )
                except aiogram.exceptions.MessageNotModified:
                    # try:
                    #
                    # except aiogram.exceptions.MessageNotModified:
                    # # print("here we go again")
                    continue

                pass
    return


async def reminder():
    weekday = datetime.now().weekday() + 1
    if weekday in [1, 2, 3, 4, 5, 6, 7]:
        bot, db = get_bot_and_db()
        codes = db.get_lots_codes()

        if len(codes) > 0:
            reminder_end_msg = await bot.send_message(
                chat_id=channel_id,
                text="До конца аукциона осталось 10 мин. Успейте сделать последние ставки!"
            )
            db.add_reminders_id(
                message_id=reminder_end_msg.message_id,
                stage="end"
            )
        return
    return


async def reminder_beggining():
    weekday = datetime.now().weekday() + 1
    if weekday in [1, 2, 3, 4, 5, 6, 7]:
        bot, db = get_bot_and_db()
        codes = db.get_lots_codes()

        # if len(codes) > 0:
        reminder_begin_msg = await bot.send_message(
            chat_id=channel_id,
            text="До начала аукциона осталось 10 мин. Успейте сделать ставки!"
        )
        db.add_reminders_id(
            message_id=reminder_begin_msg.message_id,
            stage="begin"
        )
        # return
    return


async def scheduler():
    aioschedule.every().day.at("12:00").do(edit_lots) # 12:00
    aioschedule.every().day.at("12:50").do(reminder) # 12:50
    aioschedule.every().day.at("11:50").do(reminder_beggining) # 11:50
    aioschedule.every().day.at("13:00").do(edit_markups) # 13:00
    aioschedule.every().day.at("20:50").do(start_auction) # 18:30
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main_schedule():
    await asyncio.create_task(scheduler())


if __name__ == '__main__':
    asyncio.run(main_schedule())