from requests import request
from get_bot_and_db import get_bot_and_db
from config import access_token
import requests


async def upload_lots(chat: int):
    bot, db = get_bot_and_db()

    await bot.send_message(
        chat_id=chat,
        text="Начинаю, процесс может занять некоторое время"
    )
    response = request(
        "GET",
        "https://api.moysklad.ru/api/remap/1.2/entity/assortment",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept-Encoding": "gzip"
        }
    )

    codes = db.get_all_codes()
    lots_codes = list()

    for data in response.json()["rows"]:
        # try:
        name = data["name"]

        if name[:4] != "Тест" and "code" in data.keys():
            code = data["code"]
            attributes = data["attributes"]
            price = data.get("salePrices")
            if price is not None:
                price = price[0]["value"]

            wheels_or_tires = attributes[0]["value"]
            if "колеса" in wheels_or_tires.lower() or "колёса" in wheels_or_tires.lower() or "колесо" in wheels_or_tires.lower() or "резина" in wheels_or_tires.lower():
                brand_model = attributes[1]["value"]
                season = attributes[2]["value"]
                tire_parameters = attributes[3]["value"]
                disk_parameters = attributes[4]["value"]
                status = attributes[5]["value"]
                if status.lower() in ["отличное", "плохое", "среднее", "хорошее"]:
                    status = attributes[6]["value"]
                storage = None
                for num in range(5, 9):
                    try:
                        if attributes[num]["name"] == "Склад":
                            storage = attributes[num]["value"]
                            break
                    except IndexError:
                        continue
                photo_url = data["images"]["meta"]["href"]


                try:
                    photo_download = request("GET", photo_url,
                                             headers={"Authorization": f"Bearer {access_token}"}).json()

                except requests.exceptions.ReadTimeout:
                    continue
                if len(photo_download["rows"]) > 0:
                    photo = request("GET", photo_download["rows"][0]["meta"]["downloadHref"],
                                    headers={"Authorization": f"Bearer {access_token}"}).content

                    if status.lower() in ["принят", "подтвержден",
                                          "подтверждён"] and price is not None and price > 0 and str(
                            code) not in codes and storage is not None:
                        db.add_lot(
                            name=name,
                            code=code,
                            model=brand_model,
                            season=season,
                            storage=storage,
                            tires=tire_parameters,
                            disks=disk_parameters,
                            price=price // 100,
                            photo=photo
                        )

                        lots_codes.append(code)

            elif wheels_or_tires.lower() in ["шины", "шина"]:
                brand_model = attributes[1]["value"]
                season = attributes[2]["value"]
                tire_parameters = attributes[3]["value"]
                status = attributes[4]["value"]
                if status.lower() in ["отличное", "плохое", "среднее", "хорошее"]:
                    status = attributes[5]["value"]
                storage = None
                for num in range(5, 9):
                    try:
                        if attributes[num]["name"] == "Склад":
                            storage = attributes[num]["value"]
                            break
                    except IndexError:
                        continue
                photo_url = data["images"]["meta"]["href"]
                try:
                    photo_download = request("GET", photo_url,
                                             headers={"Authorization": f"Bearer {access_token}"}).json()

                except requests.exceptions.ReadTimeout:
                    continue
                if len(photo_download["rows"]) > 0:
                    photo = request("GET", photo_download["rows"][0]["meta"]["downloadHref"],
                                    headers={"Authorization": f"Bearer {access_token}"}).content
                    if status.lower() in ["принят", "подтвержден",
                                          "подтверждён"] and price is not None and price > 0 and str(
                            code) not in codes and storage is not None:
                        db.add_lot(
                            name=name,
                            code=code,
                            model=brand_model,
                            season=season,
                            storage=storage,
                            tires=tire_parameters,
                            disks=None,
                            price=price // 100,
                            photo=photo
                        )

                        lots_codes.append(code)

    await bot.send_message(
        chat_id=chat,
        text=f"Выгружено лотов: {len(lots_codes)}\n"
             f"Коды: {lots_codes}"
    )
