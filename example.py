from requests import request
from get_bot_and_db import get_bot_and_db
import datetime
bot, db = get_bot_and_db()
access_token = "80e9d6f8d66283f2d16b974666020bf46ae83d7a"

offset = datetime.timedelta(hours=3)
datetime.timezone(offset, name='МСК')
print(datetime.datetime.now().weekday())