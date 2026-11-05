from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user, get_user_orders, get_referral_stats, update_order_status, get_setting
from smm_api import SMMProviderAPI
from utils.formatters import format_uzs, format_status

router = Router()

@router.message(F.text == "👤 Kabinet")
async def show_profile(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await message.answer("Foydalanuvchi ma'lumotlari topilmadi. Qaytadan /start bosing.")
        return

    ref_count, ref_earnings = await get_referral_stats(user_id)

    text = (
        f"👤 <b>Sizning Shaxsiy Kabinetingiz</b>\n\n"
        f"🆔 <b>ID raqamingiz:</b> <code>{user_id}</code>\n"
        f"👤 <b>Ism:</b> {user['full_name'] or 'Noma`lum'}\n"
        f"🌐 <b>Username:</b> @{user['username'] if user['username'] else 'mavjud emas'}\n\n"
        f"💰 <b>Asosiy balans:</b> <b>{format_uzs(user['balance'])}</b>\n"
        f"🛒 <b>Jami buyurtmalar:</b> {user['orders_count']} ta\n"
        f"💳 <b>Sarflangan mablag':</b> {format_uzs(user['spent'])}\n\n"
        f"👥 <b>Taklif qilingan do'stlar:</b> {ref_count} ta\n"
        f"🎁 <b>Referal daromadi:</b> {format_uzs(ref_earnings)}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Balans to'ldirish", callback_data="pay_card"),
            InlineKeyboardButton(text="📋 Buyurtmalarim", callback_data="my_orders")
        ]
    ])

    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.message(F.text == "📋 Buyurtmalarim")
@router.callback_query(F.data == "my_orders")
async def show_my_orders(event: Message | CallbackQuery):
    user_id = event.from_user.id
    orders = await get_user_orders(user_id, limit=8)

    if not orders:
        empty_text = (
            "📋 <b>Sizning buyurtmalaringiz:</b>\n\n"
            "Siz hali birorta ham xizmatga buyurtma bermagansiz.\n"
            "Buyurtma berish uchun <b>🚀 Xizmatlar</b> bo'limiga kiring!"
        )
        if isinstance(event, CallbackQuery):
            await event.message.answer(empty_text, parse_mode="HTML")
            await event.answer()
        else:
            await event.answer(empty_text, parse_mode="HTML")
        return

    # SMM Provider orqali statuslarni jonli yangilash
    api_url = await get_setting("provider_api_url", "")
    api_key = await get_setting("provider_api_key", "")

    lines = ["📋 <b>Oxirgi buyurtmalaringiz ro'yxati:</b>\n"]
    for o in orders:
        status = o["status"]

        # Agar provider_order_id bo'lsa va hali yakunlanmagan bo'lsa, statusini tekshirish
        if api_url and api_key and o["provider_order_id"] and status in ["PENDING", "PROCESSING"]:
            try:
                st_res = await SMMProviderAPI.get_order_status(api_url, api_key, o["provider_order_id"])
                if isinstance(st_res, dict) and "status" in st_res:
                    provider_st = st_res["status"].upper()
                    if provider_st in ["COMPLETED", "FINISHED"]:
                        status = "COMPLETED"
                        await update_order_status(o["id"], "COMPLETED")
                    elif provider_st in ["CANCELED", "CANCELLED"]:
                        status = "CANCELED"
                        await update_order_status(o["id"], "CANCELED")
            except Exception:
                pass

        lines.append(
            f"🔹 <b>Buyurtma #{o['id']}</b>\n"
            f"📌 {o['service_name']}\n"
            f"🔗 <code>{o['target_link']}</code>\n"
            f"🔢 Miqdor: <b>{o['quantity']:,}</b> | Narx: <b>{format_uzs(o['total_price'])}</b>\n"
            f"📊 Holati: <b>{format_status(status)}</b>\n"
            f"🕒 Sana: {str(o['created_at'])[:16]}\n"
        )

    text = "\n".join(lines)
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML")
