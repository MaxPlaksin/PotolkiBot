from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

order_router = Router()

class OrderForm(StatesGroup):
    name = State()
    phone = State()
    address = State()

@order_router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer("Здравствуйте! Давайте оформим заявку на потолки.\n\nПожалуйста, напишите ваше имя.")
    await state.set_state(OrderForm.name)

@order_router.message(OrderForm.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Спасибо! Теперь укажите номер телефона (пример: +7XXXXXXXXXX).")
    await state.set_state(OrderForm.phone)

@order_router.message(OrderForm.phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not (phone.startswith("+7") and len(phone) == 12) and not (phone.startswith("8") and len(phone) == 11):
        await message.answer("Пожалуйста, введите корректный номер телефона (пример: +7XXXXXXXXXX).")
        return
    await state.update_data(phone=phone)
    await message.answer("Спасибо! Теперь напишите адрес, где нужен монтаж.")
    await state.set_state(OrderForm.address)

@order_router.message(OrderForm.address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    data = await state.get_data()
    await message.answer(
        f"Проверьте ваши данные:\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n\n"
        f"Если всё верно — скоро перейдём к следующим вопросам!"
    )
    await state.clear() 