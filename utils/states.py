from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_quantity = State()
    waiting_for_confirm = State()

class DepositStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_receipt = State()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_user_id = State()
    waiting_for_amount = State()
    waiting_for_price = State()
    waiting_for_provider_service_id = State()
    waiting_for_api_url = State()
    waiting_for_api_key = State()
    waiting_for_card_number = State()
    waiting_for_card_holder = State()
    waiting_for_card1_number = State()
    waiting_for_card2_number = State()
    waiting_for_min_deposit = State()
