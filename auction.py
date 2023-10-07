from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentTypes, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from db_api.database import Database
from config import token, db_name, admin_group

from blanks.bot_texts import start_text
from blanks.bot_markups import get_contact_markup, appeal, winner_markup
from blanks.bot_texts import decline

from states_handlers.bot_states import RegistrationStates, AdminStates, AuctionStates
from states_handlers.get_contact_handler import get_contact_handler
from states_handlers.get_fullname_handler import get_fullname_handler
from states_handlers.get_gender_handler import get_gender_handler
from states_handlers.get_age_handler import get_age_handler
from states_handlers.get_avatar_handler import get_avatar_handler
from states_handlers.get_region_handler import get_region_handler
from states_handlers.get_company_handler import get_company_handler

from admins_functions.admin_handler import admin_handler
from admins_functions.admin_callback_handler import admin_callback_handler
from admins_functions.add_partner_handler import add_partner_handler
from admins_functions.add_admin_handler import add_admin_handler
from admins_functions.delete_admin_handler import delete_admin_handler
from admins_functions.delete_partner_handler import delete_partner_handler
from requests import request
import logging

logging.basicConfig(level="INFO")


class AucBot:
    def __init__(self, token, db_name):
        self.bot = Bot(token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.db = Database(db_name)
        self.codes = dict()

    async def start_handler(self, message, state):
        # await start_auction()
        await state.finish()
        tg_id = message.from_user.id
        blocked_users = self.db.get_blocked_users()
        if tg_id in blocked_users:
            await self.bot.send_message(
                chat_id=tg_id,
                text="К сожалению вы заблокированы"
            )

        else:
            chat = message.chat.id
            tg_id = message.from_user.id
            registered_users = self.db.get_registered_users()

            if tg_id in registered_users:
                await self.bot.send_message(
                    chat_id=chat,
                    text="Вы успешно зарегистрированы, вам доступен функционал",
                )

            else:
                await RegistrationStates.phone.set()
                await self.bot.send_message(
                    chat_id=chat,
                    text=start_text,
                    reply_markup=get_contact_markup
                )

    #{"message_id": 4, "from": {"id": 1283802964, "is_bot": false, "first_name": "Алексей", "last_name": "Смирнов", "username": "Tredikt", "language_code": "ru"}, "chat": {"id": -1001985774888, "title": "Шинный аукцион. Группа", "type": "supergroup"}, "date": 1694618860, "text": "."}

    async def winner_text_handler(self, message, state):
        tg_id = message.from_user.id
        text = message.text
        username = message.from_user.username

        if text.lower() == "Хорошо, жду":
            code = self.codes[tg_id]
            lot_id, lot_text, lot_price = self.db.get_selling_lot(code)
            phone, fullname = self.db.user_by_id(tg_id=tg_id)
            self.db.add_ransom(tg_id=tg_id, phone=phone, fullname=fullname, ransom=lot_price)
            self.db.update_status_sell(code)

            if username is None:
                if message.from_user.last_name is None:
                    username = message.from_user.first_name
                else:
                    username = f"{message.from_user.first_name} {message.from_user.last_name}"

            delete_markup = await self.bot.send_message(
                chat_id=tg_id,
                text="!",
                reply_markup=ReplyKeyboardRemove()
            )

            await self.bot.delete_message(
                chat_id=tg_id,
                message_id=delete_markup.message_id
            )
            await state.finish()

            await self.bot.send_message(
                chat_id=admin_group,
                text=f"Победитель аукциона по лоту №{code}\n"
                     f"Имя: {fullname}\n"
                     f"Тг: {username}\n"
                     f"Телефон: +{phone}\n"
                     f"Итоговая цена: {lot_price}"
            )

        elif text.lower() == "Передумал":
            phone, fullname = self.db.user_by_id(tg_id=tg_id)
            places = self.db.get_places_ids(code=self.codes[tg_id])
            this_place = places[tg_id]

            if this_place in [1, 2]:
                next_place = self.db.get_tg_id_by_place(code=self.codes[tg_id], place=this_place + 1)
                print(next_place)
                if next_place is None:
                    await self.bot.send_message(
                        chat_id=admin_group,
                        text=f"Лот №{self.codes[tg_id]} не был никем выкуплен и будет выставлен позже"
                    )
                else:
                    lot_id, lot_text, lot_price = self.db.get_selling_lot(self.codes[tg_id])
                    await self.bot.send_message(
                        chat_id=next_place[0],
                        text=f"Прошлый победитель отказался выкупать лот.\n"
                             f"Поздравляем! Ваша ставка сыграла. ЛОТ №{self.codes[tg_id]} продан вам за {lot_price} руб."
                             "В ближайшее время с Вами свяжется Менеджер Аукциона и согласует условия оплаты, время и место, "
                             "где Вы сможете забрать выигранный лот. "
                             "Также Вы сможете обсудить условия доставки. Благодарим Вас за участие в Аукционе FRESH",
                        reply_markup=winner_markup
                    )
                    await AuctionStates.winner.set()
                    await auc_bot.get_code(tg_id=next_place, code=self.codes[tg_id])

            await self.bot.send_message(
                chat_id=tg_id,
                text=decline,
                reply_markup=appeal
            )
            await self.db.block_user(tg_id=tg_id)
            self.db.add_refusial(tg_id=tg_id, phone=phone, fullname=fullname, code=self.codes[tg_id])
            del self.codes[tg_id]

        elif text.lower() == "Обжаловать":
            code = self.codes[tg_id]
            phone, fullname = self.db.user_by_id(tg_id=tg_id)
            await self.bot.send_message(
                chat_id=admin_group,
                text=f"Пользователь ({fullname} {phone}) отказывается выкупить выигранный лот "
                     f"№{code} по веским причинам и просит связаться с ним для уточнения обстоятельств",
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text="✅", callback_data=f"unlockuser_{tg_id}")
                ).add(InlineKeyboardButton(
                    text="⛔️", callback_data=f"blockuser_{tg_id}"
                ))
            )
            await self.bot.send_message(
                chat_id=tg_id,
                text="Ожидайте",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.finish()

    async def text_handler(self, message, state):
        print(message)
        # await self.bot.send_message(
        #     chat_id=1283802964,
        #     text=f"{message}"
        # )
        # print(message)
        tg_id = message.from_user.id
        blocked_users = self.db.get_blocked_users()
        if tg_id in blocked_users:
            await self.bot.send_message(
                chat_id=tg_id,
                text="К сожалению вы заблокированы"
            )
        chat = message.chat.id

        if chat == -1001985774888:
            text = message.text
            print(text)
            text_list = text.split("\n")
            print(text_list)
            name = text_list[1].split(":")[1].strip()
            model = text_list[2].split(":")[1].strip()
            code = text_list[3].split(":")[1].strip()
            season = text_list[4].split(":")[1].strip()
            tires = text_list[5].split(":")[1].strip()
            if "mp" in text_list[6].split(":")[1].strip():
                disks = text_list[6].split(":")[1].strip()
                price = text_list[7].split(":")[1].strip()
                photo = text_list[9].split(":", 1)[1].strip()
            else:
                disks = None
                price = text_list[6].split(":")[1].strip()
                photo = text_list[7].split(":", 1)[1].strip()

            response = request("GET", photo)
            print(response.json())
            if response.status_code == 200:
                with open(f"tires/photos_{code}.jpg", "wb") as file:
                    file.write(response.content)
            else:
                print(response.status_code, "status_code")
            print(name, model, code, season, tires, disks, price, photo)
            self.db.add_lot(name, model, code, season, tires, disks, price, photo)

    async def get_code(self, tg_id, code):
        self.codes[tg_id] = code

    def register_handlers(self):
        self.dp.register_message_handler(callback=add_partner_handler, state=AdminStates.add_partner,
                                         content_types=["text", "contact"])

        self.dp.register_message_handler(callback=add_admin_handler, state=AdminStates.add_admin,
                                         content_types=["text", "contact"])
        self.dp.register_message_handler(callback=delete_partner_handler, state=AdminStates.delete_partner,
                                         content_types=["text", "contact"])
        self.dp.register_message_handler(callback=delete_admin_handler, state=AdminStates.delete_admin,
                                         content_types=["text", "contact"])
        self.dp.register_message_handler(callback=self.winner_text_handler, content_types=["text"],
                                         state=AuctionStates.winner)
        self.dp.register_message_handler(callback=self.start_handler, commands=["start"], state="*")
        self.dp.register_message_handler(callback=get_contact_handler, content_types=ContentTypes.CONTACT, state=RegistrationStates.phone)
        self.dp.register_message_handler(callback=get_fullname_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.fullname)
        self.dp.register_message_handler(callback=get_gender_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.gender)
        self.dp.register_message_handler(callback=get_age_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.age)
        self.dp.register_message_handler(callback=get_avatar_handler, content_types=ContentTypes.ANY, state=RegistrationStates.avatar)
        self.dp.register_callback_query_handler(callback=get_region_handler, state=RegistrationStates.region)
        self.dp.register_message_handler(callback=get_company_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.company)

        self.dp.register_message_handler(callback=admin_handler, commands=["admin"], state="*")
        self.dp.register_message_handler(callback=self.text_handler, content_types=ContentTypes.ANY, state="*")

        self.dp.register_callback_query_handler(callback=admin_callback_handler, state="*")


        # self.dp.register_callback_query_handler(callback=auc_callback, state="*")

    def run(self):
        self.register_handlers()
        executor.start_polling(dispatcher=self.dp, skip_updates=True)


auc_bot = AucBot(token=token, db_name=db_name)
if __name__ == "__main__":
    auc_bot.run()