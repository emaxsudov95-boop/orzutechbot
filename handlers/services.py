from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import (
    get_services_by_category,
    get_service,
    get_user,
    record_user_order,
    create_order,
    get_setting,
    get_admin_ids
)
from smm_api import SMMProviderAPI
from keyboards.inline import (
    get_categories_keyboard,
    get_services_keyboard,
    get_order_confirm_keyboard,
    get_back_button
)
from keyboards.reply import get_cancel_menu, get_main_menu
from utils.states import OrderStates
from utils.formatters import format_uzs, format_status

router = Router()

@router.message(F.text == "🚀 Xizmatlar")
async def show_categories(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "🚀 <b>SMM Xizmatlari Katalogi</b>\n\n"
        "O'zingizga kerakli ijtimoiy tarmoqni tanlang:"
    )
    await message.answer(text, reply_markup=get_categories_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "back_to_categories")
async def callback_back_categories(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🚀 <b>SMM Xizmatlari Katalogi</b>\n\n"
        "O'zingizga kerakli ijtimoiy tarmoqni tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=get_categories_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def callback_category_services(callback: CallbackQuery):
    category = callback.data.split("_")[1]
    services = await get_services_by_category(category)

    category_titles = {
        "telegram": "📱 Telegram",
        "instagram": "📸 Instagram",
        "tiktok": "🎵 TikTok",
        "youtube": "▶️ YouTube",
        "stars": "⭐ Telegram Stars"
    }
    title = category_titles.get(category, "Xizmatlar")

    if not services:
        await callback.answer("Hozircha ushbu bo'limda faol xizmatlar yo'q.", show_alert=True)
        return

    text = f"<b>{title} xizmatlari ro'yxati:</b>\n\nKerakli xizmat ustiga bosing:"
    await callback.message.edit_text(text, reply_markup=get_services_keyboard(services, category), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("srv_"))
async def callback_service_details(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    service = await get_service(service_id)

    if not service:
        await callback.answer("Xizmat topilmadi.", show_alert=True)
        return

    is_fixed_stars = (service["category"] == "stars")

    await state.update_data(
        service_id=service_id,
        service_name=service["name"],
        price_per_1000=service["price_per_1000"],
        min_amount=service["min_amount"],
        max_amount=service["max_amount"],
        is_fixed=is_fixed_stars,
        category=service["category"],
        provider_service_id=service["provider_service_id"]
    )

    if is_fixed_stars:
        text = (
            f"<b>{service['name']}</b>\n\n"
            f"💵 <b>Paket narxi:</b> {format_uzs(service['price_per_1000'])}\n"
            f"📝 <b>Tavsif:</b> {service['description']}\n\n"
            f"🔗 <b>Stars qabul qiluvchi kanal yoki profil havolasini yuboring:</b>\n"
            f"Masalan: https://t.me/kanal_nomi yoki @username"
        )
    else:
        text = (
            f"<b>{service['name']}</b>\n\n"
            f"💵 <b>Narxi (1000 ta uchun):</b> {format_uzs(service['price_per_1000'])}\n"
            f"📊 <b>Minimal buyurtma:</b> {service['min_amount']} ta\n"
            f"📊 <b>Maksimal buyurtma:</b> {service['max_amount']} ta\n"
            f"📝 <b>Tavsif:</b> {service['description']}\n\n"
            f"🔗 <b>Buyurtma uchun kanal, profil yoki post havolasini yuboring:</b>\n"
            f"Masalan: https://t.me/kanal_nomi yoki https://instagram.com/p/..."
        )

    await state.set_state(OrderStates.waiting_for_link)
    await callback.message.delete()
    await callback.message.answer(text, reply_markup=get_cancel_menu(), parse_mode="HTML")
    await callback.answer()

@router.message(OrderStates.waiting_for_link)
async def process_target_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if link == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Buyurtma bekor qilindi.", reply_markup=get_main_menu())
        return

    if len(link) < 3:
        await message.answer("⚠️ Havola noto'g'ri ko'rinadi. Iltimos to'g'ri havola yoki @username kiriting:")
        return

    data = await state.get_data()
    await state.update_data(target_link=link)

    # Agar Stars paketi bo'lsa, miqdor so'ralmaydi (1 ta paket)
    if data.get("is_fixed"):
        quantity = 1
        total_price = data["price_per_1000"]
        await state.update_data(quantity=quantity, total_price=total_price)

        user = await get_user(message.from_user.id)
        user_balance = user["balance"] if user else 0.0

        summary = (
            f"📋 <b>Buyurtmani tasdiqlash</b>\n\n"
            f"• <b>Xizmat:</b> {data['service_name']}\n"
            f"• <b>Qabul qiluvchi:</b> <code>{link}</code>\n"
            f"• <b>Summa:</b> <b>{format_uzs(total_price)}</b>\n"
            f"• <b>Sizning balansingiz:</b> <b>{format_uzs(user_balance)}</b>\n\n"
        )

        if user_balance < total_price:
            summary += "⚠️ <b>Hisobingizda mablag' yetarli emas!</b> Iltimos, avval hisobingizni to'ldiring."
            await state.clear()
            await message.answer(summary, reply_markup=get_main_menu(), parse_mode="HTML")
            return

        summary += "Buyurtmani tasdiqlaysizmi?"
        await state.set_state(OrderStates.waiting_for_confirm)
        await message.answer(summary, reply_markup=get_order_confirm_keyboard(data["service_id"]), parse_mode="HTML")
        return

    # Normal xizmat uchun miqdor so'raladi
    min_amount = data["min_amount"]
    max_amount = data["max_amount"]
    await state.set_state(OrderStates.waiting_for_quantity)
    await message.answer(
        f"🔢 <b>Miqdorni kiriting:</b>\n"
        f"Minimal: <b>{min_amount}</b> ta | Maksimal: <b>{max_amount}</b> ta",
        reply_markup=get_cancel_menu(),
        parse_mode="HTML"
    )

@router.message(OrderStates.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Buyurtma bekor qilindi.", reply_markup=get_main_menu())
        return

    if not text.isdigit():
        await message.answer("⚠️ Iltimos, faqat raqam kiriting (masalan: 500 yoki 1000):")
        return

    quantity = int(text)
    data = await state.get_data()
    min_amount = data["min_amount"]
    max_amount = data["max_amount"]

    if quantity < min_amount or quantity > max_amount:
        await message.answer(
            f"⚠️ Miqdor <b>{min_amount}</b> va <b>{max_amount}</b> oralig'ida bo'lishi shart!\n"
            f"Qaytadan kiriting:",
            parse_mode="HTML"
        )
        return

    price_per_1000 = data["price_per_1000"]
    total_price = round((quantity / 1000.0) * price_per_1000, 2)

    await state.update_data(quantity=quantity, total_price=total_price)

    user = await get_user(message.from_user.id)
    user_balance = user["balance"] if user else 0.0

    summary = (
        f"📋 <b>Buyurtmani tasdiqlash</b>\n\n"
        f"• <b>Xizmat:</b> {data['service_name']}\n"
        f"• <b>Havola:</b> <code>{data['target_link']}</code>\n"
        f"• <b>Miqdor:</b> {quantity:,} ta\n"
        f"• <b>To'lov summasi:</b> <b>{format_uzs(total_price)}</b>\n"
        f"• <b>Sizning balansingiz:</b> <b>{format_uzs(user_balance)}</b>\n\n"
    )

    if user_balance < total_price:
        summary += "⚠️ <b>Hisobingizda mablag' yetarli emas!</b>\nIltimos, avval hisobingizni to'ldiring."
        await state.clear()
        await message.answer(summary, reply_markup=get_main_menu(), parse_mode="HTML")
        return

    summary += "Buyurtmani tasdiqlaysizmi?"
    await state.set_state(OrderStates.waiting_for_confirm)
    await message.answer(summary, reply_markup=get_order_confirm_keyboard(data["service_id"]), parse_mode="HTML")

@router.callback_query(OrderStates.waiting_for_confirm, F.data == "confirm_order")
async def process_confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    user = await get_user(user_id)

    total_price = data.get("total_price", 0.0)
    if not user or user["balance"] < total_price:
        await callback.answer("⚠️ Balansingizda yetarli mablag' mavjud emas!", show_alert=True)
        await state.clear()
        await callback.message.delete()
        await callback.message.answer("⚠️ Balansingizda mablag' yetarli emas.", reply_markup=get_main_menu())
        return

    # Balansdan yechish
    await record_user_order(user_id, total_price)

    service_id = data["service_id"]
    service_name = data["service_name"]
    target_link = data["target_link"]
    quantity = data["quantity"]
    provider_service_id = data.get("provider_service_id", 0)

    # SMM Provider API orqali yuborishni tekshirish
    api_url = await get_setting("provider_api_url", "")
    api_key = await get_setting("provider_api_key", "")
    provider_order_id = None

    if api_url and api_key and provider_service_id and provider_service_id > 0:
        api_res = await SMMProviderAPI.add_order(
            api_url=api_url,
            api_key=api_key,
            service_id=provider_service_id,
            link=target_link,
            quantity=quantity
        )
        if isinstance(api_res, dict) and "order" in api_res:
            provider_order_id = str(api_res["order"])

    # Bazaga yozish
    order_id = await create_order(
        user_id=user_id,
        service_id=service_id,
        service_name=service_name,
        target_link=target_link,
        quantity=quantity,
        total_price=total_price,
        provider_order_id=provider_order_id
    )

    await state.clear()
    await callback.message.delete()

    order_status = "⚡ Bajarilmoqda" if provider_order_id else "⏳ Kutilmoqda"

    success_msg = (
        f"✅ <b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"🆔 <b>Buyurtma ID:</b> #{order_id}\n"
        f"📌 <b>Xizmat:</b> {service_name}\n"
        f"🔗 <b>Havola:</b> <code>{target_link}</code>\n"
        f"🔢 <b>Miqdor:</b> {quantity:,} ta\n"
        f"💵 <b>To'landi:</b> {format_uzs(total_price)}\n"
        f"📊 <b>Holati:</b> {order_status}\n\n"
        f"Buyurtmangiz tez orada to'liq bajariladi. Holatni '📋 Buyurtmalarim' bo'limida kuzatishingiz mumkin."
    )
    await callback.message.answer(success_msg, reply_markup=get_main_menu(), parse_mode="HTML")

    # Adminga yangi buyurtma xabarini yetkazish
    admin_alert = (
        f"🔔 <b>YANGI BUYURTMA #{order_id}</b>\n\n"
        f"👤 Foydalanuvchi: <a href='tg://user?id={user_id}'>{callback.from_user.full_name}</a> (ID: {user_id})\n"
        f"📌 Xizmat: {service_name}\n"
        f"🔗 Havola: <code>{target_link}</code>\n"
        f"🔢 Miqdor: {quantity:,} ta\n"
        f"💵 Summa: {format_uzs(total_price)}\n"
        f"🌐 Provider ID: {provider_order_id or 'Qo‘lda bajarish rejimida'}"
    )
    admin_ids = await get_admin_ids()
    for admin_id in admin_ids:
        try:
            await callback.bot.send_message(admin_id, admin_alert, parse_mode="HTML")
        except Exception:
            pass

@router.callback_query(F.data == "cancel_order")
async def process_cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Buyurtma bekor qilindi.", reply_markup=get_main_menu())
    await callback.answer()
