from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="Оформить заказ")],
        [KeyboardButton(text="Потолочный калькулятор")],
        [KeyboardButton(text="Связаться с мастером")],
        [KeyboardButton(text="Посмотреть примеры работ")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def start_keyboard():
    keyboard = [
        [KeyboardButton(text="Старт")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def cancel_keyboard():
    keyboard = [
        [KeyboardButton(text="Отмена")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True) 