from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.formatters import format_uzs

def get_categories_keyboard() -> InlineKeyboardMarkup:
    """Ijtimoiy tarmoqlar toifalarini tanlash"""
    buttons = [
        [
            InlineKeyboardButton(text="📱 Telegram", callback_data="cat_telegram"),
            InlineKeyboardButton(text="📸 Instagram", callback_data="cat_instagram")
        ],
        [
            InlineKeyboardButton(text="🎵 TikTok", callback_data="cat_tiktok"),
            InlineKeyboardButton(text="▶️ YouTube", callback_data="cat_youtube")
        ],
        [
            InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="cat_stars")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_services_keyboard(services: list, category: str) -> InlineKeyboardMarkup:
    """Tanlangan toifadagi xizmatlar ro'yxati"""
    buttons = []
    for s in services:
        if category == "stars":
            price_text = format_uzs(s["price_per_1000"])
        else:
            price_text = f"1k/{format_uzs(s['price_per_1000'])}"
        
        btn_text = f"{s['name']} — {price_text}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"srv_{s['id']}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Barcha toifalar", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_order_confirm_keyboard(service_id: int) -> InlineKeyboardMarkup:
    """Buyurtmani tasdiqlash yoki bekor qilish tugmalari"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="confirm_order"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_deposit_methods_keyboard() -> InlineKeyboardMarkup:
    """To'lov usullarini tanlash"""
    buttons = [
        [
            InlineKeyboardButton(text="💳 Visa karta orqali to'lov", callback_data="pay_card")
        ],
        [
            InlineKeyboardButton(text="⭐ Telegram Stars (Avtomatik)", callback_data="pay_stars")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_stars_deposit_keyboard() -> InlineKeyboardMarkup:
    """Telegram Stars paketlari orqali hisob to'ldirish"""
    buttons = [
        [
            InlineKeyboardButton(text="🌟 10 Stars (2 500 so'm)", callback_data="stars_dep_10"),
            InlineKeyboardButton(text="🌟 25 Stars (6 250 so'm)", callback_data="stars_dep_25")
        ],
        [
            InlineKeyboardButton(text="🌟 50 Stars (12 500 so'm)", callback_data="stars_dep_50"),
            InlineKeyboardButton(text="🌟 100 Stars (25 000 so'm)", callback_data="stars_dep_100")
        ],
        [
            InlineKeyboardButton(text="🌟 250 Stars (62 500 so'm)", callback_data="stars_dep_250"),
            InlineKeyboardButton(text="🌟 500 Stars (125 000 so'm)", callback_data="stars_dep_500")
        ],
        [
            InlineKeyboardButton(text="⬅️ To'lov usullariga qaytish", callback_data="back_to_deposit_methods")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_payment_verify_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Admin uchun to'lov chekini tasdiqlash yoki rad etish"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"adm_pay_ok_{payment_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"adm_pay_no_{payment_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Admin boshqaruv paneli menyusi"""
    buttons = [
        [
            InlineKeyboardButton(text="📊 Umumiy Statistika", callback_data="adm_stats"),
            InlineKeyboardButton(text="💰 Balans Boshqaruvi", callback_data="adm_balance")
        ],
        [
            InlineKeyboardButton(text="📢 Xabar Tarqatish", callback_data="adm_broadcast"),
            InlineKeyboardButton(text="🌐 SMM API Sozlamalari", callback_data="adm_api")
        ],
        [
            InlineKeyboardButton(text="💵 Narxlarni o'zgartirish", callback_data="adm_prices"),
            InlineKeyboardButton(text="💳 Karta Rekvizitlari", callback_data="adm_card")
        ],
        [
            InlineKeyboardButton(text="🔙 Menyuni yopish", callback_data="adm_close")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_button(callback_data: str = "back_to_categories") -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data=callback_data)
    ]])
