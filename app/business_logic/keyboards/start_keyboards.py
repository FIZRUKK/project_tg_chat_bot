from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class StartKeyboards:
    @staticmethod
    async def main_menu() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Option 1", callback_data="option_1"),
                    InlineKeyboardButton(text="Option 2", callback_data="option_2"),
                ],
                [
                    InlineKeyboardButton(text="Help", callback_data="help"),
                ]
            ]
        )
        return keyboard
    

start_keyboard = StartKeyboards()