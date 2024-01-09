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

            if code in codes:
                continue
            else:
                attributes = data["attributes"]
                price = data.get("salePrices")
                if price is not None:
                    price = price[0]["value"]

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
                        # print(code, storage, status, price)
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

                    # print(f"{status =} {price =} {code =} {storage =}")
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


d = {'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/8b7744c6-92c8-11ee-0a80-0ff60000779a',
              'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata', 'type': 'product',
              'mediaType': 'application/json',
              'uuidHref': 'https://online.moysklad.ru/app/#good/edit?id=8b7730c3-92c8-11ee-0a80-0ff600007790'},
     'id': '8b7744c6-92c8-11ee-0a80-0ff60000779a', 'accountId': '0795996b-26dc-11ee-0a80-03cd000037cb', 'owner': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/employee/aa2d2eda-877d-11ee-0a80-0eb3003510e7',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/employee/metadata', 'type': 'employee',
                 'mediaType': 'application/json',
                 'uuidHref': 'https://online.moysklad.ru/app/#employee/edit?id=aa2d2eda-877d-11ee-0a80-0eb3003510e7'}},
     'shared': True, 'group': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/group/721857f3-2c97-11ee-0a80-0b2d0014608a',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/group/metadata', 'type': 'group',
                 'mediaType': 'application/json'}}, 'updated': '2023-12-04 20:14:12.569',
     'name': '019555_Резина_Bridgestone', 'code': '019555', 'externalCode': '019555', 'archived': False, 'pathName': '',
     'useParentVat': True, 'uom': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/uom/991c77c7-2c90-11ee-0a80-0302000ba4a7',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/uom/metadata', 'type': 'uom',
                 'mediaType': 'application/json'}}, 'images': {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/8b7744c6-92c8-11ee-0a80-0ff60000779a/images',
        'type': 'image', 'mediaType': 'application/json', 'size': 0, 'limit': 1000, 'offset': 0}},
     'minPrice': {'value': 0.0, 'currency': {
         'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/07eaaf5d-26dc-11ee-0a80-0d350007b4d5',
                  'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/metadata', 'type': 'currency',
                  'mediaType': 'application/json',
                  'uuidHref': 'https://online.moysklad.ru/app/#currency/edit?id=07eaaf5d-26dc-11ee-0a80-0d350007b4d5'}}},
     'salePrices': [{'value': 700000.0, 'currency': {
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
     'barcodes': [{'ean13': '2000000001807'}], 'attributes': [{'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612914-2c8f-11ee-0a80-11e40013a426',
        'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612914-2c8f-11ee-0a80-11e40013a426',
                                                               'name': 'Предмет', 'type': 'text', 'value': 'Резина'}, {
                                                                  'meta': {
                                                                      'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612bc0-2c8f-11ee-0a80-11e40013a427',
                                                                      'type': 'attributemetadata',
                                                                      'mediaType': 'application/json'},
                                                                  'id': 'dd612bc0-2c8f-11ee-0a80-11e40013a427',
                                                                  'name': 'Марка, модель', 'type': 'text',
                                                                  'value': 'Bridgestone Blizzak'}, {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612c6c-2c8f-11ee-0a80-11e40013a428',
        'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612c6c-2c8f-11ee-0a80-11e40013a428',
                                                                                                    'name': 'Сезон',
                                                                                                    'type': 'text',
                                                                                                    'value': 'Зима шипы'},
                                                              {'meta': {
                                                                  'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612d24-2c8f-11ee-0a80-11e40013a429',
                                                                  'type': 'attributemetadata',
                                                                  'mediaType': 'application/json'},
                                                               'id': 'dd612d24-2c8f-11ee-0a80-11e40013a429',
                                                               'name': 'Параметры шин', 'type': 'text',
                                                               'value': '195/55R16'}, {'meta': {
            'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612ea4-2c8f-11ee-0a80-11e40013a42b',
            'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612ea4-2c8f-11ee-0a80-11e40013a42b',
                                                                                       'name': 'Состояние',
                                                                                       'type': 'text',
                                                                                       'value': 'Хорошее'}, {'meta': {
            'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612f4f-2c8f-11ee-0a80-11e40013a42c',
            'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612f4f-2c8f-11ee-0a80-11e40013a42c',
                                                                                                             'name': 'Статус',
                                                                                                             'type': 'text',
                                                                                                             'value': 'Принято'},
                                                              {'meta': {
                                                                  'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/77397075-6830-11ee-0a80-1196001195c2',
                                                                  'type': 'attributemetadata',
                                                                  'mediaType': 'application/json'},
                                                               'id': '77397075-6830-11ee-0a80-1196001195c2',
                                                               'name': 'Склад', 'type': 'string',
                                                               'value': 'Воронеж Север'}, {'meta': {
            'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/998a611b-82fa-11ee-0a80-0e34001752ad',
            'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': '998a611b-82fa-11ee-0a80-0e34001752ad',
                                                                                           'name': 'Ссылка на фотографии',
                                                                                           'type': 'link',
                                                                                           'value': 'https://drive.google.com/drive/folders/1DTpLQf8whUegQLYB_LU86pqaW664OrXq?usp=sharing'}],
     'paymentItemType': 'GOOD', 'discountProhibited': False, 'weight': 0.0, 'volume': 0.0, 'variantsCount': 0,
     'isSerialTrackable': False, 'trackingType': 'NOT_TRACKED', 'files': {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/8b7744c6-92c8-11ee-0a80-0ff60000779a/files',
        'type': 'files', 'mediaType': 'application/json', 'size': 0, 'limit': 1000, 'offset': 0}}, 'stock': 0.0,
     'reserve': 0.0, 'inTransit': 0.0, 'quantity': 0.0}
