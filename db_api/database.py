from sqlite3 import connect


class Database:
    def __init__(self, name: str):
        self.conn = connect(name)
        self.cur = self.conn.cursor()

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                tg_id INTEGER,
                phone TEXT,
                email TEXT,
                fullname TEXT,
                gender TEXT,
                age INTEGER,
                avatar BLOB,
                region TEXT,
                company TEXT,
                blocked INTEGER
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS registration_passed(
                tg_id INTEGER
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS admins(
                tg_id INTEGER,
                phone TEXT
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS lots(
                name TEXT,
                model TEXT,
                code TEXT PRIMARY KEY,
                storage TEXT,
                season TEXT,
                tires TEXT,
                disks TEXT,
                price TEXT,
                photo BLOB,
                status TEXT,
                google_link TEXT,
                stage TEXT
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS re_lots(
                code TEXT,
                repetition INTEGER
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS now_lots(
                lot_id INTEGER,
                lot_text TEXT,
                lot_price INTEGER,
                code TEXT PRIMARY KEY
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bids(
                tg_id INTEGER,
                username TEXT,
                lot_price INTEGER,
                code TEXT
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS refusials(
                tg_id INTEGER,
                phone TEXT,
                fullname TEXT,
                code TEXT
            )
            """

        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_lots(
                lot_id INTEGER,
                chat_id INTEGER,
                code TEXT
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ransoms(
                tg_id INTEGER,
                phone TEXT,
                fullname TEXT,
                code TEXT,
                ransom INTEGER
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS places(
                tg_id INTEGER,
                code TEXT,
                place INTEGER
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS winners(
                tg_id INTEGER,
                phone TEXT,
                fullname TEXT,
                code TEXT
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders(
                message_id INTEGER,
                stage TEXT
            )
            """
        )

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS auction_time(
                time TEXT,
                number INTEGER PRIMARY KEY
            )
            """
        )

        self.conn.commit()

    def get_auction_time(self, index):
        start_auc = self.cur.execute(
            f"""
            SELECT time FROM auction_time
            WHERE number={index}
            """
        ).fetchone()

        return start_auc[0]

    def update_time_auction(self, time, index):
        self.cur.execute(
            f"""
            INSERT OR REPLACE INTO auction_time
            (time, number)
            VALUES
            (?, ?)
            """,
            (time, index)
        )
        self.conn.commit()


    def get_reminder_id(self, stage):
        message_id = self.cur.execute(
            f"""
            SELECT message_id FROM reminders
            WHERE stage='{stage}'
            """
        ).fetchone()

        if message_id is None:
            return None
        message_id = message_id[0]
        return message_id

    def delete_reminder_id(self, stage):
        self.cur.execute(
            f"""
            DELETE FROM reminders
            WHERE stage='{stage}'
            """
        )

    def add_reminders_id(self, message_id, stage):
        self.cur.execute(
            f"""
            INSERT OR REPLACE INTO reminders
            (message_id, stage)
            VALUES
            ({message_id}, '{stage}')
            """
        )

        self.conn.commit()

        self.conn.commit()

    def delete_bids(self, code):
        self.cur.execute(
            f"""
            DELETE FROM bids
            WHERE code='{code}';
            """
        )
        self.conn.commit()

    def delete_places(self, code):
        self.cur.execute(
            f"""
            DELETE FROM places
            WHERE code='{code}';
            """
        )
        self.conn.commit()

    def delete_saved_chats(self, code):
        self.cur.execute(
            f"""
            DELETE FROM saved_lots
            WHERE code='{code}';
            """
        )
        self.conn.commit()

    def get_photo_by_code(self, code):
        photo = self.cur.execute(
            f"""
            SELECT photo FROM lots
            WHERE code='{code}'
            """
        ).fetchone()

        if photo is None:
            return None
        return photo[0]

    def add_place(self, tg_id, code, place):
        self.cur.execute(
            f"""
            DELETE FROM places
            WHERE tg_id={tg_id}
            AND code='{code}'
            """
        )

        self.cur.execute(
            """
            INSERT INTO places
            (tg_id, code, place)
            VALUES
            (?, ?, ?)
            """,
            (tg_id, code, place)
        )
        self.conn.commit()

    def get_bids_by_tg_id_and_code(self, tg_id, code):
        bids = self.cur.execute(
            f"""
            SELECT username, lot_price FROM bids
            WHERE tg_id={tg_id}
            AND code='{code}'
            """
        ).fetchall()

        return bids

    def get_tg_id_by_place(self, code, place):
        info = self.cur.execute(
            f"""
            SELECT tg_id FROM places
            WHERE code='{code}'
            AND place={place}
            """
        ).fetchone()

        return info

    def get_places_ids(self, code):
        places_ids = self.cur.execute(
            f"""
            SELECT tg_id, place FROM places
            WHERE code='{code}'
            """
        ).fetchall()
        # print(places_ids, "places_ids")
        if places_ids is None:
            return {}
        places_dict = {elem[0]: elem[1] for elem in places_ids}
        return places_dict

    def add_refusial(self, tg_id, phone, fullname, code):
        self.cur.execute(
            """
            INSERT INTO refusials
            (tg_id, phone, fullname, code)
            VALUES
            (?, ?, ?, ?)
            """,
            (tg_id, phone, fullname, code)
        )
        self.conn.commit()

    def get_refusials(self, tg_id):
        refusials = self.cur.execute(
            f"""
            SELECT code FROM refusials
            WHERE tg_id={tg_id}
            """
        ).fetchall()

        if refusials is None:
            return []
        refusials = [elem[0] for elem in refusials]
        return refusials

    def get_last_price(self, code):
        last_price = self.cur.execute(
            f"""
            SELECT ransom FROM ransoms
            WHERE code='{code}'
            """
        ).fetchone()

        if last_price is None:
            return 0
        return last_price[0]

    def add_ransom(self, tg_id, phone, fullname, code, ransom):
        self.cur.execute(
            """
            INSERT INTO ransoms
            (tg_id, phone, fullname, code, ransom)
            VALUES
            (?, ?, ?, ?, ?)
            """,
            (tg_id, phone, fullname, code, ransom)
        )
        self.conn.commit()

    def get_ransom_price(self, tg_id):
        ransoms_prices = self.cur.execute(
            f"""
            SELECT ransom FROM ransoms
            WHERE tg_id={tg_id}
            """
        ).fetchall()
        self.conn.commit()

        if ransoms_prices is None:
            return []
        ransoms_prices = [elem[0] for elem in ransoms_prices]
        return ransoms_prices

    def get_ransom_codes(self):
        codes = self.cur.execute(
            """
            SELECT code FROM ransoms
            """
        ).fetchall()

        if codes is None:
            return []
        codes = [elem[0] for elem in codes]
        return codes

    def get_refusials_codes(self):
        codes = self.cur.execute(
            """
            SELECT code FROM refusials
            """
        ).fetchall()

        if codes is None:
            return []
        codes = [elem[0] for elem in codes]
        return codes

    def get_ransom_prices(self):
        prices = self.cur.execute(
            """
            SELECT ransom FROM ransoms
            """
        ).fetchall()

        if prices is None:
            return []
        prices = [elem[0] for elem in prices]
        return prices


    def add_winner(self, tg_id, phone, fullname, code):
        self.cur.execute(
            """
            INSERT INTO winners
            (tg_id, phone, fullname, code)
            VALUES
            (?, ?, ?, ?)
            """,
            (tg_id, phone, fullname, code)
        )
        self.conn.commit()

    def get_victory_count(self, tg_id):
        victories = self.cur.execute(
            f"""
            SELECT code FROM winners
            WHERE tg_id={tg_id}
            """
        ).fetchall()

        if victories is None:
            return []
        victories = [elem[0] for elem in victories]
        return victories

    def add_re_lot(self, code):
        self.cur.execute(
            """
            INSERT INTO re_lots
            (code, repetition)
            VALUES
            (?, ?)
            """,
            (code, 1)
        )

        self.conn.commit()

    def get_re_lot(self):
        codes = self.cur.execute(
            """
            SELECT code FROM re_lots
            WHERE repetition < 3
            """
        ).fetchall()

        if codes is None:
            return []
        codes = [elem[0] for elem in codes]
        return codes

    def update_repetition(self, code):
        self.cur.execute(
            f"""
            UPDATE re_lots
            SET repetition=repetition + 1
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def get_repetition(self, code):
        repetition_count = self.cur.execute(
            f"""
            SELECT repetition FROM re_lots
            WHERE code='{code}'
            """
        ).fetchone()
        self.conn.commit()

        if repetition_count is None:
            return None
        return repetition_count[0]

    def delete_lot(self, code):
        self.cur.execute(
            f"""
            DELETE FROM lots
            WHERE code='{code}'
            """
        )

        self.cur.execute(
            f"""
            DELETE FROM re_lots
            WHERE code='{code}'
            """
        )

        self.conn.commit()

    def delete_info_about_lot(self, code):
        db_names_list = ["lots", "re_lots", "bids", "saved_lots", "places"]

        for name in db_names_list:
            self.cur.execute(
                f"""
                DELETE FROM {name}
                WHERE code='{code}'
                """
            )
            self.conn.commit()

    def delete_now_lots(self, code):
        self.cur.execute(
            f"""
            DELETE FROM now_lots
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def get_bids_codes(self, tg_id):
        bids_codes = self.cur.execute(
            f"""
            SELECT code FROM bids
            WHERE tg_id={tg_id}
            """
        ).fetchall()

        if bids_codes is None:
            return []
        bids_codes = [elem[0] for elem in bids_codes]
        return bids_codes

    def get_bids_ids(self, code):
        bids_ids = self.cur.execute(
            f"""
            SELECT tg_id FROM bids
            WHERE code='{code}'
            """
        ).fetchall()

        if bids_ids is None:
            return []
        bids_ids = [elem[0] for elem in bids_ids]
        return bids_ids

    def get_all_bids_ids(self):
        ids = self.cur.execute(
            """
            SELECT tg_id FROM bids
            """
        ).fetchall()

        if ids is None:
            return []
        ids = [elem[0] for elem in ids]
        return ids

    def get_all_saved_lots_id(self):
        ids = self.cur.execute(
            """
            SELECT chat_id FROM saved_lots
            """
        ).fetchall()

        if ids is None:
            return []
        ids = [elem[0] for elem in ids]
        return ids

    def delete_relots(self, code):
        self.cur.execute(
            f"""
            DELETE FROM re_lots
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def get_bids(self):
        bids = self.cur.execute(
            """
            SELECT * FROM bids
            """
        ).fetchall()

        if bids is None:
            return []
        return bids


    def get_sold_lots_codes(self):
        codes = self.cur.execute(
            """
            SELECT code FROM lots
            WHERE status='sell'
            OR status='auction'
            """
        ).fetchall()

        if codes is None:
            return []
        codes = [elem[0] for elem in codes]
        return codes

    def get_saved_lots_codes(self, tg_id):
        saved_lots_codes = self.cur.execute(
            f"""
            SELECT code FROM saved_lots
            WHERE chat_id={tg_id}
            """
        ).fetchall()

        if saved_lots_codes is None:
            return []
        saved_lots_codes = [elem[0] for elem in saved_lots_codes]
        return saved_lots_codes

    def get_saved_lots_ids(self, code):
        get_saved_lots_ids = self.cur.execute(
            f"""
               SELECT chat_id FROM saved_lots
               WHERE code='{code}'
               """
        ).fetchall()

        if get_saved_lots_ids is None:
            return []
        get_saved_lots_ids = [elem[0] for elem in get_saved_lots_ids]
        return get_saved_lots_ids

    def update_winner(self, tg_id, username):
        self.cur.execute(
            f"""
            UPDATE winners
            SET tg_id={tg_id},
            username='{username}'
            """
        )

        self.conn.commit()

    def get_user_bids(self, tg_id, code):
        bids_count = self.cur.execute(
            f"""
            SELECT * FROM bids
            WHERE tg_id={tg_id} AND code='{code}'
            """
        ).fetchall()

        if bids_count is None:
            return 0
        return len(bids_count)


    def save_lot(self, lot_id, chat_id, code):
        self.cur.execute(
            """
            INSERT INTO saved_lots
            (lot_id, chat_id, code)
            VALUES
            (?, ?, ?)
            """,
            (lot_id, chat_id, code)
        )
        self.conn.commit()

    def get_saved_lots(self, code):
        saved_lots = self.cur.execute(
            f"""
            SELECT lot_id, chat_id FROM saved_lots
            WHERE code='{code}'
            """
        ).fetchall()

        self.conn.commit()
        if saved_lots is None:
            return []
        return saved_lots

    def add_bid(self, tg_id, username, lot_price, code):
        info = (tg_id, username, lot_price, code)
        self.cur.execute(
            """
            INSERT INTO bids
            (tg_id, username, lot_price, code)
            VALUES
            (?, ?, ?, ?)
            """,
            info
        )
        self.conn.commit()

    def get_bid(self, code):
        users = self.cur.execute(
            f"""
            SELECT tg_id, username, lot_price FROM bids
            WHERE code='{code}'
            """
        ).fetchall()

        return users

    def add_user(self, phone, email, tg_id, fullname, gender, age, avatar_name, region, company):
        self.cur.execute(
            f"""
            DELETE FROM users
            WHERE phone='{phone}'
            """
        )

        with open(avatar_name, "rb") as avatar:
            info = (phone, email, tg_id, fullname, gender, age, avatar.read(), region, company, 0)

            self.cur.execute(
                """
                INSERT INTO users
                (phone, email, tg_id, fullname, gender, age, avatar, region, company, blocked)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                info
            )

            self.add_registered_user(tg_id=tg_id)
            self.conn.commit()

    def block_user(self, tg_id):
        self.cur.execute(
            f"""
            UPDATE users
            SET blocked=1
            WHERE tg_id={tg_id}
            """
        )
        self.conn.commit()

    def get_blocked_users(self):
        blocked_users = self.cur.execute(
            """
            SELECT tg_id FROM users
            WHERE blocked=1
            """
        ).fetchall()

        if blocked_users is None:
            return []
        blocked_users = [elem[0] for elem in blocked_users]
        return blocked_users

    def unlock_user_by_tg(self, tg_id):
        self.cur.execute(
            f"""
            UPDATE users
            SET blocked=0
            WHERE tg_id='{tg_id}'
            """
        )
        self.conn.commit()

    def unlock_user(self, phone):
        self.cur.execute(
            f"""
            UPDATE users
            SET blocked=0
            WHERE phone='{phone}'
            """
        )
        self.conn.commit()


    def add_partner(self, phone):
        self.cur.execute(
            """
            INSERT INTO users
            (phone)
            VALUES(?)
            """,
            (phone,)
        )
        self.conn.commit()

    def delete_partner(self, phone):
        self.cur.execute(
            f"""
            DELETE FROM users
            WHERE phone='{phone}'
            """
        )
        self.conn.commit()

    def add_admin(self, phone):
        self.cur.execute(
            """
            INSERT INTO admins
            (phone)
            VALUES(?)
            """,
            (phone,)
        )
        self.conn.commit()

    def delete_admin(self, phone):
        self.cur.execute(
            """
            DELETE FROM admins
            WHERE phone='{phone}'
            """
        )
        self.conn.commit()

    def add_admin_id(self, tg_id, phone):
        self.cur.execute(
            f"""
            UPDATE admins
            SET tg_id={tg_id}
            WHERE phone='{phone}'
            """
        )
        self.conn.commit()

    def add_registered_user(self, tg_id):
        self.cur.execute(
            """
            INSERT INTO registration_passed
            (tg_id)
            VALUES(?)
            """,
            (tg_id,)
        )
        self.conn.commit()

    def get_registered_users(self):
        registered_users = self.cur.execute(
            """
            SELECT tg_id FROM registration_passed
            """
        ).fetchall()

        if registered_users is None:
            return []
        registered_users = [elem[0] for elem in registered_users]
        return registered_users

    def get_phones(self):
        phones = self.cur.execute(
            """
            SELECT phone FROM users
            """
        ).fetchall()

        if phones is None:
            return []

        phones = [elem[0] for elem in phones]
        return phones

    def user_by_id(self, tg_id):
        user_info = self.cur.execute(
            f"""
            SELECT phone, fullname FROM users
            WHERE tg_id={tg_id}
            """
        ).fetchone()

        return user_info

    def get_users_ids(self):
        ids = self.cur.execute(
            """
            SELECT tg_id FROM users
            """
        ).fetchall()

        if ids is None:
            return []

        ids = [elem[0] for elem in ids]
        return ids

    def get_lots_codes(self):
        codes = self.cur.execute(
            """
            SELECT code FROM now_lots
            """
        ).fetchall()

        if codes is not None:
            codes = [elem[0] for elem in codes]
            return codes
        return []

    def get_admins(self):
        ids = self.cur.execute(
            """
            SELECT tg_id FROM admins
            """
        ).fetchall()

        if ids is None:
            return []

        ids = [elem[0] for elem in ids]
        return ids

    def get_admin_phones(self):
        phones = self.cur.execute(
            """
            SELECT phone FROM admins
            """
        ).fetchall()

        if phones is None:
            return []

        phones = [elem[0] for elem in phones]
        return phones

    def add_lot(self, name, model, code, storage, season, tires, disks, price, photo, google_link, stage):
        status = "stock"
        info = (name, model, code, storage, season, tires, disks, price, photo, status, google_link, stage)
        self.cur.execute(
            """
            INSERT OR REPLACE INTO lots
            (name, model, code, storage, season, tires, disks, price, photo, status, google_link, stage)
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            info
        )

        self.conn.commit()

    def get_all_codes(self):
        codes = self.cur.execute(
            """
            SELECT code FROM lots
            """
        ).fetchall()

        if codes is None:
            return []
        codes = [code[0] for code in codes]
        return codes

    def get_lot(self, code):
        lots = self.cur.execute(
            f"""
            SELECT * FROM lots
            WHERE code='{code}'
            
            """
        ).fetchone()

        self.conn.commit()
        return lots

    def get_selling_lot(self, code):
        lot = self.cur.execute(
            f"""
            SELECT lot_id, lot_text, lot_price FROM now_lots
            WHERE code='{code}'
            """
        ).fetchone()

        self.conn.commit()
        # print(lot)
        return lot

    def get_waiting_lots(self):
        waiting_codes = self.cur.execute(
            f"""
            SELECT code FROM lots
            WHERE status='waiting'
            """
        ).fetchall()

        if waiting_codes is None:
            return []
        waiting_codes = [elem[0] for elem in waiting_codes]
        return waiting_codes

    def update_price(self, code, price):
        self.cur.execute(
            f"""
            UPDATE now_lots
            SET lot_price=lot_price + {price}
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def update_now_lot_price_and_text(self, new_lot_price, new_lot_text, code):
        self.cur.execute(
            f"""
            UPDATE now_lots
            SET lot_price=?,
            lot_text=?
            WHERE code=?
            """,
            (new_lot_price, new_lot_text, code)
        )
        self.conn.commit()
    def add_auc_lot(self, lot_id, lot_text, lot_price, code):
        self.cur.execute(
            """
            INSERT OR REPLACE INTO now_lots
            (lot_id, lot_text, lot_price, code)
            VALUES
            (?, ?, ?, ?)
            """,
            (lot_id, lot_text, lot_price, code)
        )
        self.conn.commit()

    def edit_lot_price(self, code, new_price):
        self.cur.execute(
            f"""
            UPDATE lots
            SET price='{new_price}'
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def update_status_auction(self, code):
        self.cur.execute(
            f"""
            UPDATE lots
            SET status="auction"
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def update_status_stock(self, code):
        self.cur.execute(
            f"""
            UPDATE lots
            SET status="stock"
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def update_status_draw(self, code):
        self.cur.execute(
            f"""
            UPDATE lots
            SET status="draw"
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def update_status_waiting(self, code):
        self.cur.execute(
            f"""
            UPDATE lots
            SET status="waiting"
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def update_status_deleted(self, code):
        self.cur.execute(
            f"""
            UPDATE lots
            SET status="deleted"
            WHERE code='{code}'
            """
        )
        self.conn.commit()


    def update_status_sell(self, code):
        self.cur.execute(
            f"""
            UPDATE lots
            SET status="sell"
            WHERE code='{code}'
            """
        )
        self.conn.commit()

    def get_start_lot_time(self, code):
        time = self.cur.execute(
            f"""
            SELECT time FROM lots_time
            WHERE code='{code}'
            """
        ).fetchone()

        time = time[0]
        minutes, hours = time.split("_")
        return minutes, hours

    def get_draw_lots(self):
        three_lots = self.cur.execute(
            f"""
            SELECT name, model, code, storage, season, tires, disks, price, photo, status, google_link, stage FROM lots
            WHERE status="draw"
            """
        ).fetchall()

        return three_lots
