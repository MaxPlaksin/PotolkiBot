from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards import main_menu_keyboard
from database.db import save_user, get_all_users

order_router = Router()

class OrderForm(StatesGroup):
    name = State()
    phone = State()
    address = State()

class CalcForm(StatesGroup):
    area = State()
    type = State()

ADMIN_ID = 5137827921

@order_router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer(
        "Добрый день! Меня зовут мастер Романт и я готов выполнить ваш заказ.\n\nПожалуйста, представьтесь (напишите ваше имя).",
        reply_markup=main_menu_keyboard()
    )
    await state.set_state(OrderForm.name)

@order_router.message(OrderForm.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Спасибо! Теперь укажите номер телефона (можно в любом формате):")
    await state.set_state(OrderForm.phone)

@order_router.message(OrderForm.phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    data = await state.get_data()
    name = data.get('name', '')
    await save_user(name, phone)
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

@order_router.message(F.text == "Расчёт стоимости")
async def calc_start(message: Message, state: FSMContext):
    await message.answer("Введите метраж помещения (в м²):")
    await state.set_state(CalcForm.area)

@order_router.message(CalcForm.area)
async def calc_area(message: Message, state: FSMContext):
    try:
        area = float(message.text.replace(",", "."))
        if area <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число (метраж в м²):")
        return
    await state.update_data(area=area)
    await message.answer("Выберите тип потолка:\n1. ПВХ матовый\n2. ПВХ глянцевый\n3. Тканевый\n4. Эксклюзивный\n(Напишите номер варианта)")
    await state.set_state(CalcForm.type)

@order_router.message(CalcForm.type)
async def calc_type(message: Message, state: FSMContext):
    types = {
        "1": ("ПВХ матовый", 290, 490),
        "2": ("ПВХ глянцевый", 390, 560),
        "3": ("Тканевый", 950, 1500),
        "4": ("Эксклюзивный", 590, 1500),
    }
    t = message.text.strip()
    if t not in types:
        await message.answer("Пожалуйста, выберите вариант из списка (1-4):")
        return
    name, cheap, expensive = types[t]
    data = await state.get_data()
    area = data["area"]
    price_cheap = area * cheap
    price_exp = area * expensive
    await message.answer(
        f"Тип потолка: {name}\n"
        f"Метраж: {area} м²\n"
        f"\nВариант подешевле: {int(price_cheap)} руб.\n"
        f"Вариант подороже: {int(price_exp)} руб.\n"
        f"\nЭто примерная стоимость. Для точного расчёта выберите 'Оформить заказ'!"
    )
    await state.clear()

@order_router.message(F.text == "/users")
async def show_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ запрещён. Только для администратора.")
        return
    users = await get_all_users()
    if not users:
        await message.answer("Пользователей пока нет.")
        return
    text = "Список пользователей:\n"
    for user in users:
        text += f"ID: {user[0]}, Имя: {user[1]}, Телефон: {user[2]}, Дата: {user[3]}\n"
    await message.answer(text)

@order_router.message(F.text == "Связаться с мастером")
async def contact_master(message: Message):
    await message.answer("Вы можете связаться с мастером напрямую по телефону: +7 999 123-45-67 или в Telegram: @master_romant")

@order_router.message(F.text == "Посмотреть примеры работ")
async def show_examples(message: Message):
    await message.answer("Выберите, что хотите посмотреть:\n1. Фото примеры\n2. Видео примеры\n(Напишите номер варианта или уточните, что интересно)")

@order_router.message(F.text == "Потолочный калькулятор")
async def calc_start_btn(message: Message, state: FSMContext):
    await calc_start(message, state) 