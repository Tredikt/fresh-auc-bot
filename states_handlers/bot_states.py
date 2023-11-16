from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    phone = State()
    email = State()
    fullname = State()
    gender = State()
    age = State()
    avatar = State()
    region = State()
    company = State()


class AdminStates(StatesGroup):
    add_partner = State()
    add_admin = State()
    delete_partner = State()
    delete_admin = State()
    delete_lot = State()
    edit_lot_code = State()
    edit_lot_price = State()


class AuctionStates(StatesGroup):
    winner = State()
