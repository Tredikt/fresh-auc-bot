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
            attributes = data["attributes"]
            price = data.get("salePrices")
            if price is not None:
                price = price[0]["value"]

            wheels_or_tires = attributes[0]["value"]
            if "колеса" in wheels_or_tires.lower() or "колёса" in wheels_or_tires.lower() or "колесо" in wheels_or_tires.lower() or "резина" in wheels_or_tires.lower():
                # print(code)
                brand_model = attributes[1]["value"]
                season = attributes[2]["value"]
                tire_parameters = attributes[3]["value"]
                disk_parameters = attributes[4]["value"]
                status = attributes[5]["value"]
                if status.lower() in ["отличное", "плохое", "среднее", "хорошее", "нормальное"]:
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
                if status.lower() in ["отличное", "плохое", "среднее", "хорошее", "нормальное"]:
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


d = {'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/942935e3-816e-11ee-0a80-012500449568',
              'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata', 'type': 'product',
              'mediaType': 'application/json',
              'uuidHref': 'https://online.moysklad.ru/app/#good/edit?id=942923d3-816e-11ee-0a80-01250044955e'},
     'id': '942935e3-816e-11ee-0a80-012500449568', 'accountId': '0795996b-26dc-11ee-0a80-03cd000037cb', 'owner': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/employee/1074d62b-7efe-11ee-0a80-01250012f9b8',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/employee/metadata', 'type': 'employee',
                 'mediaType': 'application/json',
                 'uuidHref': 'https://online.moysklad.ru/app/#employee/edit?id=1074d62b-7efe-11ee-0a80-01250012f9b8'}},
     'shared': True, 'group': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/group/7218334b-2c97-11ee-0a80-0b2d00146089',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/group/metadata', 'type': 'group',
                 'mediaType': 'application/json'}}, 'updated': '2023-11-13 09:57:09.612',
     'name': '037802_Резина на штампах', 'code': '037802', 'externalCode': '037802', 'archived': False, 'pathName': '',
     'useParentVat': True, 'uom': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/uom/991c77c7-2c90-11ee-0a80-0302000ba4a7',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/uom/metadata', 'type': 'uom',
                 'mediaType': 'application/json'}}, 'images': {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/942935e3-816e-11ee-0a80-012500449568/images',
        'type': 'image', 'mediaType': 'application/json', 'size': 9, 'limit': 1000, 'offset': 0}},
     'minPrice': {'value': 0.0, 'currency': {
         'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/07eaaf5d-26dc-11ee-0a80-0d350007b4d5',
                  'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/metadata', 'type': 'currency',
                  'mediaType': 'application/json',
                  'uuidHref': 'https://online.moysklad.ru/app/#currency/edit?id=07eaaf5d-26dc-11ee-0a80-0d350007b4d5'}}},
     'salePrices': [{'value': 400000.0, 'currency': {
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
     'barcodes': [{'ean13': '2000000001258'}], 'attributes': [{'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612914-2c8f-11ee-0a80-11e40013a426',
        'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612914-2c8f-11ee-0a80-11e40013a426',
                                                               'name': 'Предмет', 'type': 'text',
                                                               'value': 'Резина на штампах'}, {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612bc0-2c8f-11ee-0a80-11e40013a427',
        'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612bc0-2c8f-11ee-0a80-11e40013a427',
                                                                                               'name': 'Марка, модель',
                                                                                               'type': 'text',
                                                                                               'value': 'amtel nord master ST'},
                                                              {'meta': {
                                                                  'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612c6c-2c8f-11ee-0a80-11e40013a428',
                                                                  'type': 'attributemetadata',
                                                                  'mediaType': 'application/json'},
                                                               'id': 'dd612c6c-2c8f-11ee-0a80-11e40013a428',
                                                               'name': 'Сезон', 'type': 'text', 'value': 'Зима Шипы'}, {
                                                                  'meta': {
                                                                      'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612d24-2c8f-11ee-0a80-11e40013a429',
                                                                      'type': 'attributemetadata',
                                                                      'mediaType': 'application/json'},
                                                                  'id': 'dd612d24-2c8f-11ee-0a80-11e40013a429',
                                                                  'name': 'Параметры шин', 'type': 'text',
                                                                  'value': '175/70 R13'}, {'meta': {
            'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612dc7-2c8f-11ee-0a80-11e40013a42a',
            'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612dc7-2c8f-11ee-0a80-11e40013a42a',
                                                                                           'name': 'Параметры дисков',
                                                                                           'type': 'text',
                                                                                           'value': '4х98'}, {'meta': {
            'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612ea4-2c8f-11ee-0a80-11e40013a42b',
            'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612ea4-2c8f-11ee-0a80-11e40013a42b',
                                                                                                              'name': 'Состояние',
                                                                                                              'type': 'text',
                                                                                                              'value': 'Нормальное'},
                                                              {'meta': {
                                                                  'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612f4f-2c8f-11ee-0a80-11e40013a42c',
                                                                  'type': 'attributemetadata',
                                                                  'mediaType': 'application/json'},
                                                               'id': 'dd612f4f-2c8f-11ee-0a80-11e40013a42c',
                                                               'name': 'Статус', 'type': 'text', 'value': 'Принят'}, {
                                                                  'meta': {
                                                                      'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/77397075-6830-11ee-0a80-1196001195c2',
                                                                      'type': 'attributemetadata',
                                                                      'mediaType': 'application/json'},
                                                                  'id': '77397075-6830-11ee-0a80-1196001195c2',
                                                                  'name': 'Склад', 'type': 'string',
                                                                  'value': 'Воронеж АО'}], 'paymentItemType': 'GOOD',
     'discountProhibited': False, 'weight': 0.0, 'volume': 0.0, 'variantsCount': 0, 'isSerialTrackable': False,
     'trackingType': 'NOT_TRACKED', 'files': {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/942935e3-816e-11ee-0a80-012500449568/files',
        'type': 'files', 'mediaType': 'application/json', 'size': 0, 'limit': 1000, 'offset': 0}}, 'stock': 0.0,
     'reserve': 0.0, 'inTransit': 0.0, 'quantity': 0.0}
