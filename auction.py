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
            name, model, code, storage, season, tires, disks, price, photo, status = self.db.get_lot(code)

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
            link = self.bot.export_chat_invite_link(
                chat_id=channel_id
            )

            await self.bot.send_message(
                chat_id=tg_id,
                text=f"Ссылка для входа на канал: {link}"
            )

    async def winner_text_handler(self, message, state):
        tg_id = message.from_user.id
        text = message.text
        username = message.from_user.username
        tg_id = message.from_user.id
        admins = self.db.get_admins()
        blocked_users = self.db.get_blocked_users()
        id_and_codes = self.db.get_id_and_codes()
        if tg_id in blocked_users and text.lower() != "обжаловать":
            await self.bot.send_message(
                chat_id=tg_id,
                text="К сожалению вы заблокированы"
            )

        elif tg_id in id_and_codes:
            if text.lower() == "хорошо, жду":
                code = id_and_codes[tg_id]
                lot_id, lot_text, lot_price = self.db.get_selling_lot(code)
                phone, fullname = self.db.user_by_id(tg_id=tg_id)
                self.db.add_ransom(tg_id=tg_id, phone=phone, fullname=fullname, code=code, ransom=lot_price)
                self.db.update_status_sell(code)
                self.db.delete_now_lots(id_and_codes[tg_id])
                self.db.delete_id_and_codes(tg_id=tg_id, code=id_and_codes[tg_id])
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

                user_bids = self.db.get_bids_by_tg_id_and_code(tg_id=tg_id,
                                                               code=id_and_codes[tg_id])
                best_bid = max(user_bids, key=lambda x: x[1])
                await self.bot.send_message(
                    chat_id=admin_group,
                    text=f"Победитель аукциона по лоту №{code}\n"
                         f"Имя: {fullname}\n"
                         f"Тг: {username}\n"
                         f"Телефон: +{phone}\n"
                         f"Итоговая цена: {best_bid[0]}"
                )

                self.db.delete_id_and_codes(tg_id, id_and_codes[tg_id])

            elif text.lower() == "передумал":
                phone, fullname = self.db.user_by_id(tg_id=tg_id)
                places = self.db.get_places_ids(code=id_and_codes[tg_id])
                this_place = places[tg_id]
                # self.db.delete_id_and_codes(tg_id, id_and_codes[tg_id])
                if this_place in [1, 2]:
                    next_place = self.db.get_tg_id_by_place(code=id_and_codes[tg_id], place=this_place + 1)
                    # print(f"{next_place}, {this_place}, {admins}")
                    if next_place is None or next_place[0] in admins:
                        if next_place is not None and next_place[0] in admins and this_place == 1:
                            next_place = self.db.get_tg_id_by_place(code=id_and_codes[tg_id], place=3)

                        if next_place is None:
                            await self.bot.send_message(
                                chat_id=admin_group,
                                text=f"Лот №{id_and_codes[tg_id]} не был никем выкуплен и будет выставлен позже"
                            )
                            self.db.delete_bids(id_and_codes[tg_id])
                            self.db.delete_places(id_and_codes[tg_id])
                            self.db.delete_saved_chats(id_and_codes[tg_id])
                            repetition_count = self.db.get_repetition(id_and_codes[tg_id])

                            if repetition_count is None:
                                self.db.update_status_stock(id_and_codes[tg_id])
                                self.db.add_re_lot(id_and_codes[tg_id])
                            elif repetition_count in [1, 2]:
                                self.db.update_status_stock(id_and_codes[tg_id])
                                self.db.update_repetition(id_and_codes[tg_id])
                            elif repetition_count == 3:
                                self.db.update_status_deleted(id_and_codes[tg_id])
                                await self.bot.send_message(
                                    chat_id=admin_group,
                                    text=f"Лот №{id_and_codes[tg_id]} удалён, так как никто не выкупил его в течении 3 дней."
                                )
                            self.db.delete_now_lots(id_and_codes[tg_id])

                        elif next_place is not None:
                            user_bids = self.db.get_bids_by_tg_id_and_code(tg_id=next_place[0],
                                                                           code=id_and_codes[tg_id])
                            best_bid = max(user_bids, key=lambda x: x[1])

                            # first_place = list(best_bid[0])
                            # first_place[-1] = "*"
                            # first_place[-2] = "*"
                            # first_place = "".join(first_place)
                            #
                            # lot_id, lot_text, lot_price = self.db.get_selling_lot(id_and_codes[tg_id])
                            await self.bot.send_message(
                                chat_id=next_place[0],
                                text=f"Прошлый победитель отказался выкупать лот.\n"
                                     f"Поздравляем! Ваша ставка сыграла. ЛОТ №{id_and_codes[tg_id]} продан вам за {best_bid[1]} руб."
                                     "В ближайшее время с Вами свяжется Менеджер Аукциона и согласует условия оплаты, время и место, "
                                     "где Вы сможете забрать выигранный лот. "
                                     "Также Вы сможете обсудить условия доставки. Благодарим Вас за участие в Аукционе FRESH",
                                reply_markup=winner_markup
                            )
                            await auc_bot.get_code(tg_id=next_place[0], code=id_and_codes[tg_id])

                    else:
                        user_bids = self.db.get_bids_by_tg_id_and_code(tg_id=next_place[0], code=id_and_codes[tg_id])
                        # print(user_bids, next_place[0])
                        best_bid = max(user_bids, key=lambda x: x[1])

                        first_place = list(best_bid[0])
                        first_place[-1] = "*"
                        first_place[-2] = "*"
                        first_place = "".join(first_place)

                        lot_id, lot_text, lot_price = self.db.get_selling_lot(id_and_codes[tg_id])
                        await self.bot.send_message(
                            chat_id=next_place[0],
                            text=f"Прошлый победитель отказался выкупать лот.\n"
                                 f"Поздравляем! Ваша ставка сыграла. ЛОТ №{id_and_codes[tg_id]} продан вам за {best_bid[1]} руб."
                                 "В ближайшее время с Вами свяжется Менеджер Аукциона и согласует условия оплаты, время и место, "
                                 "где Вы сможете забрать выигранный лот. "
                                 "Также Вы сможете обсудить условия доставки. Благодарим Вас за участие в Аукционе FRESH",
                            reply_markup=winner_markup
                        )
                        await auc_bot.get_code(tg_id=next_place[0], code=id_and_codes[tg_id])

                await self.bot.send_message(
                    chat_id=tg_id,
                    text=decline,
                    reply_markup=appeal
                )
                self.db.block_user(tg_id=tg_id)
                self.db.add_refusial(tg_id=tg_id, phone=phone, fullname=fullname, code=id_and_codes[tg_id])
                # self.db.delete_id_and_codes(tg_id, id_and_codes[tg_id])

            elif text.lower() == "обжаловать":
                code = id_and_codes[tg_id]
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



    async def get_code(self, tg_id, code):
        self.codes[tg_id] = code

    def register_handlers(self):
        self.dp.register_message_handler(callback=admin_handler, commands=["admin"], state="*")
        self.dp.register_message_handler(callback=self.start_handler, commands=["start"], state="*")
        self.dp.register_message_handler(callback=self.get_rules, commands=["rules"], state="*")
        self.dp.register_message_handler(callback=add_partner_handler, state=AdminStates.add_partner,
                                         content_types=["text", "contact"])

        self.dp.register_message_handler(callback=add_admin_handler, state=AdminStates.add_admin,
                                         content_types=["text", "contact"])
        self.dp.register_message_handler(callback=delete_partner_handler, state=AdminStates.delete_partner,
                                         content_types=["text", "contact"])
        self.dp.register_message_handler(callback=delete_admin_handler, state=AdminStates.delete_admin,
                                         content_types=["text", "contact"])
        self.dp.register_message_handler(callback=get_contact_handler, content_types=ContentTypes.CONTACT, state=RegistrationStates.phone)
        self.dp.register_message_handler(callback=get_email_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.email)
        self.dp.register_message_handler(callback=get_fullname_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.fullname)
        self.dp.register_message_handler(callback=get_gender_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.gender)
        self.dp.register_message_handler(callback=get_age_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.age)
        self.dp.register_message_handler(callback=get_avatar_handler, content_types=ContentTypes.ANY, state=RegistrationStates.avatar)
        self.dp.register_callback_query_handler(callback=get_region_handler, state=RegistrationStates.region)
        self.dp.register_message_handler(callback=get_company_handler, content_types=ContentTypes.TEXT, state=RegistrationStates.company)
        self.dp.register_message_handler(callback=self.winner_text_handler, content_types=["text"], state="*")



        # self.dp.register_message_handler(callback=self.text_handler, content_types=ContentTypes.ANY, state="*")

        self.dp.register_callback_query_handler(callback=admin_callback_handler, state="*")


        # self.dp.register_callback_query_handler(callback=auc_callback, state="*")

    def run(self):
        self.register_handlers()
        executor.start_polling(dispatcher=self.dp, skip_updates=True)


auc_bot = AucBot(token=token, db_name=db_name)
if __name__ == "__main__":
    auc_bot.run()