"""
Функция для выгрузки Шинных Лотов в базу данных
"""

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
        # print(data)
        name = data["name"]

        if name[:4] != "Тест" and "code" in data.keys():
            code = data["code"]


            try:
                attributes = data["attributes"]
            except KeyError:
                continue

            price = data.get("salePrices")
            if price is not None:
                price = price[0]["value"]
            db.update_uploaded_price(code=code, price=price)

            if code in codes:
                continue
            else:
                wheels_or_tires = attributes[0]["value"]
                if "колеса" in wheels_or_tires.lower() or "колёса" in wheels_or_tires.lower() or "колес" in wheels_or_tires.lower() or "резина" in wheels_or_tires.lower():
                    # print(code, attributes)
                    brand_model = attributes[1]["value"]
                    season = attributes[2]["value"]
                    tire_parameters = attributes[3]["value"]
                    status = attributes[5]["value"]
                    google_disk_link = None

                    if status.lower() in ["отличное", "плохое", "среднее", "хорошее", "нормальное"]:
                        status = attributes[6]["value"]

                    storage = None
                    stage = None
                    disk_parameters = None
                    for num in range(3, 11):
                        try:
                            if attributes[num]["name"] == "Склад":
                                storage = attributes[num]["value"]["name"]
                            elif attributes[num]["name"] == "Ссылка на фотографии":
                                google_disk_link = attributes[num]["value"]
                            elif attributes[num]["name"] == "Состояние":
                                stage = attributes[num]["value"]
                            elif attributes[num]["name"] == "Параметры дисков":
                                disk_parameters = attributes[num]["value"]
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


                        if (status.lower() in ["принят", "подтвержден",
                                               "подтверждён", "принято",
                                               "подтверждено"] and price is not None and price > 0 and
                                str(code) not in codes and storage is not None):
                            lots_codes.append(code)
                            db.add_lot(
                                name=name,
                                code=code,
                                model=brand_model,
                                season=season,
                                storage=storage,
                                tires=tire_parameters,
                                disks=disk_parameters,
                                price=price // 100,
                                photo=photo,
                                google_link=google_disk_link,
                                stage=stage
                            )

                elif wheels_or_tires.lower() in ["шины", "шина"]:
                    brand_model = attributes[1]["value"]
                    season = attributes[2]["value"]
                    tire_parameters = attributes[3]["value"]
                    status = attributes[4]["value"]
                    if status.lower() in ["отличное", "плохое", "среднее", "хорошее", "нормальное"]:
                        status = attributes[5]["value"]

                    storage = None
                    google_disk_link = None
                    stage = None
                    for num in range(3, 11):
                        try:
                            if attributes[num]["name"] == "Склад":
                                storage = attributes[num]["value"]
                            elif attributes[num]["name"] == "Ссылка на фотографии":
                                google_disk_link = attributes[num]["value"]
                            elif attributes[num]["name"] == "Состояние":
                                stage = attributes[num]["value"]
                        except IndexError:
                            continue
                    photo_url = data["images"]["meta"]["href"]
                    try:
                        photo_download = request("GET", photo_url,
                                                 headers={"Authorization": f"Bearer {access_token}"}).json()

                    except requests.exceptions.ReadTimeout:
                        continue

                    print(f"{status =} {price =} {code =} {storage =}")
                    if len(photo_download["rows"]) > 0:
                        photo = request("GET", photo_download["rows"][0]["meta"]["downloadHref"],
                                        headers={"Authorization": f"Bearer {access_token}"}).content
                        if status.lower() in ["принят", "подтвержден",
                                              "подтверждён", "принято",
                                              "подтверждено"] and price is not None and price > 0 and str(
                            code) not in codes and storage is not None:
                            lots_codes.append(code)
                            db.add_lot(
                                name=name,
                                code=code,
                                model=brand_model,
                                season=season,
                                storage=storage,
                                tires=tire_parameters,
                                disks=None,
                                price=price // 100,
                                photo=photo,
                                google_link=google_disk_link,
                                stage=stage
                            )

    await bot.send_message(
        chat_id=chat,
        text=f"Выгружено лотов: {len(lots_codes)}\n"
             f"Коды: {lots_codes}"
    )


d = {'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/04810ea8-a338-11ee-0a80-00f0005b009d',
              'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata', 'type': 'product',
              'mediaType': 'application/json',
              'uuidHref': 'https://online.moysklad.ru/app/#good/edit?id=048103bb-a338-11ee-0a80-00f0005b0093'},
     'id': '04810ea8-a338-11ee-0a80-00f0005b009d', 'accountId': '0795996b-26dc-11ee-0a80-03cd000037cb', 'owner': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/employee/aa2d2eda-877d-11ee-0a80-0eb3003510e7',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/employee/metadata', 'type': 'employee',
                 'mediaType': 'application/json',
                 'uuidHref': 'https://online.moysklad.ru/app/#employee/edit?id=aa2d2eda-877d-11ee-0a80-0eb3003510e7'}},
     'shared': True, 'group': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/group/721857f3-2c97-11ee-0a80-0b2d0014608a',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/group/metadata', 'type': 'group',
                 'mediaType': 'application/json'}}, 'updated': '2023-12-25 18:12:28.249',
     'name': '1856515NN251223_Резина_NiTTO', 'code': '1856515NN251223', 'externalCode': '1856515NN251223',
     'archived': False, 'pathName': '', 'useParentVat': True, 'uom': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/uom/991c77c7-2c90-11ee-0a80-0302000ba4a7',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/uom/metadata', 'type': 'uom',
                 'mediaType': 'application/json'}}, 'images': {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/04810ea8-a338-11ee-0a80-00f0005b009d/images',
        'type': 'image', 'mediaType': 'application/json', 'size': 9, 'limit': 1000, 'offset': 0}},
     'minPrice': {'value': 0.0, 'currency': {
         'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/07eaaf5d-26dc-11ee-0a80-0d350007b4d5',
                  'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/metadata', 'type': 'currency',
                  'mediaType': 'application/json',
                  'uuidHref': 'https://online.moysklad.ru/app/#currency/edit?id=07eaaf5d-26dc-11ee-0a80-0d350007b4d5'}}},
     'salePrices': [{'value': 0.0, 'currency': {
         'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/07eaaf5d-26dc-11ee-0a80-0d350007b4d5',
                  'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/metadata', 'type': 'currency',
                  'mediaType': 'application/json',
                  'uuidHref': 'https://online.moysklad.ru/app/#currency/edit?id=07eaaf5d-26dc-11ee-0a80-0d350007b4d5'}},
                     'priceType': {'meta': {
                         'href': 'https://api.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/07eaf3c8-26dc-11ee-0a80-0d350007b4d6',
                         'type': 'pricetype', 'mediaType': 'application/json'},
                                   'id': '07eaf3c8-26dc-11ee-0a80-0d350007b4d6', 'name': 'Цена продажи',
                                   'externalCode': 'cbcf493b-55bc-11d9-848a-00112f43529a'}}], 'buyPrice': {'value': 0.0,
                                                                                                           'currency': {
                                                                                                               'meta': {
                                                                                                                   'href': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/07eaaf5d-26dc-11ee-0a80-0d350007b4d5',
                                                                                                                   'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/metadata',
                                                                                                                   'type': 'currency',
                                                                                                                   'mediaType': 'application/json',
                                                                                                                   'uuidHref': 'https://online.moysklad.ru/app/#currency/edit?id=07eaaf5d-26dc-11ee-0a80-0d350007b4d5'}}},
     'barcodes': [{'ean13': '2000000002231'}], 'paymentItemType': 'GOOD', 'discountProhibited': False, 'weight': 0.0,
     'volume': 0.0, 'variantsCount': 0, 'isSerialTrackable': False, 'trackingType': 'NOT_TRACKED', 'files': {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/04810ea8-a338-11ee-0a80-00f0005b009d/files',
        'type': 'files', 'mediaType': 'application/json', 'size': 0, 'limit': 1000, 'offset': 0}}, 'stock': 0.0,
     'reserve': 0.0, 'inTransit': 0.0, 'quantity': 0.0}
