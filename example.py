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

for data in response.json()["rows"]:
    try:
        name = data["name"]

        if name[:4] != "Тест" and "code" in data.keys():
            code = data["code"]
            attributes = data["attributes"]
            price = data.get("salePrices")
            if price is not None:
              price = price[0]["value"]

            wheels_or_tires = attributes[0]["value"]
            if wheels_or_tires in ["Колеса", "Колёса"]:
                brand_model = attributes[1]["value"]
                season = attributes[2]["value"]
                tire_parameters = attributes[3]["value"]
                disk_parameters = attributes[4]["value"]
                status = attributes[5]["value"]
                if status in ["Отличное", "Плохое", "Среднее", "Хорошее"]:
                    status = attributes[6]["value"]
                photo_url = data["images"]["meta"]["href"]
                photo_download = request("GET", photo_url,
                                         headers={"Authorization": f"Bearer {access_token}"}).json()
                # print(photo_download["rows"])
                if len(photo_download["rows"]) > 0:
                    photo = request("GET", photo_download["rows"][0]["meta"]["downloadHref"],
                                    headers={"Authorization": f"Bearer {access_token}"}).content
                    if status == "Принят" and price is not None and price > 0 and str(code) not in codes:
                        db.add_lot(
                            name=name,
                            code=code,
                            model=brand_model,
                            season=season,
                            tires=tire_parameters,
                            disks=disk_parameters,
                            price=price // 100,
                            photo=photo
                        )
                        print(
                            f"{name = } {code =} {wheels_or_tires =} {brand_model = } {season =} {tire_parameters =} {status =}")

            elif wheels_or_tires in ["Шины", "Шина"]:
                brand_model = attributes[1]["value"]
                season = attributes[2]["value"]
                tire_parameters = attributes[3]["value"]
                status = attributes[4]["value"]
                if status in ["Отличное", "Плохое", "Среднее", "Хорошее"]:
                    status = attributes[5]["value"]

                photo_url = data["images"]["meta"]["href"]
                photo_download = request("GET", photo_url,
                                         headers={
                                             "Authorization": f"Bearer {access_token}"}).json()
                # print(photo_download["rows"])
                if len(photo_download["rows"]) > 0:
                    photo = request("GET", photo_download["rows"][0]["meta"]["downloadHref"],
                                    headers={"Authorization": f"Bearer {access_token}"}).content

                    if status == "Принят" and price is not None and price > 0 and str(code) not in codes:
                        db.add_lot(
                            name=name,
                            code=code,
                            model=brand_model,
                            season=season,
                            tires=tire_parameters,
                            disks=None,
                            price=price // 100,
                            photo=photo
                        )

        #                 print(
        #                     f"{name = } {code =} {wheels_or_tires =} {brand_model = } {season =} {tire_parameters =} {status =}")
    except Exception as e:
        print(e, data.keys(), sep="\n")
        print("\n\n")

