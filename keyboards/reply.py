from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi (@PixelSmmUzBot uslubida)"""
    keyboard = [
        [
            KeyboardButton(text="🚀 Xizmatlar"),
            KeyboardButton(text="💰 Balans to'ldirish")
        ],
        [
            KeyboardButton(text="👤 Kabinet"),
            KeyboardButton(text="📋 Buyurtmalarim")
        ],
        [
            KeyboardButton(text="⭐ Telegram Stars"),
            KeyboardButton(text="👥 Referal tizimi")
        ],
        [
            KeyboardButton(text="📞 Yordam")
        ]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="⚙️ Admin Panel")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_cancel_menu() -> ReplyKeyboardMarkup:
    """Jarayonni bekor qilish tugmasi"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )
