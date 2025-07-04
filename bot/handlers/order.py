from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards import main_menu_keyboard, start_keyboard, cancel_keyboard
from database.db import save_user, get_all_users, save_order, get_all_orders, update_measure_date
import datetime
import pytz

order_router = Router()

class OrderForm(StatesGroup):
    name = State()
    phone = State()
    address = State()
    confirm = State()
    desired_date = State()

class CalcForm(StatesGroup):
    area = State()
    type = State()

ADMIN_ID = 5137827921

MENU_BUTTONS = [
    "Оформить заказ",
    "Потолочный калькулятор",
    "Связаться с мастером",
    "Посмотреть примеры работ",
    "Старт"
]

@order_router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz).hour
    if 5 <= now < 12:
        greeting = "Доброе утро"
    elif 12 <= now < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"
    await message.answer(
        f"{greeting}! Меня зовут мастер Роман и я готов выполнить ваш заказ.",
        reply_markup=start_keyboard()
    )
    await state.clear()

@order_router.message(F.text == "Старт")
async def start_dialog(message: Message, state: FSMContext):
    await message.answer(
        "Выберите действие в меню:",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()

@order_router.message(F.text == "Оформить заказ")
async def start_order(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, представьтесь (напишите ваше имя).",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(OrderForm.name)

@order_router.message(OrderForm.name)
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if name == "Отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=main_menu_keyboard())
        return
    if name == "Потолочный калькулятор":
        await state.clear()
        await calc_start_btn(message, state)
        return
    if name == "Оформить заказ":
        await state.clear()
        await start_order(message, state)
        return
    if name == "Связаться с мастером":
        await state.clear()
        await contact_master(message)
        return
    if name == "Посмотреть примеры работ":
        await state.clear()
        await show_examples(message)
        return
    await state.update_data(name=name)
    await message.answer("Спасибо! Теперь укажите номер телефона (можно в любом формате):", reply_markup=cancel_keyboard())
    await state.set_state(OrderForm.phone)

@order_router.message(OrderForm.phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if phone == "Отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=main_menu_keyboard())
        return
    if phone == "Потолочный калькулятор":
        await state.clear()
        await calc_start_btn(message, state)
        return
    if phone == "Оформить заказ":
        await state.clear()
        await start_order(message, state)
        return
    if phone == "Связаться с мастером":
        await state.clear()
        await contact_master(message)
        return
    if phone == "Посмотреть примеры работ":
        await state.clear()
        await show_examples(message)
        return
    data = await state.get_data()
    name = data.get('name', '')
    await save_user(name, phone)
    await state.update_data(phone=phone)
    await message.answer("Спасибо! Теперь напишите адрес, где нужен монтаж.", reply_markup=cancel_keyboard())
    await state.set_state(OrderForm.address)

@order_router.message(OrderForm.address)
async def get_address(message: Message, state: FSMContext):
    address = message.text.strip()
    if address == "Отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=main_menu_keyboard())
        return
    if address == "Потолочный калькулятор":
        await state.clear()
        await calc_start_btn(message, state)
        return
    if address == "Оформить заказ":
        await state.clear()
        await start_order(message, state)
        return
    if address == "Связаться с мастером":
        await state.clear()
        await contact_master(message)
        return
    if address == "Посмотреть примеры работ":
        await state.clear()
        await show_examples(message)
        return
    await state.update_data(address=address)
    data = await state.get_data()
    await message.answer(
        f"Проверьте ваши данные:\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n\n"
        f"Если всё верно — напишите 'да' или 'верно', если нужно изменить — нажмите 'Отмена'.",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(OrderForm.confirm)

@order_router.message(OrderForm.confirm)
async def confirm_order(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    if text == "отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=main_menu_keyboard())
        return
    if text in ["да", "верно"]:
        await message.answer("Пожалуйста, укажите желаемую дату монтажа (например, 10.07.2025):", reply_markup=cancel_keyboard())
        await state.set_state(OrderForm.desired_date)
        return
    await message.answer("Пожалуйста, напишите 'да' или 'верно', либо нажмите 'Отмена'.", reply_markup=cancel_keyboard())

@order_router.message(OrderForm.desired_date)
async def get_desired_date(message: Message, state: FSMContext):
    desired_date = message.text.strip()
    if desired_date.lower() == "отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=main_menu_keyboard())
        return
    data = await state.get_data()
    await save_order(data['name'], data['phone'], data['address'], desired_date)
    await message.answer(
        f"Спасибо! Ваша заявка принята. Мы свяжемся с вами для уточнения времени замера.",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()

@order_router.message(F.text == "Расчёт стоимости")
async def calc_start(message: Message, state: FSMContext):
    await message.answer("Введите метраж помещения (в м²):", reply_markup=cancel_keyboard())
    await state.set_state(CalcForm.area)

@order_router.message(CalcForm.area)
async def calc_area(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "Отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=main_menu_keyboard())
        return
    if text == "Потолочный калькулятор":
        await state.clear()
        await calc_start_btn(message, state)
        return
    if text == "Оформить заказ":
        await state.clear()
        await start_order(message, state)
        return
    if text == "Связаться с мастером":
        await state.clear()
        await contact_master(message)
        return
    if text == "Посмотреть примеры работ":
        await state.clear()
        await show_examples(message)
        return
    try:
        area = float(text.replace(",", "."))
        if area <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число (метраж в м²):", reply_markup=cancel_keyboard())
        return
    await state.update_data(area=area)
    await message.answer("Выберите тип потолка:\n1. ПВХ матовый\n2. ПВХ глянцевый\n3. Тканевый\n4. Эксклюзивный\n(Напишите номер варианта)", reply_markup=cancel_keyboard())
    await state.set_state(CalcForm.type)

@order_router.message(CalcForm.type)
async def calc_type(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "Отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=main_menu_keyboard())
        return
    if text == "Потолочный калькулятор":
        await state.clear()
        await calc_start_btn(message, state)
        return
    if text == "Оформить заказ":
        await state.clear()
        await start_order(message, state)
        return
    if text == "Связаться с мастером":
        await state.clear()
        await contact_master(message)
        return
    if text == "Посмотреть примеры работ":
        await state.clear()
        await show_examples(message)
        return
    types = {
        "1": ("ПВХ матовый", 290, 490),
        "2": ("ПВХ глянцевый", 390, 560),
        "3": ("Тканевый", 950, 1500),
        "4": ("Эксклюзивный", 590, 1500),
    }
    t = text
    if t not in types:
        await message.answer("Пожалуйста, выберите вариант из списка (1-4):", reply_markup=cancel_keyboard())
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
        f"\nЭто примерная стоимость. Для точного расчёта выберите 'Оформить заказ'!",
        reply_markup=main_menu_keyboard()
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

@order_router.message(F.text == "/orders")
async def show_orders(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ запрещён. Только для администратора.")
        return
    orders = await get_all_orders()
    if not orders:
        await message.answer("Заявок пока нет.")
        return
    text = "Список заявок:\n"
    for order in orders:
        text += f"ID: {order[0]}, Имя: {order[1]}, Телефон: {order[2]}, Адрес: {order[3]}, Дата монтажа: {order[4]}, Создано: {order[5]}\n"
    await message.answer(text)

@order_router.message(F.text.regexp(r"^/set_measure \\d+ \\S+"))
async def set_measure_date(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ запрещён. Только для администратора.")
        return
    try:
        parts = message.text.strip().split(maxsplit=2)
        order_id = int(parts[1])
        measure_date = parts[2]
    except Exception:
        await message.answer("Используйте формат: /set_measure <order_id> <дата>")
        return
    await update_measure_date(order_id, measure_date)
    await message.answer(f"Дата замера для заявки {order_id} установлена: {measure_date}") 