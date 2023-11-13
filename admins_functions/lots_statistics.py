from get_bot_and_db import get_bot_and_db
from xlsxwriter import Workbook
import os


async def get_lots_statistics(tg_id):
    bot, db = get_bot_and_db()
    codes = db.get_sold_lots_codes()

    wb = Workbook("lots-list.xlsx")
    worksheet = wb.add_worksheet()

    if os.path.isfile("lots-list.xlsx"):
        os.remove("lots-list.xlsx")

    row = 0
    worksheet.write(row, 0, "Количество участвовавших партнеров")
    worksheet.write(row, 1, "Количество ставок")
    worksheet.write(row, 2, "На сколько увеличилась цена (в %)")

    for code in codes:
        bids_count = len(db.get_bids_ids(code=code))
        raise_bids = set(db.get_bids_ids(code=code))
        save_lots = set(db.get_saved_lots_ids(code=code))
        take_part = len(raise_bids.union(save_lots))
        name, model, code, storage, season, tires, disks, price, photo, status = db.get_lot(code)
        last_price = db.get_last_price(code)

        percentage = 0
        if last_price != 0:
            percentage = last_price / int(price.split(".")[0]) * 100 - 100

        row += 1
        worksheet.write(row, 0, take_part)
        worksheet.write(row, 1, bids_count)
        worksheet.write(row, 2, percentage)

    wb.close()

    with open("lots-list.xlsx", "rb") as document:
        await bot.send_document(
            chat_id=tg_id,
            caption="Файл с данными о всех лотах:",
            document=document
        )
        os.remove("lots-list.xlsx")