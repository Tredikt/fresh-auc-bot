from get_bot_and_db import get_bot_and_db
from datetime import datetime


async def auc_callback(call, state):
    chat = call.message.chat.id
    m_id = call.message.message_id
    bot, db = get_bot_and_db()
    callback = call.data
    tg_id = call.message["from"].id
    blocked_users = db.get_blocked_users()
    if tg_id in blocked_users:
        await bot.send_message(
            chat_id=tg_id,
            text="К сожалению вы заблокированы"
        )

    elif callback == "warning":
        print("aboba")
        await call.answer(text="Если победитель откажется от лота, он передается следующему участнику")

    elif callback[:4] == "time":
        code = int(callback.split("_")[1])
        minutes, hours = db.get_start_lot_time(code)
        now_minutes = datetime.now().minute
        now_hours = datetime.now().hour

        time = (now_hours * 60 + now_minutes) - (hours * 60 + minutes)
        await call.answer(text=f"До конца аукциона {time} минут")

