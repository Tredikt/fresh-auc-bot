from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentTypes, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from db_api.database import Database
from config import token, db_name, admin_group, channel_id

from blanks.bot_texts import start_text, auction_rules
from blanks.bot_markups import get_contact_markup, appeal, winner_markup
from blanks.bot_texts import decline

from states_handlers.bot_states import RegistrationStates, AdminStates, AuctionStates
from states_handlers.get_contact_handler import get_contact_handler
from states_handlers.get_email_handler import get_email_handler
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
from admins_functions.delete_lot_handler import delete_lot_handler
from admins_functions.edit_lot_code_handler import edit_lot_code_handler
from admins_functions.edit_lot_price_handler import edit_lot_price_handler
from admins_functions.add_lots_for_auc_handler import add_lots_for_auc_handler
from admins_functions.edit_time_handler import edit_time_handler

from requests import request
import logging
from datetime import datetime
logging.basicConfig(level="INFO")


class AucBot:
    def __init__(self, token, db_name):
        self.bot = Bot(token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.db = Database(db_name)
        self.codes = dict()

    async def start_handler(self, message, state):

        await state.finish()
        chat_id = message.chat.id
        tg_id = message.from_user.id
        blocked_users = self.db.get_blocked_users()
        admins = self.db.get_admins()

        text = message.text
        print(message)
        if text[7:17] == "raiseprice":
            code = text.split("_")[1]
            await self.bot.send_message(
                chat_id=tg_id,
                text="Вы уверены, что хотите повысить ставку?",
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text="Да", callback_data=f"confirm_{code}")
                ).add(InlineKeyboardButton(
                    text="Нет", callback_data=f"decline_{code}"
                ))
            )

        elif text[7:11] == "save":
            code = text.split("_")[1]
            lot_id, lot_text, lot_price = self.db.get_selling_lot(code)
            name, model, code, storage, season, tires, disks, price, photo, status, google_disk, stage = self.db.get_lot(code)

            try:
                if int(tires[-2:]) >= 18:
                    auc_price = "+ 500р."
                else:
                    auc_price = "+ 250р."
            except ValueError:
                auc_price = "+ 250р."

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(
                    text=auc_price, callback_data=f"raiseprice_{code}"
                )
            ).add(
                InlineKeyboardButton(
                    text="⏳", callback_data=f"time_{code}"
                ),
                InlineKeyboardButton(
                    text="⚠️", callback_data="warning"
                )
            )

            if tg_id in admins:
                markup.add(
                    InlineKeyboardButton(text="❌", callback_data=f"deletelot_{code}")
                )

            saved_lot = await self.bot.copy_message(
                chat_id=tg_id,
                from_chat_id=channel_id,
                message_id=lot_id,
                reply_markup=markup
            )
            self.db.save_lot(lot_id=saved_lot.message_id, chat_id=tg_id, code=code)

        else:
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
    async def get_rules(self, message, state):
        await state.finish()
        tg_id = message.from_user.id

        await self.bot.send_message(
            chat_id=tg_id,
            text=auction_rules,
            parse_mode="html"
        )

    async def get_link(self, message, state):
        await state.finish()
        admins = self.db.get_admins()
        tg_id = message.from_user.id

        if tg_id in admins:
            link = await self.bot.export_chat_invite_link(
                chat_id=channel_id
            )
            await self.bot.send_message(
                chat_id=tg_id,
                text=f"Ссылка для входа на канал: {link}"
            )

    async def winner_text_handler(self, message, state):
        print(message)
        chat_id = message.chat.id
        text = message.text
        username = message.from_user.username
        tg_id = message.from_user.id
        admins = self.db.get_admins()
        blocked_users = self.db.get_blocked_users()

        if chat_id == -1002127006977:
            if tg_id not in admins:
                await self.bot.delete_message(
                    chat_id=chat_id,
                    message_id=message.message_id
                )

    async def get_code(self, tg_id, code):
        self.codes[tg_id] = code

    def register_handlers(self):
        self.dp.register_message_handler(callback=admin_handler, commands=["admin"], state="*")
        self.dp.register_message_handler(callback=self.start_handler, commands=["start"], state="*")
        self.dp.register_message_handler(callback=self.get_rules, commands=["rules"], state="*")
        self.dp.register_message_handler(callback=self.get_link, commands=["get_link"], state="*")
        self.dp.register_message_handler(callback=add_lots_for_auc_handler, state=AdminStates.add_lots_for_auc, content_types=["text"])
        self.dp.register_message_handler(callback=edit_time_handler, state=AdminStates.edit_time, content_types=["text"])
        self.dp.register_message_handler(callback=add_partner_handler, state=AdminStates.add_partner,
                                         content_types=["text", "contact"])

        self.dp.register_message_handler(callback=add_admin_handler, state=AdminStates.add_admin,
                                         content_types=["text", "contact"])
        self.dp.register_message_handler(callback=delete_partner_handler, state=AdminStates.delete_partner,
                                         content_types=["text", "contact"])
        self.dp.register_message_handler(callback=delete_admin_handler, state=AdminStates.delete_admin,
                                         content_types=["text", "contact"]),
        self.dp.register_message_handler(callback=delete_lot_handler, state=AdminStates.delete_lot,
                                         content_types=["text"])
        self.dp.register_message_handler(callback=get_contact_handler, content_types=ContentTypes.CONTACT, state=RegistrationStates.phone)
        self.dp.register_message_handler(callback=get_email_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.email)
        self.dp.register_message_handler(callback=get_fullname_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.fullname)
        self.dp.register_message_handler(callback=get_gender_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.gender)
        self.dp.register_message_handler(callback=get_age_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.age)
        self.dp.register_message_handler(callback=get_avatar_handler, content_types=ContentTypes.ANY, state=RegistrationStates.avatar)
        self.dp.register_callback_query_handler(callback=get_region_handler, state=RegistrationStates.region)
        self.dp.register_message_handler(callback=get_company_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.company)
        self.dp.register_message_handler(callback=edit_lot_code_handler, content_types=ContentTypes.TEXT,
                                         state=AdminStates.edit_lot_code)
        self.dp.register_message_handler(callback=edit_lot_price_handler, content_types=ContentTypes.TEXT,
                                         state=AdminStates.edit_lot_price)
        self.dp.register_message_handler(callback=self.winner_text_handler, content_types=["video"], state="*")
        self.dp.register_callback_query_handler(callback=admin_callback_handler, state="*")

    def run(self):
        self.register_handlers()
        executor.start_polling(dispatcher=self.dp, skip_updates=True)


auc_bot = AucBot(token=token, db_name=db_name)
if __name__ == "__main__":
    auc_bot.run()