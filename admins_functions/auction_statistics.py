from get_bot_and_db import get_bot_and_db
from xlsxwriter import Workbook
import os


async def get_auction_statistics(tg_id):
    bot, db = get_bot_and_db()
    codes = db.get_sold_lots_codes()

    wb = Workbook("auc-list.xlsx")
    worksheet = wb.add_worksheet()

    if os.path.isfile("auc-list.xlsx"):
        os.remove("auc-list.xlsx")

    row = 0
    worksheet.write(row, 0, "Количество разыгранных уникальны лотов (без повторов)")
    worksheet.write(row, 1, "Количество повторных лотов")
    worksheet.write(row, 2, "Сколько пользователей принимало участие в торгах")
    worksheet.write(row, 3, "Средний прирост цены")
    worksheet.write(row, 4, "Количество выкупленных лотов")
    worksheet.write(row, 5, "Количество отказов от выкупа")
    worksheet.write(row, 6, "Итоговая выручка")



    lots_count = len(codes) #where status=sold/auc количество разыгранных уникальны лотов
    relots_count = len(db.get_re_lot()) #количество повторных лотов (более 1 раза)
    # сколько пользователей принимали участие в торгах
    raise_bids = set(db.get_all_bids_ids())
    save_lots = set(db.get_all_saved_lots_id())
    take_part = len(raise_bids.union(save_lots)) # участие
    count = 0
    prices_list = list()

    for code in codes:
        count += 1
        name, model, code, storage, season, tires, disks, price, photo, status = db.get_lot(code)
        last_price = db.get_last_price(code)
        percentage = 0
        if last_price != 0:
            percentage = last_price / int(price.split(".")[0]) * 100 - 100 # прирост цены (%)
        prices_list.append(percentage)
    else:
        count = 1
    average_growing_price = sum(prices_list) / count
    ransoms_count = len(db.get_ransom_codes()) # количество выкупленных лотов
    refusials_count = len(db.get_refusials_codes()) # количество отказов от выкупа
    final_ransom = sum(db.get_ransom_prices()) # итоговая выручка

    row += 1
    worksheet.write(row, 0, lots_count)
    worksheet.write(row, 1, relots_count)
    worksheet.write(row, 2, take_part)
    worksheet.write(row, 3, average_growing_price)
    worksheet.write(row, 4, ransoms_count)
    worksheet.write(row, 5, refusials_count)
    worksheet.write(row, 6, final_ransom)

    wb.close()

    with open("auc-list.xlsx", "rb") as document:
        await bot.send_document(
            chat_id=tg_id,
            caption="Файл с данными о аукционе:",
            document=document
        )
        os.remove("auc-list.xlsx")