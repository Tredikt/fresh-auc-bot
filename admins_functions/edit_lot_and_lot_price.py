from get_bot_and_db import get_bot_and_db
from config import channel_id


async def edit_lot_and_lot_price(code, new_price):
    bot, db = get_bot_and_db()
    name, model, code, storage, season, tires, disks, price, photo, status = db.get_lot(code)
    lot_id, lot_text, lot_price = db.get_selling_lot(code)
    new_lot_text = lot_text.replace(str(price), str(new_price))

    db.update_now_lot_price_and_text(new_lot_price=new_lot_text, new_lot_text=new_lot_text, code=code)

    await bot.edit_message_caption(
        chat_id=channel_id,
        message_id=lot_id,
        caption=new_lot_text
    )