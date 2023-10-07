from aiogram import Bot
from db_api.database import Database
from config import token, db_name


def get_bot_and_db():
    bot = Bot(token)
    db = Database(db_name)

    return bot, db