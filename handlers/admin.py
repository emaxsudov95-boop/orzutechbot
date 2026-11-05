from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import (
    get_all_users_count,
    get_today_users_count,
    get_all_orders_count,
    get_total_spent,
    get_all_users,
    get_user,
    update_balance,
    get_all_services,
    get_service,
    update_service_price,
    update_service_provider_id,
    get_setting,
    set_setting,
    get_admin_ids,
    is_admin
)
from smm_api import SMMProviderAPI
from keyboards.inline import get_admin_menu_keyboard, get_back_button
from keyboards.reply import get_cancel_menu, get_main_menu
from utils.states import AdminStates
from utils.formatters import format_uzs
from config import (
    ADMIN_IDS,
    CARD_1_NUMBER,
    CARD_1_NAME,
    CARD_2_NUMBER,
    CARD_2_NAME,
    DEFAULT_CARD_HOLDER
)
import asyncio

router = Router()

@router.message(Command("admin"))
@router.message(F.text == "⚙️ Admin Panel")
async def show_admin_panel(message: Message, state: FSMContext):
    admin_ids = await get_admin_ids()
    if not admin_ids:
        await set_setting("admin_id", str(message.from_user.id))
        await message.answer(f"👑 Siz muvaffaqiyatli Bosh Admin qilib belgilandingiz! (ID: {message.from_user.id})")
    elif not await is_admin(message.from_user.id):
        return

    await state.clear()
    text = (
        "⚙️ <b>Admin Boshqaruv Paneli</b>\n\n"
        "Kerakli bo'limni tanlang:"
    )
    await message.answer(text, reply_markup=get_admin_menu_keyboard(), parse_mode="HTML")

@router.message(Command("setchat"))
async def cmd_set_check_chat(message: Message):
    if not await is_admin(message.from_user.id):
        return
    chat_id = message.chat.id
    await set_setting("check_chat_id", str(chat_id))
    await message.answer(
        f"✅ <b>Ushbu chat (ID: <code>{chat_id}</code>) to'lov cheklarini qabul qiluvchi alohida chat sifatida muvaffaqiyatli saqlandi!</b>\n\n"
        f"Endi foydalanuvchilar to'lov qilganda yuborgan barcha cheklar ushbu chatga tasdiqlash va rad etish tugmalari bilan birga keladi.",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "adm_close")
async def callback_admin_close(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Asosiy menyuga qaytdingiz.", reply_markup=get_main_menu(is_admin=True))
    await callback.answer()

# ==================== 1. STATISTIKA ====================

@router.callback_query(F.data == "adm_stats")
async def callback_admin_stats(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return

    users_total = await get_all_users_count()
    users_today = await get_today_users_count()
    orders_total = await get_all_orders_count()
    total_spent = await get_total_spent()

    # Provider balansini tekshirish
    api_url = await get_setting("provider_api_url", "")
    api_key = await get_setting("provider_api_key", "")
    provider_bal_text = "Ulanmagan"

    if api_url and api_key:
        p_res = await SMMProviderAPI.get_balance(api_url, api_key)
        if isinstance(p_res, dict) and "balance" in p_res:
            provider_bal_text = f"{p_res['balance']} {p_res.get('currency', 'USD')}"
        elif isinstance(p_res, dict) and "error" in p_res:
            provider_bal_text = f"Xatolik: {p_res['error']}"

    text = (
        "📊 <b>Botning Umumiy Statistikasi</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {users_total:,} ta\n"
        f"🆕 <b>Bugun qo'shilganlar:</b> {users_today:,} ta\n"
        f"📦 <b>Jami buyurtmalar:</b> {orders_total:,} ta\n"
        f"💰 <b>Jami tushum / aylanma:</b> {format_uzs(total_spent)}\n\n"
        f"🌐 <b>SMM Provayder hisobi:</b> {provider_bal_text}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Admin Menyu", callback_data="adm_back_menu")
    ]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "adm_back_menu")
async def callback_admin_back_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("⚙️ <b>Admin Boshqaruv Paneli</b>\n\nKerakli bo'limni tanlang:", reply_markup=get_admin_menu_keyboard(), parse_mode="HTML")
    await callback.answer()

# ==================== 2. BALANS BOSHQARUVI ====================

@router.callback_query(F.data == "adm_balance")
async def callback_admin_balance(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return

    await state.set_state(AdminStates.waiting_for_user_id)
    await callback.message.delete()
    await callback.message.answer(
        "💰 <b>Foydalanuvchi balansini o'zgartirish</b>\n\n"
        "Foydalanuvchining Telegram ID raqamini kiriting:",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_user_id)
async def process_admin_user_id(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    if not text.isdigit():
        await message.answer("⚠️ Faqat raqamli ID kiriting:")
        return

    target_id = int(text)
    user = await get_user(target_id)
    if not user:
        await message.answer(f"⚠️ ID: {target_id} foydalanuvchisi bot bazasidan topilmadi. Qaytadan kiriting:")
        return

    await state.update_data(target_user_id=target_id)
    await state.set_state(AdminStates.waiting_for_amount)
    await message.answer(
        f"👤 <b>Foydalanuvchi:</b> {user['full_name']} (@{user['username'] or 'mavjud emas'})\n"
        f"💰 <b>Hozirgi balansi:</b> {format_uzs(user['balance'])}\n\n"
        f"Qo'shish yoki ayirish miqdorini kiriting:\n"
        f"Masalan: 10000 (qo'shish) yoki -5000 (ayirish)",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )

@router.message(AdminStates.waiting_for_amount)
async def process_admin_balance_amount(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    try:
        amount = float(text)
    except ValueError:
        await message.answer("⚠️ Iltimos, to'g'ri son kiriting (masalan: 10000 yoki -5000):")
        return

    data = await state.get_data()
    target_id = data["target_user_id"]

    await update_balance(target_id, amount)
    updated_user = await get_user(target_id)

    # Foydalanuvchiga bildirishnoma
    try:
        if amount > 0:
            msg_user = f"💰 <b>Balansingiz to'ldirildi!</b>\n\nAdmin tomonidan balansingizga <b>+{format_uzs(amount)}</b> qo'shildi.\nHozirgi balans: <b>{format_uzs(updated_user['balance'])}</b>"
        else:
            msg_user = f"⚠️ <b>Balansingiz o'zgartirildi!</b>\n\nAdmin tomonidan balansingizdan <b>{format_uzs(abs(amount))}</b> yechildi.\nHozirgi balans: <b>{format_uzs(updated_user['balance'])}</b>"
        await message.bot.send_message(target_id, msg_user, parse_mode="HTML")
    except Exception:
        pass

    await state.clear()
    await message.answer(
        f"✅ <b>Balans muvaffaqiyatli yangilandi!</b>\n\n"
        f"👤 ID: <code>{target_id}</code>\n"
        f"💰 Yangi balans: <b>{format_uzs(updated_user['balance'])}</b>",
        reply_markup=get_main_menu(is_admin=True),
        parse_mode="HTML"
    )

# ==================== 3. XABAR TARQATISH (BROADCAST) ====================

@router.callback_query(F.data == "adm_broadcast")
async def callback_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return

    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.message.delete()
    await callback.message.answer(
        "📢 <b>Barcha foydalanuvchilarga xabar yuborish</b>\n\n"
        "Tarqatmoqchi bo'lgan xabaringizni yuboring (Matn, rasm yoki video):",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_broadcast)
async def process_admin_broadcast(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Xabar tarqatish bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    await state.clear()
    status_msg = await message.answer("⏳ Xabar tarqatish boshlandi...")

    users = await get_all_users()
    success = 0
    failed = 0

    for uid in users:
        try:
            await message.copy_to(chat_id=uid)
            success += 1
            await asyncio.sleep(0.05)  # Telegram limitlariga tushmaslik uchun
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"📢 <b>Xabar tarqatish yakunlandi!</b>\n\n"
        f"✅ Yetkazildi: <b>{success}</b> ta\n"
        f"❌ Yetkazilmadi (bloklangan): <b>{failed}</b> ta",
        parse_mode="HTML"
    )

# ==================== 4. SMM API SOZLAMALARI ====================

@router.callback_query(F.data == "adm_api")
async def callback_admin_api(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return

    api_url = await get_setting("provider_api_url", "O'rnatilmagan")
    api_key = await get_setting("provider_api_key", "O'rnatilmagan")
    masked_key = (api_key[:6] + "..." + api_key[-4:]) if len(api_key) > 10 else api_key

    text = (
        "🌐 <b>SMM Provayder API Sozlamalari</b>\n\n"
        f"🔗 <b>API URL:</b> <code>{api_url}</code>\n"
        f"🔑 <b>API Key:</b> <code>{masked_key}</code>\n\n"
        "Bu yerga o'zingiz ulangan SMM panel (Mediasmm, JustSMM, Peakerr va h.k.) API ma'lumotlarini kiritishingiz mumkin."
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ API URL o'zgartirish", callback_data="adm_set_api_url"),
            InlineKeyboardButton(text="✏️ API Key o'zgartirish", callback_data="adm_set_api_key")
        ],
        [
            InlineKeyboardButton(text="🔄 Provayder Balansini Tekshirish", callback_data="adm_check_api_bal")
        ],
        [
            InlineKeyboardButton(text="⬅️ Admin Menyu", callback_data="adm_back_menu")
        ]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "adm_set_api_url")
async def callback_set_api_url(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_api_url)
    await callback.message.delete()
    await callback.message.answer(
        "🔗 <b>Yangi API URL manzilini kiriting:</b>\nMasalan: https://justsmm.com/api/v2",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_api_url)
async def process_api_url(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    url = message.text.strip()
    await set_setting("provider_api_url", url)
    await state.clear()
    await message.answer(f"✅ API URL muvaffaqiyatli saqlandi:\n<code>{url}</code>", reply_markup=get_main_menu(is_admin=True), parse_mode="HTML")

@router.callback_query(F.data == "adm_set_api_key")
async def callback_set_api_key(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_api_key)
    await callback.message.delete()
    await callback.message.answer(
        "🔑 <b>Yangi API Key kalitini kiriting:</b>",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_api_key)
async def process_api_key(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    key = message.text.strip()
    await set_setting("provider_api_key", key)
    await state.clear()
    await message.answer("✅ API Key muvaffaqiyatli saqlandi!", reply_markup=get_main_menu(is_admin=True))

@router.callback_query(F.data == "adm_check_api_bal")
async def callback_check_api_bal(callback: CallbackQuery):
    api_url = await get_setting("provider_api_url", "")
    api_key = await get_setting("provider_api_key", "")

    if not api_url or not api_key:
        await callback.answer("⚠️ API URL yoki Key kiritilmagan!", show_alert=True)
        return

    res = await SMMProviderAPI.get_balance(api_url, api_key)
    if isinstance(res, dict) and "balance" in res:
        await callback.answer(f"💰 Provayderdagi hisob: {res['balance']} {res.get('currency', 'USD')}", show_alert=True)
    else:
        err = res.get("error", "Noma'lum xatolik") if isinstance(res, dict) else str(res)
        await callback.answer(f"❌ Xatolik yuz berdi: {err}", show_alert=True)

# ==================== 5. NARXLARNI O'ZGARTIRISH ====================

@router.callback_query(F.data == "adm_prices")
async def callback_admin_prices(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return

    services = await get_all_services()
    lines = ["💵 <b>Xizmatlar va joriy narxlar:</b>\n"]
    for s in services:
        lines.append(
            f"ID: <b>{s['id']}</b> | {s['name']}\n"
            f"Narxi: <b>{format_uzs(s['price_per_1000'])}</b> | Provider SID: <code>{s['provider_service_id']}</code>\n"
        )

    text = "\n".join(lines[:15])  # Telegram limitiga sig'ishi uchun
    text += "\n\nQuyidagi tugmalar orqali narx yoki Provider SID ni o'zgartirishingiz mumkin:"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Narxni o'zgartirish", callback_data="adm_edit_price"),
            InlineKeyboardButton(text="🔗 Provider SID bog'lash", callback_data="adm_edit_sid")
        ],
        [
            InlineKeyboardButton(text="⬅️ Admin Menyu", callback_data="adm_back_menu")
        ]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "adm_edit_price")
async def callback_edit_price(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_price)
    await callback.message.delete()
    await callback.message.answer(
        "✏️ <b>Narxni o'zgartirish:</b>\n\n"
        "Xizmat ID si va yangi narxini bo'sh joy bilan kiriting:\n"
        "Format: [Xizmat_ID] [Yangi_Narx]\n"
        "Masalan: 1 8500",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_price)
async def process_service_price(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[0].isdigit():
        await message.answer("⚠️ Noto'g'ri format! Masalan: 1 8500 ko'rinishida kiriting:")
        return

    service_id = int(parts[0])
    try:
        new_price = float(parts[1])
    except ValueError:
        await message.answer("⚠️ Yangi narx to'g'ri son bo'lishi kerak:")
        return

    srv = await get_service(service_id)
    if not srv:
        await message.answer(f"⚠️ ID: {service_id} raqamli xizmat topilmadi.")
        return

    await update_service_price(service_id, new_price)
    await state.clear()
    await message.answer(
        f"✅ <b>{srv['name']}</b> xizmatining yangi narxi belgilandi: <b>{format_uzs(new_price)}</b>",
        reply_markup=get_main_menu(is_admin=True),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "adm_edit_sid")
async def callback_edit_sid(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_provider_service_id)
    await callback.message.delete()
    await callback.message.answer(
        "🔗 <b>Provider Service ID bog'lash:</b>\n\n"
        "Botdagi xizmat ID si va SMM Provayder paneldagi Service ID sini kiriting:\n"
        "Format: [Bot_Xizmat_ID] [Provider_Service_ID]\n"
        "Masalan: 1 1450",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_provider_service_id)
async def process_service_sid(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        await message.answer("⚠️ Noto'g'ri format! Masalan: 1 1450 ko'rinishida kiriting:")
        return

    service_id = int(parts[0])
    provider_sid = int(parts[1])

    srv = await get_service(service_id)
    if not srv:
        await message.answer(f"⚠️ ID: {service_id} raqamli xizmat topilmadi.")
        return

    await update_service_provider_id(service_id, provider_sid)
    await state.clear()
    await message.answer(
        f"✅ <b>{srv['name']}</b> uchun Provider Service ID bog'landi: <code>{provider_sid}</code>",
        reply_markup=get_main_menu(is_admin=True),
        parse_mode="HTML"
    )

# ==================== 6. KARTA REKVIZITLARI ====================

@router.callback_query(F.data == "adm_card")
async def callback_admin_card(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return

    card1_num = await get_setting("card_1_number", CARD_1_NUMBER)
    card1_name = await get_setting("card_1_name", CARD_1_NAME)
    card2_num = await get_setting("card_2_number", CARD_2_NUMBER)
    card2_name = await get_setting("card_2_name", CARD_2_NAME)
    card_holder = await get_setting("card_holder", DEFAULT_CARD_HOLDER)
    min_dep = await get_setting("min_deposit", "5000")

    text = (
        "💳 <b>To'lov Rekvizitlari Sozlamalari</b>\n\n"
        f"👤 <b>Karta egasi:</b> {card_holder}\n\n"
        f"🔹 <b>1-Karta:</b> {card1_name}\n"
        f"• Raqami: <code>{card1_num}</code>\n\n"
        f"🔹 <b>2-Karta:</b> {card2_name or 'O`rnatilmagan'}\n"
        f"• Raqami: <code>{card2_num or 'O`rnatilmagan'}</code>\n\n"
        f"• Minimal to'lov summasi: <b>{format_uzs(float(min_dep))}</b>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ 1-kartani o'zgartirish", callback_data="adm_edit_card1"),
            InlineKeyboardButton(text="✏️ 2-kartani o'zgartirish", callback_data="adm_edit_card2")
        ],
        [
            InlineKeyboardButton(text="✏️ Minimal to'lovni o'zgartirish", callback_data="adm_edit_min_dep")
        ],
        [
            InlineKeyboardButton(text="⬅️ Admin Menyu", callback_data="adm_back_menu")
        ]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "adm_edit_card1")
async def callback_edit_card1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_card1_number)
    await callback.message.delete()
    await callback.message.answer(
        "💳 <b>1-karta (Uzum Bank) raqamini kiriting:</b>\nMasalan: 4916 9903 2289 2321",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_card1_number)
async def process_card1_number(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    card = message.text.strip()
    await set_setting("card_1_number", card)
    await set_setting("card_number", card)
    await state.clear()
    await message.answer(f"✅ 1-karta raqami saqlandi: <code>{card}</code>", reply_markup=get_main_menu(is_admin=True), parse_mode="HTML")

@router.callback_query(F.data == "adm_edit_card2")
async def callback_edit_card2(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_card2_number)
    await callback.message.delete()
    await callback.message.answer(
        "💳 <b>2-karta (Kapitalbank) raqamini kiriting:</b>\nMasalan: 4790 7400 0008 4837",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_card2_number)
async def process_card2_number(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    card = message.text.strip()
    await set_setting("card_2_number", card)
    await state.clear()
    await message.answer(f"✅ 2-karta raqami saqlandi: <code>{card}</code>", reply_markup=get_main_menu(is_admin=True), parse_mode="HTML")

@router.callback_query(F.data == "adm_edit_min_dep")
async def callback_edit_min_dep(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_min_deposit)
    await callback.message.delete()
    await callback.message.answer(
        "💵 <b>Yangi minimal to'lov summasini (so'mda) kiriting:</b>\nMasalan: 5000",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_min_deposit)
async def process_min_dep(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_main_menu(is_admin=True))
        return

    if not message.text.strip().isdigit():
        await message.answer("⚠️ Iltimos, faqat raqam kiriting:")
        return

    val = message.text.strip()
    await set_setting("min_deposit", val)
    await state.clear()
    await message.answer(f"✅ Minimal to'lov summasi saqlandi: <b>{format_uzs(float(val))}</b>", reply_markup=get_main_menu(is_admin=True), parse_mode="HTML")
