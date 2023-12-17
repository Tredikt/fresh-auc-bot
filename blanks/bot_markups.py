from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# удаление ReplyKeyboard
remove_markup = ReplyKeyboardRemove()

# регистрация
get_contact_markup = ReplyKeyboardMarkup(resize_keyboard=True)
get_contact_markup.add(
    KeyboardButton(text="Отправить номер телефона 📱", request_contact=True)
)

# гендер
gender_markup = ReplyKeyboardMarkup(resize_keyboard=True)
gender_markup.add("Мужчина", "Женщина")
gender_markup.add("Пропустить")

# компания
company_markup = ReplyKeyboardMarkup(resize_keyboard=True)
company_markup.add("Я не работаю в компании")


# регионы
with open("regions.txt", "r", encoding="UTF-8") as file:
    regions_list = file.read().split("\n")

    markups_regions_list = []
    markup = InlineKeyboardMarkup()
    count = 1
    markup_count = 0
    for elem in regions_list:
        try:
            code, region = elem.split("@")
        except Exception:
            pass
        if count == 10:
            if markup_count == 0:
                markup.add(
                    InlineKeyboardButton(text="⏩", callback_data="next_page1")
                )

            elif markup_count == 8:
                markup.add(
                    InlineKeyboardButton(text="⏪", callback_data="prev_page7")
                )

            else:
                markup.add(
                    InlineKeyboardButton(text="⏪", callback_data=f"prev_page{markup_count - 1}"),
                    InlineKeyboardButton(text="⏩", callback_data=f"next_page{markup_count + 1}"),
                )

            markups_regions_list.append(markup)
            markup = InlineKeyboardMarkup()
            count = 0
            markup_count += 1

        markup.add(
            InlineKeyboardButton(text=region, callback_data=code)
        )
        count += 1



# админы
admin_markup = InlineKeyboardMarkup()
(admin_markup.add(
    InlineKeyboardButton(
        text="Выгрузить лоты",
        callback_data="upload_lots"
    )
).add(
    InlineKeyboardButton(
        text="Добавить лоты на аукцион",
        callback_data="add_lots_for_auc"
    )
).add(
    InlineKeyboardButton(
        text="Удалить лот из базы",
        callback_data="delete_lot_admin"
    )
).add(
    InlineKeyboardButton(
        text="Изменить цену лота",
        callback_data="edit_lot_price"
    )
).add(
    InlineKeyboardButton(
        text="Изменить цену на превью",
        callback_data="edit_lot_price_preview"
    )
).add(
    InlineKeyboardButton(
        text="Изменить время",
        callback_data="time_markup"
    )
).add(
    InlineKeyboardButton(
        text="Добавить партнёра",
        callback_data="add_partner"
    )
).add(
    InlineKeyboardButton(
        text="Добавить админа",
        callback_data="add_admin"
    )
).add(
    InlineKeyboardButton(
        text="Удалить партнёра",
        callback_data="delete_partner"
    )
).add(
    InlineKeyboardButton(
        text="Удалить админа",
        callback_data="delete_admin"
    )
).add(
    InlineKeyboardButton(
        text="О пользователях",
        callback_data="statistics_users"
    )
).add(
    InlineKeyboardButton(
        text="О лотах",
        callback_data="statistics_lots"
    )
).add(
    InlineKeyboardButton(
        text="О торгах",
        callback_data="statistics_auction"
    )
))

time_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        text="Изменить публикацию лотов",
        callback_data="edit_time_1"
    )
).add(
    InlineKeyboardButton(
        text="Изменить напоминание о начале",
        callback_data="edit_time_2"
    )
).add(
    InlineKeyboardButton(
        text="Изменить начало аукциона",
        callback_data="edit_time_3"
    )
).add(
    InlineKeyboardButton(
        text="Изменить напоминание о конце",
        callback_data="edit_time_4"
    )
).add(
    InlineKeyboardButton(
        text="Изменить конец аукциона",
        callback_data="edit_time_5"
    )
).add(
    InlineKeyboardButton(
        text="Назад",
        callback_data="admin_back"
    )
)

admin_back = InlineKeyboardMarkup()
admin_back.add(InlineKeyboardButton(
    text="Назад", callback_data="admin_back"
))


winner_markup = ReplyKeyboardMarkup(resize_keyboard=True).add("Хорошо, жду").add("Передумал")

appeal = ReplyKeyboardMarkup(resize_keyboard=True).add("Обжаловать")