import pytest
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.handlers.order import order_router
import asyncio

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def bot():
    return Bot(token="TEST:TOKEN", parse_mode="HTML")

@pytest.fixture
def dispatcher(bot):
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(order_router)
    return dp

# Моки для Message и FSMContext
class MockMessage:
    def __init__(self, text, from_user_id=123):
        self.text = text
        self.from_user = type('User', (), {'id': from_user_id})
        self.answer_calls = []
    async def answer(self, text, **kwargs):
        self.answer_calls.append((text, kwargs))

class MockFSMContext:
    def __init__(self):
        self.state = None
        self.data = {}
    async def set_state(self, state):
        self.state = state
    async def update_data(self, **kwargs):
        self.data.update(kwargs)
    async def get_data(self):
        return self.data
    async def clear(self):
        self.state = None
        self.data = {}

@pytest.mark.asyncio
async def test_start_and_menu():
    from bot.handlers.order import start_dialog
    message = MockMessage("Старт")
    state = MockFSMContext()
    await start_dialog(message, state)
    assert "Выберите действие в меню" in message.answer_calls[0][0]
    assert state.state is None

@pytest.mark.asyncio
async def test_order_cancel():
    from bot.handlers.order import start_order, get_name
    message = MockMessage("Оформить заказ")
    state = MockFSMContext()
    await start_order(message, state)
    assert "Пожалуйста, представьтесь" in message.answer_calls[0][0]
    # Отмена
    message_cancel = MockMessage("Отмена")
    await get_name(message_cancel, state)
    assert "Действие отменено" in message_cancel.answer_calls[0][0]
    assert state.state is None

@pytest.mark.asyncio
async def test_order_full_flow():
    from bot.handlers.order import start_order, get_name, get_phone, get_address
    state = MockFSMContext()
    # Оформить заказ
    message = MockMessage("Оформить заказ")
    await start_order(message, state)
    # Имя
    message_name = MockMessage("Иван")
    await get_name(message_name, state)
    # Телефон
    message_phone = MockMessage("89991234567")
    await get_phone(message_phone, state)
    # Адрес
    message_address = MockMessage("Москва")
    await get_address(message_address, state)
    assert "Проверьте ваши данные" in message_address.answer_calls[0][0]
    assert state.state is None

@pytest.mark.asyncio
async def test_calc_start_btn():
    from bot.handlers.order import calc_start_btn
    message = MockMessage("Потолочный калькулятор")
    state = MockFSMContext()
    await calc_start_btn(message, state)
    assert "Введите метраж помещения" in message.answer_calls[0][0] 