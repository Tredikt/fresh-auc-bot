from get_bot_and_db import get_bot_and_db
from xlsxwriter import Workbook
import os


async def get_users_statistics(tg_id):
    bot, db = get_bot_and_db()
    users_ids = db.get_users_ids()

    wb = Workbook("users-list.xlsx")
    worksheet = wb.add_worksheet()

    if os.path.isfile("users-list.xlsx"):
        os.remove("users-list.xlsx")

    row = 0
    worksheet.write(row, 0, "ФИ")
    worksheet.write(row, 1, "Телефон")
    worksheet.write(row, 2, "Количество участий")
    worksheet.write(row, 3, "Количество ставко")
    worksheet.write(row, 4, "Количество побед")
    worksheet.write(row, 5, "Количество выкупленных лотов")
    worksheet.write(row, 6, "Количество отказов от выкупа")
    worksheet.write(row, 7, "Выручка")
    worksheet.write(row, 8, "Средняя цена лота")

    for user_id in users_ids:
        if user_id is not None:
            row += 1

            phone, fullname = db.user_by_id(user_id)
            raise_bid = set(*db.get_bids_codes(user_id)) # code Количество аукционов в которых принимал участие (лот добавлен в избранное или сделана ставка)
            save_lots = set(*db.get_saved_lots_codes(user_id)) # code, tg_id
            take_part = len(raise_bid.union(save_lots))
            bids_count = len(db.get_bids_codes(user_id)) # количество ставок
            ransoms_count = len(db.get_ransom_price(user_id)) # количество выкупов
            victories_count = len(db.get_victory_count(user_id)) # количество побед
            refusials_count = len(db.get_refusials(user_id)) # количество отказов
            ransoms = db.get_ransom_price(user_id) # сумма выкупа
            ransom_sum = sum(ransoms)
            if len(ransoms) == 0:
                average_price = 0
            else:
                average_price = sum(ransoms) / len(ransoms)

            worksheet.write(row, 0, fullname)
            worksheet.write(row, 1, phone)
            worksheet.write(row, 2, take_part)
            worksheet.write(row, 3, bids_count)
            worksheet.write(row, 4, ransoms_count)
            worksheet.write(row, 5, victories_count)
            worksheet.write(row, 6, refusials_count)
            worksheet.write(row, 7, ransom_sum)
            worksheet.write(row, 8, average_price)

    wb.close()

    with open("users-list.xlsx", "rb") as document:
        await bot.send_document(
            chat_id=tg_id,
            caption="Файл с данными о всех пользователях:",
            document=document
        )
        os.remove("users-list.xlsx")






