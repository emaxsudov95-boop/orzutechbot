from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext
from database import get_or_create_user, get_referral_stats, get_setting, set_setting, get_admin_ids, is_admin
from keyboards.reply import get_main_menu
from utils.formatters import format_uzs
from config import REFERRAL_PERCENT

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    referrer_id = None
    args = command.args
    if args:
        if args.startswith("ref_") and args[4:].isdigit():
            referrer_id = int(args[4:])
        elif args.isdigit():
            referrer_id = int(args)

    user = await get_or_create_user(
        user_id=user_id,
        username=username,
        full_name=full_name,
        referrer_id=referrer_id
    )

    admin_ids = await get_admin_ids()
    if not admin_ids:
        # Hali admin yo'q bo'lsa, birinchi start bosgan foydalanuvchini avtomatik bosh admin qilish
        await set_setting("admin_id", str(user_id))
        admin_ids = [user_id]
        await message.answer(
            f"👑 <b>Siz muvaffaqiyatli Bosh Admin sifatida belgilandingiz!</b>\n\n"
            f"🆔 Telegram ID: <code>{user_id}</code>\n"
            f"Foydalanuvchilar to'lov qilganda yuborgan barcha cheklar sizga tasdiqlash uchun yuboriladi.",
            parse_mode="HTML"
        )

    admin_status = await is_admin(user_id)

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {full_name}!</b>\n\n"
        f"🚀 <b>Eng sifatli va arzon SMM xizmatlari botiga xush kelibsiz!</b>\n\n"
        f"Bizning bot orqali siz:\n"
        f"• <b>Telegram</b> (Kafolatli obunachilar, ko'rishlar, reaksiyalar)\n"
        f"• <b>Instagram</b> (Obunachilar, layklar, reels ko'rishlar)\n"
        f"• <b>TikTok</b> (Obunachilar, layklar, ko'rishlar)\n"
        f"• <b>YouTube</b> (Obunachi, ko'rishlar, layklar)\n"
        f"• <b>Telegram Stars</b> (Xarid qilish va balans to'ldirish)\n\n"
        f"💡 Kerakli bo'limni quyidagi menyudan tanlang:"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_main_menu(is_admin=admin_status),
        parse_mode="HTML"
    )

@router.message(Command("id"))
@router.message(Command("myid"))
async def cmd_my_id(message: Message):
    user_id = message.from_user.id
    admin_status = await is_admin(user_id)
    role = "👑 Bosh Admin" if admin_status else "👤 Oddiy foydalanuvchi"
    await message.answer(
        f"🆔 <b>Sizning Telegram ID raqamingiz:</b> <code>{user_id}</code>\n"
        f"👤 <b>Rol:</b> {role}",
        parse_mode="HTML"
    )

@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    admin_status = await is_admin(message.from_user.id)
    await message.answer(
        "❌ Amaliyot bekor qilindi.",
        reply_markup=get_main_menu(is_admin=admin_status)
    )

@router.message(F.text.in_(["👥 Referal tizimi", "👥 Referal"]))
async def referral_handler(message: Message):
    user_id = message.from_user.id
    bot_info = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"

    count, earnings = await get_referral_stats(user_id)

    text = (
        f"👥 <b>Do'stlarni taklif qilish va daromad olish!</b>\n\n"
        f"Do'stlaringizni taklif qiling va ular hisobini to'ldirganda <b>{REFERRAL_PERCENT}%</b> "
        f"miqdorida naqd bonusga ega bo'ling!\n\n"
        f"📊 <b>Sizning statistikangiz:</b>\n"
        f"• Taklif qilingan do'stlar: <b>{count} ta</b>\n"
        f"• Ishlangan jami daromad: <b>{format_uzs(earnings)}</b>\n\n"
        f"🔗 <b>Sizning referal havolangiz:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"Ushbu havolani do'stlaringizga yoki kanallaringizga ulashing!"
    )
    await message.answer(text, parse_mode="HTML")
