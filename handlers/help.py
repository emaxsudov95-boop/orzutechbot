from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_setting
from config import SUPPORT_USERNAME

from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
@router.message(F.text.in_(["📞 Yordam", "📞 Yordam / Qo'llanma"]))
async def show_help(message: Message):
    support = await get_setting("support_username", SUPPORT_USERNAME)
    support_clean = support.replace("@", "")

    text = (
        "📖 <b>Botdan foydalanish qo'llanmasi va qoidalar</b>\n\n"
        "1️⃣ <b>Hisobni to'ldirish:</b>\n"
        "• '💰 Balans to'ldirish' tugmasini bosing.\n"
        "• Karta (Uzcard/Humo) orqali to'lov qilib chekni yuboring, yoki <b>Telegram Stars</b> orqali 1 soniyada avtomatik to'lang.\n\n"
        "2️⃣ <b>Buyurtma berish:</b>\n"
        "• '🚀 Xizmatlar' bo'limidan ijtimoiy tarmoqni tanlang (Telegram, Instagram, TikTok, YouTube, Stars).\n"
        "• O'zingizga kerakli xizmatni tanlab, havola va miqdorni kiriting.\n"
        "• Buyurtmani tasdiqlang — u avtomatik tarzda bajarilishga o'tadi.\n\n"
        "⚠️ <b>Muhim eslatmalar:</b>\n"
        "• Havola kiritilayotgan kanal, guruh yoki profil <b>OCHIQ (PUBLIC)</b> bo'lishi shart!\n"
        "• Buyurtma bajarilayotgan vaqtda profil havolasini (username) o'zgartirmang.\n"
        "• Bitta havola uchun oldingi buyurtma tugamasdan turib yangi xuddi shunday buyurtma bermang.\n\n"
        "📞 <b>Qo'llab-quvvatlash xizmati:</b>\n"
        f"Savollar yoki muammolar bo'lsa, adminga murojaat qiling: @{support_clean}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Qo'llab-quvvatlash (Admin)", url=f"https://t.me/{support_clean}")
        ]
    ])

    await message.answer(text, reply_markup=kb, parse_mode="HTML")
