"""
Inline-клавиатуры для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_period_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора периода для графиков"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 час", callback_data="graph_1"),
            InlineKeyboardButton(text="6 часов", callback_data="graph_6"),
        ],
        [
            InlineKeyboardButton(text="24 часа", callback_data="graph_24"),
            InlineKeyboardButton(text="7 дней", callback_data="graph_168"),
        ],
    ])
    return keyboard


def get_history_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора периода для истории"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 час", callback_data="history_1"),
            InlineKeyboardButton(text="6 часов", callback_data="history_6"),
        ],
        [
            InlineKeyboardButton(text="24 часа", callback_data="history_24"),
            InlineKeyboardButton(text="7 дней", callback_data="history_168"),
        ],
    ])
    return keyboard

