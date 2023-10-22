from requests import request
from get_bot_and_db import get_bot_and_db

bot, db = get_bot_and_db()
access_token = "80e9d6f8d66283f2d16b974666020bf46ae83d7a"

response = request(
    "GET",
    "https://api.moysklad.ru/api/remap/1.2/entity/assortment",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept-Encoding": "gzip"
    }
)

codes = db.get_all_codes()
l = []

dd, g = l

# for data in response.json()["rows"]:
#     print(data)
#     try:
#         name = data["name"]
#
#         if name[:4] != "Тест" and "code" in data.keys():
#             code = data["code"]
#             attributes = data["attributes"]
#             price = data.get("salePrices")
#             if price is not None:
#                 price = price[0]["value"]
#
#             wheels_or_tires = attributes[0]["value"]
#             if wheels_or_tires in ["Колеса", "Колёса"]:
#                 brand_model = attributes[1]["value"]
#                 season = attributes[2]["value"]
#                 tire_parameters = attributes[3]["value"]
#                 disk_parameters = attributes[4]["value"]
#                 status = attributes[5]["value"]
#                 if status in ["Отличное", "Плохое", "Среднее", "Хорошее"]:
#                     status = attributes[6]["value"]
#                 storage = None
#                 for num in range(5, 9):
#                     if attributes[num]["name"] == "Склад":
#                         storage = attributes[num]["value"]
#                         break
#                 photo_url = data["images"]["meta"]["href"]
#                 photo_download = request("GET", photo_url,
#                                          headers={"Authorization": f"Bearer {access_token}"}).json()
#                 # print(photo_download["rows"])
#                 if len(photo_download["rows"]) > 0:
#                     photo = request("GET", photo_download["rows"][0]["meta"]["downloadHref"],
#                                     headers={"Authorization": f"Bearer {access_token}"}).content
#                     if status == "Принят" and price is not None and price > 0 and str(code) not in codes and storage is not None:
#                         db.add_lot(
#                             name=name,
#                             code=code,
#                             model=brand_model,
#                             season=season,
#                             storage=storage,
#                             tires=tire_parameters,
#                             disks=disk_parameters,
#                             price=price // 100,
#                             photo=photo
#                         )
#                         print(
#                             f"{name = } {code =} {wheels_or_tires =} {brand_model = } {season =} {tire_parameters =} {status =}")
#
#             elif wheels_or_tires in ["Шины", "Шина"]:
#                 brand_model = attributes[1]["value"]
#                 season = attributes[2]["value"]
#                 tire_parameters = attributes[3]["value"]
#                 status = attributes[4]["value"]
#                 if status in ["Отличное", "Плохое", "Среднее", "Хорошее"]:
#                     status = attributes[5]["value"]
#                 place = None
#                 for num in range(5, 9):
#                     if attributes[num]["name"] == "Склад":
#                         place = attributes[num]["value"]
#                         break
#                 photo_url = data["images"]["meta"]["href"]
#                 photo_download = request("GET", photo_url,
#                                          headers={
#                                              "Authorization": f"Bearer {access_token}"}).json()
#                 # print(photo_download["rows"])
#                 if len(photo_download["rows"]) > 0:
#                     photo = request("GET", photo_download["rows"][0]["meta"]["downloadHref"],
#                                     headers={"Authorization": f"Bearer {access_token}"}).content
#
#                     if status == "Принят" and price is not None and price > 0 and str(code) not in codes and storage is not None:
#                         db.add_lot(
#                             name=name,
#                             code=code,
#                             model=brand_model,
#                             season=season,
#                             storage=storage,
#                             tires=tire_parameters,
#                             disks=None,
#                             price=price // 100,
#                             photo=photo
#                         )
#
#         #                 print(
#         #                     f"{name = } {code =} {wheels_or_tires =} {brand_model = } {season =} {tire_parameters =} {status =}")
#     except Exception as e:
#         print(e, data.keys(), sep="\n")
#         print("\n\n")

tire = {'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/f2d74b89-2d4f-11ee-0a80-03120008f578',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata', 'type': 'product',
                 'mediaType': 'application/json',
                 'uuidHref': 'https://online.moysklad.ru/app/#good/edit?id=f2d73b4a-2d4f-11ee-0a80-03120008f570'},
        'id': 'f2d74b89-2d4f-11ee-0a80-03120008f578', 'accountId': '0795996b-26dc-11ee-0a80-03cd000037cb', 'owner': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/employee/07d72c88-26dc-11ee-0a80-0d350007b48b',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/employee/metadata', 'type': 'employee',
                 'mediaType': 'application/json',
                 'uuidHref': 'https://online.moysklad.ru/app/#employee/edit?id=07d72c88-26dc-11ee-0a80-0d350007b48b'}},
        'shared': True, 'group': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/group/7218334b-2c97-11ee-0a80-0b2d00146089',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/group/metadata', 'type': 'group',
                 'mediaType': 'application/json'}}, 'updated': '2023-10-17 05:35:19.843', 'name': '032470_Резина',
        'code': '032470', 'externalCode': '032470', 'archived': False, 'pathName': '', 'useParentVat': True, 'uom': {
        'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/uom/991c77c7-2c90-11ee-0a80-0302000ba4a7',
                 'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/uom/metadata', 'type': 'uom',
                 'mediaType': 'application/json'}}, 'images': {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/f2d74b89-2d4f-11ee-0a80-03120008f578/images',
        'type': 'image', 'mediaType': 'application/json', 'size': 10, 'limit': 1000, 'offset': 0}},
        'minPrice': {'value': 0.0, 'currency': {'meta': {
            'href': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/07eaaf5d-26dc-11ee-0a80-0d350007b4d5',
            'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/metadata', 'type': 'currency',
            'mediaType': 'application/json',
            'uuidHref': 'https://online.moysklad.ru/app/#currency/edit?id=07eaaf5d-26dc-11ee-0a80-0d350007b4d5'}}},
        'salePrices': [{'value': 300000.0, 'currency': {'meta': {
            'href': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/07eaaf5d-26dc-11ee-0a80-0d350007b4d5',
            'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/metadata', 'type': 'currency',
            'mediaType': 'application/json',
            'uuidHref': 'https://online.moysklad.ru/app/#currency/edit?id=07eaaf5d-26dc-11ee-0a80-0d350007b4d5'}},
                        'priceType': {'meta': {
                            'href': 'https://api.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/07eaf3c8-26dc-11ee-0a80-0d350007b4d6',
                            'type': 'pricetype', 'mediaType': 'application/json'},
                                      'id': '07eaf3c8-26dc-11ee-0a80-0d350007b4d6', 'name': 'Цена продажи',
                                      'externalCode': 'cbcf493b-55bc-11d9-848a-00112f43529a'}}],
        'buyPrice': {'value': 0.0, 'currency': {'meta': {
            'href': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/07eaaf5d-26dc-11ee-0a80-0d350007b4d5',
            'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/currency/metadata', 'type': 'currency',
            'mediaType': 'application/json',
            'uuidHref': 'https://online.moysklad.ru/app/#currency/edit?id=07eaaf5d-26dc-11ee-0a80-0d350007b4d5'}}},
        'barcodes': [{'ean13': '2000000000411'}], 'attributes': [{'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612914-2c8f-11ee-0a80-11e40013a426',
        'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612914-2c8f-11ee-0a80-11e40013a426',
                                                                  'name': 'Предмет', 'type': 'text', 'value': 'Шины'}, {
                                                                     'meta': {
                                                                         'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612bc0-2c8f-11ee-0a80-11e40013a427',
                                                                         'type': 'attributemetadata',
                                                                         'mediaType': 'application/json'},
                                                                     'id': 'dd612bc0-2c8f-11ee-0a80-11e40013a427',
                                                                     'name': 'Марка, модель', 'type': 'text',
                                                                     'value': 'Pirelli P Zero'}, {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612c6c-2c8f-11ee-0a80-11e40013a428',
        'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612c6c-2c8f-11ee-0a80-11e40013a428',
                                                                                                  'name': 'Сезон',
                                                                                                  'type': 'text',
                                                                                                  'value': 'Лето'}, {
                                                                     'meta': {
                                                                         'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612d24-2c8f-11ee-0a80-11e40013a429',
                                                                         'type': 'attributemetadata',
                                                                         'mediaType': 'application/json'},
                                                                     'id': 'dd612d24-2c8f-11ee-0a80-11e40013a429',
                                                                     'name': 'Параметры шин', 'type': 'text',
                                                                     'value': '255\\35R18, 225\\40R18'}, {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612ea4-2c8f-11ee-0a80-11e40013a42b',
        'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': 'dd612ea4-2c8f-11ee-0a80-11e40013a42b',
                                                                                                          'name': 'Состояние',
                                                                                                          'type': 'text',
                                                                                                          'value': 'Отличное'},
                                                                 {'meta': {
                                                                     'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612f4f-2c8f-11ee-0a80-11e40013a42c',
                                                                     'type': 'attributemetadata',
                                                                     'mediaType': 'application/json'},
                                                                  'id': 'dd612f4f-2c8f-11ee-0a80-11e40013a42c',
                                                                  'name': 'Статус', 'type': 'text', 'value': 'Принят'},
                                                                 {'meta': {
                                                                     'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/dd612ff1-2c8f-11ee-0a80-11e40013a42d',
                                                                     'type': 'attributemetadata',
                                                                     'mediaType': 'application/json'},
                                                                  'id': 'dd612ff1-2c8f-11ee-0a80-11e40013a42d',
                                                                  'name': 'Цена торгов', 'type': 'long',
                                                                  'value': 15000}, {'meta': {
            'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/metadata/attributes/77397075-6830-11ee-0a80-1196001195c2',
            'type': 'attributemetadata', 'mediaType': 'application/json'}, 'id': '77397075-6830-11ee-0a80-1196001195c2',
                                                                                    'name': 'Склад', 'type': 'string',
                                                                                    'value': 'Воронеж АО'}],
        'paymentItemType': 'GOOD', 'discountProhibited': False, 'weight': 0.0, 'volume': 0.0, 'variantsCount': 0,
        'isSerialTrackable': False, 'trackingType': 'NOT_TRACKED', 'files': {'meta': {
        'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/f2d74b89-2d4f-11ee-0a80-03120008f578/files',
        'type': 'files', 'mediaType': 'application/json', 'size': 0, 'limit': 1000, 'offset': 0}}, 'stock': 0.0,
        'reserve': 0.0, 'inTransit': 0.0, 'quantity': 0.0}
