import aioschedule
from states_handlers.bot_states import AuctionStates
from get_bot_and_db import get_bot_and_db
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
from admins_functions.winner_places import winner_places
from blanks.bot_markups import winner_markup
from auction import auc_bot

from datetime import datetime
from config import channel_id, admin_group


async def start_auction():
    print("beginning")
    if datetime.now().weekday() in [1, 2, 3, 4, 5, 6, 7]:
        print("i'm here")
        bot, db = get_bot_and_db()
        three_lots = db.get_three_lots()
        print(three_lots)

        for elem in three_lots:
            print("lots")
            name, model, code, season, tires, disks, price, photo = elem

            if int(tires[-2:]) >= 18:
                auc_price = "+ 500р."
            else:
                auc_price = "+ 250р."

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

            text = f"🔥 СТАРТ {price} ₽🔥\n\n" \
                    f"🌍 Место склада\n" \
                    f"✅ Шины {disks}\n" \
                    f"✅ {season}\n" \
                    f"✅ {tires}\n\n" \
                    f"❗️ Продолжительность аукциона - 1 час!\n\n" \
                    f"Администратор аукциона: @KristinaBashmakova\n\n" \
                    f"📌 Лот № {code}\n"


            db.update_status_auction(code)

            lot_message = f"Предстоящий ЛОТ!!!\n"
            if datetime.now().weekday() == 5:
                lot_message = "Добрый день! Данный лот будет разыгран в понедельник в 12:00\n"

            auc_message = await bot.send_message(
                chat_id=channel_id,
                # photo=photo,
                text=lot_message + text + f"💰 ТЕКУЩАЯ ЦЕНА: {price}",
                # reply_markup=markup
            )

            db.add_auc_lot(lot_id=auc_message.message_id, lot_text=text, lot_price=price, code=code)
            await asyncio.sleep(15 * 60)


async def edit_lots():
    if datetime.now().weekday() in [1, 2, 3, 4, 5, 6, 7]:
        bot, db = get_bot_and_db()

        codes = db.get_lots_codes()
        for code in codes:
            name, model, code, season, tires, disks, price, photo, status = db.get_lot(code)
            lot_id, lot_text, lot_price = db.get_selling_lot(code)
            if int(tires[-2:]) >= 18:
                auc_price = "+ 500р."
            else:
                auc_price = "+ 250р."

            await bot.edit_message_text(
                chat_id=channel_id,
                message_id=lot_id,
                # photo=photo,
                text=lot_text + f"💰 ТЕКУЩАЯ ЦЕНА: {lot_price}",
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(
                        text=auc_price, callback_data=f"raiseprice_{code}"
                    )
                ).add(
                    InlineKeyboardButton(
                        text="💾", callback_data=f"save_{code}"
                    ),
                    InlineKeyboardButton(
                        text="⏳", callback_data=f"time_{code}"
                    ),
                    InlineKeyboardButton(
                        text="⚠️", callback_data="warning"
                    )
                )
            )
    return



async def edit_markups():
    if datetime.now().weekday() in [1, 2, 3, 4, 5]:
        bot, db = get_bot_and_db()
        codes = db.get_lots_codes()

        if (datetime.now().hour * 60 + datetime.now().minute) == (13 * 60):
            for code in codes:

                name, model, code, season, tires, disks, price, photo, status = db.get_lot(code)
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

                    saved_chats = db.get_saved_lots(code=code)
                    if len(saved_chats) > 0:
                        saved_chats.insert(0, (lot_id, channel_id))
                    for elem in saved_chats:
                        lot_id, chat_id = elem
                        await bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=lot_id,
                            text=lot_text + f"\n{first_place}" + f"💰 ИТОГОВАЯ ЦЕНА: {lot_price}",
                            reply_markup=None
                        )

                    db.add_winner(tg_id=winner, phone="admin", fullname="admin", code=code)
                    admins = db.get_admins()

                    if winner in admins:
                        next_place = db.get_tg_id_by_place(code=code, place=2)
                        if next_place is None:
                            await bot.send_message(
                                chat_id=admin_group,
                                text=f"Лот №{code} не был никем выкуплен и будет выставлен позже"
                            )
                        else:
                            lot_id, lot_text, lot_price = db.get_selling_lot(code)
                            await bot.send_message(
                                chat_id=next_place[0],
                                text=f"Прошлый победитель отказался выкупать лот.\n"
                                     f"Поздравляем! Ваша ставка сыграла. ЛОТ №{code} продан вам за {lot_price} руб."
                                     "В ближайшее время с Вами свяжется Менеджер Аукциона и согласует условия оплаты, время и место, "
                                     "где Вы сможете забрать выигранный лот. "
                                     "Также Вы сможете обсудить условия доставки. Благодарим Вас за участие в Аукционе FRESH",
                                reply_markup=winner_markup
                            )
                            await AuctionStates.winner.set()
                            await auc_bot.get_code(tg_id=next_place, code=code)


                    else:
                        await bot.send_message(
                            chat_id=winner,
                            text=f"Поздравляем! Ваша ставка сыграла. ЛОТ №{code} продан вам за {lot_price} руб."
                                 "В ближайшее время с Вами свяжется Менеджер Аукциона и согласует условия оплаты, время и место, "
                                 "где Вы сможете забрать выигранный лот. "
                                 "Также Вы сможете обсудить условия доставки. Благодарим Вас за участие в Аукционе FRESH",
                            reply_markup=winner_markup
                        )
                        await AuctionStates.winner.set()
                        await auc_bot.get_code(tg_id=winner, code=code)

                else:

                    saved_chats = db.get_saved_lots(code=code)

                    if len(saved_chats) > 0:
                        saved_chats.insert(0, (lot_id, channel_id))

                    for elem in saved_chats:
                        lot_id, chat_id = elem
                        await bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=lot_id,
                            text=lot_text + f" 💰 ИТОГОВАЯ ЦЕНА: {lot_price}",
                        )

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
    return





async def reminder():
    bot, db = get_bot_and_db()
    codes = db.get_lots_codes()

    if len(codes) > 0:
        await bot.send_message(
            chat_id=channel_id,
            text="До конца аукциона осталось 10 мин. Успейте сделать последние ставки!"
        )
    return


async def scheduler():
    aioschedule.every().day.at("12:00").do(edit_lots) #12:00
    aioschedule.every().day.at("12:50").do(reminder)
    aioschedule.every().day.at("13:00").do(edit_markups)
    aioschedule.every().day.at("18:30").do(start_auction) #18:30
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main_schedule():
    await asyncio.create_task(scheduler())


if __name__ == '__main__':
    asyncio.run(main_schedule())