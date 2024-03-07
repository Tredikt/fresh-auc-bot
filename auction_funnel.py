"""
При запуске данного файла aioschedule проверяет время и запускает различные функции:
1) Запуск Аукциона
2) Окончание Аукциона
3) Напомнинание об Аукционе
"""

import aioschedule
from get_bot_and_db import get_bot_and_db
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
from admins_functions.winner_places import winner_places
import aiogram
from datetime import datetime
from config import channel_id, admin_group


bot, db = get_bot_and_db()


async def start_auction(manually=None):
    weekday = datetime.now().weekday() + 1
    if weekday in [1, 2, 3, 4, 5] or manually:
        bot, db = get_bot_and_db()
        relots_codes = db.get_re_lot()
        all_codes = db.get_all_codes()

        lots_for_auc = db.get_draw_lots()

        for elem in lots_for_auc:
            name, model, code, storage, season, tires, disks, price, photo, status, google_link, stage = elem
            if google_link is None:
                google_link = ""
            else:
                google_link = "✅" + google_link + "\n\nПо ссылке подробные фотографии лота\n\n"

            if disks is not None and disks.lower() not in ["хорошее", "плохое", "среднее", "отличное", "мало шипов. плохое"]:
                text = f"🔥 СТАРТ {price} ₽🔥\n\n" \
                       f"✅ {model}\n" \
                       f"✅ Колёса {disks}\n" \
                       f"✅ {tires}\n" \
                       f"✅ Состояние: {stage}\n" \
                       f"✅ {season}\n" + google_link + f"🌍 Место склада {storage}\n\n" \
                        f"❗️ Продолжительность аукциона - 1 час ❗️ \n\n" \
                        f"Администратор аукциона: @Ataev_Sergey\n\n" \
                        f"📌 Лот № {code}\n"
            else:
                text = f"🔥 СТАРТ {price} ₽🔥\n\n" \
                       f"✅ {model}\n" \
                       f"✅ Шины {tires}\n" \
                       f"✅ Состояние: {stage}\n" \
                       f"✅ {season}\n" + google_link + f"🌍 Место склада {storage}\n\n" \
                       f"❗️ Продолжительность аукциона - 1 час ❗️\n\n" \
                       f"Администратор аукциона: @Ataev_Sergey\n\n" \
                       f"📌 Лот № {code}\n"
            db.update_status_auction(code)

            month = datetime.now().month
            day = datetime.now().day
            if len(str(month)) < 2:
                month = "0" + str(month)
            if 1100 <= datetime.now().minute + datetime.now().hour * 60 <= 1440:
                day += 1

            if len(str(day)) < 2:
                day = "0" + str(day)
                
            lot_message = f"Данный лот будет разыгран {day}.{month} в 12:00!!!\n"
            if datetime.now().weekday() + 1 == 5:
                lot_message = "Добрый вечер! Данный лот будет разыгран в понедельник в 12:00\n"

            auc_message = await bot.send_photo(
                chat_id=channel_id,
                photo=photo,
                caption=lot_message + text + f"💰 ТЕКУЩАЯ ЦЕНА: {price}",
                # reply_markup=markup
            )

            db.add_auc_lot(lot_id=auc_message.message_id, lot_text=text, lot_price=price, code=code)
            await asyncio.sleep(5 * 60)


async def edit_lots():
    weekday = datetime.now().weekday() + 1
    # if True:
    if weekday in [1, 2, 3, 4, 5]:
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

        waiting_codes = db.get_waiting_lots()
        codes = db.get_lots_codes()
        for code in codes:
            if code not in waiting_codes:
                # print(code)
                name, model, code, storage, season, tires, disks, price, photo, status, google_link, stage = db.get_lot(code)
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
                    await bot.edit_message_reply_markup(
                        chat_id=channel_id,
                        message_id=lot_id,
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
                except:
                    pass
                #
                # try:
                #     await bot.edit_message_caption(
                #         chat_id=channel_id,
                #         message_id=lot_id,
                #         caption=lot_text + f"💰 ТЕКУЩАЯ ЦЕНА: {lot_price}",
                #     )
                # except aiogram.exceptions.MessageIdInvalid:
                #     continue
                # except aiogram.exceptions.MessageNotModified:
                #     continue
                # except Exception:
                #     pass


    return


async def edit_markups():
    global reminder_end_msg
    weekday = datetime.now().weekday() + 1
    # if True:
    if weekday in [1, 2, 3, 4, 5]:
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
            name, model, code, storage, season, tires, disks, price, photo, status, google_link, stage = db.get_lot(code)
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

                        name, model, code, storage, season, tires, disks, price, photo, status, google_link, stage = db.get_lot(code)
                        try:
                            price = int(price)
                        except ValueError:
                            price = int(price.split(".")[0])

                        new_price = price - (price * 0.3)
                        new_price = list(str(new_price))
                        new_price[-3] = "0"
                        new_price = "".join(new_price)
                        db.edit_lot_price(code, new_price)

                        repetition_count = db.get_repetition(code)

                        if repetition_count is None:
                            db.update_status_stock(code)
                            db.add_re_lot(code)
                        elif repetition_count in [1, 2]:
                            db.update_status_stock(code)
                            db.update_repetition(code)
                        elif repetition_count == 3:
                            # db.update_status_deleted(code)
                            db.delete_lot(code)
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

                            name, model, code, storage, season, tires, disks, price, photo, status, google_link, stage = db.get_lot(code)
                            try:
                                price = int(price)
                            except ValueError:
                                price = int(price.split(".")[0])

                            new_price = price - (price * 0.3)
                            new_price = str(new_price).split()
                            new_price[-1] = "0"
                            new_price = int("".join(new_price))
                            db.edit_lot_price(code, new_price)

                    else:
                        user_bids = db.get_bids_by_tg_id_and_code(tg_id=next_place[0], code=code)
                        best_bid = max(user_bids, key=lambda x: x[1])

                        first_place = list(best_bid[0])
                        for num in range(1, len(first_place) - 1):
                            first_place[-num] = "*"
                        first_place = "".join(first_place)

                        saved_chats = db.get_saved_lots(code=code)
                        if len(saved_chats) >= 0:
                            saved_chats.insert(0, (lot_id, channel_id))
                        db.update_status_waiting(code=code)
                        await bot.send_message(
                            chat_id=next_place[0],
                            text=f"Прошлый победитель отказался выкупать лот.\n"
                                 f"Поздравляем! Ваша ставка сыграла. ЛОТ №{code} продан вам за {best_bid[1]} руб."
                                 "В ближайшее время с Вами свяжется Менеджер Аукциона и согласует условия оплаты, время и место, "
                                 "где Вы сможете забрать выигранный лот. "
                                 "Также Вы сможете обсудить условия доставки. Благодарим Вас за участие в Аукционе FRESH",
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton(
                                    text="Хорошо, жду",
                                    callback_data=f"waiting_{code}"
                                )
                            ).add(
                            InlineKeyboardButton(
                                text="Передумал",
                                callback_data=f"refusial_{code}"
                            )
                            ))

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
                    db.update_status_waiting(code=code)

                    await bot.send_message(
                        chat_id=winner,
                        text=f"Поздравляем! Ваша ставка сыграла. ЛОТ №{code} продан вам за {lot_price} руб."
                             "В ближайшее время с Вами свяжется Менеджер Аукциона и согласует условия оплаты, время и место, "
                             "где Вы сможете забрать выигранный лот. "
                             "Также Вы сможете обсудить условия доставки. Благодарим Вас за участие в Аукционе FRESH",
                        reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton(
                                    text="Хорошо, жду",
                                    callback_data=f"waiting_{code}"
                                )
                            ).add(
                            InlineKeyboardButton(
                                text="Передумал",
                                callback_data=f"refusial_{code}"
                            )
                        )
                    )

                    if len(saved_chats) >= 0:
                        saved_chats.insert(0, (lot_id, channel_id))

                    winner = winner_places(code, winner=True)
                    print(winner)
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
                name, model, code, storage, season, tires, disks, price, photo, status, google_link, stage = db.get_lot(code)
                try:
                    price = int(price)
                except ValueError:
                    price = int(price.split(".")[0])

                new_price = price - (price * 0.3)
                new_price = list(str(new_price))
                new_price[-3] = "0"
                new_price = "".join(new_price)
                db.edit_lot_price(code, new_price)

                repetition_count = db.get_repetition(code)

                if repetition_count is None:
                    db.update_status_stock(code)
                    db.add_re_lot(code)
                elif repetition_count in [1, 2]:
                    db.update_status_stock(code)
                    db.update_repetition(code)
                elif repetition_count == 3:
                    db.delete_lot(code)
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
    if weekday in [1, 2, 3, 4, 5]:
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
    if weekday in [1, 2, 3, 4, 5]:
        bot, db = get_bot_and_db()
        codes = db.get_lots_codes()

        if len(codes) > 0:
            reminder_begin_msg = await bot.send_message(
                chat_id=channel_id,
                text="До начала аукциона осталось 10 мин. Успейте сделать ставки!"
            )
            db.add_reminders_id(
                message_id=reminder_begin_msg.message_id,
                stage="begin"
            )
        return
    return


async def scheduler():
    aioschedule.every().day.at("12:00").do(edit_lots) # 12:00
    aioschedule.every().day.at("12:50").do(reminder) # 12:50
    aioschedule.every().day.at("11:50").do(reminder_beggining) # 11:50
    aioschedule.every().day.at("13:00").do(edit_markups) # 13:00
    aioschedule.every().day.at("18:20").do(start_auction)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(60)


async def main_schedule():
    await asyncio.create_task(scheduler())


if __name__ == '__main__':
    asyncio.run(main_schedule())