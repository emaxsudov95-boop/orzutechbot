def format_uzs(amount: float) -> str:
    """Raqamni 8 500 so'm ko'rinishida formatlash"""
    try:
        val = int(amount) if amount == int(amount) else round(amount, 2)
        return f"{val:,}".replace(",", " ") + " so'm"
    except Exception:
        return f"{amount} so'm"

def format_status(status: str) -> str:
    """Statusni o'zbekcha chiroyli ko'rinishga keltirish"""
    s = (status or "").upper()
    if s in ["PENDING", "KUTILMOQDA"]:
        return "⏳ Kutilmoqda"
    elif s in ["PROCESSING", "IN_PROGRESS", "BAJARILMOQDA"]:
        return "⚡ Bajarilmoqda"
    elif s in ["COMPLETED", "BAJARILDI"]:
        return "✅ Bajarildi"
    elif s in ["CANCELED", "CANCELLED", "BEKOR QILINDI"]:
        return "❌ Bekor qilindi"
    elif s in ["REFUNDED", "QAYTARILDI"]:
        return "🔄 Balansga qaytarildi"
    return f"ℹ️ {status}"
