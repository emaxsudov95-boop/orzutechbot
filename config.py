import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin IDs (vergul bilan ajratilgan ID lar, masalan: 12345678,87654321)
ADMINS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMINS_RAW.split(",") if x.strip().isdigit()]

# Standart SMM Provayder API sozlamalari (Standard v2 API)
PROVIDER_API_URL = os.getenv("PROVIDER_API_URL", "")
PROVIDER_API_KEY = os.getenv("PROVIDER_API_KEY", "")

# To'lov kartalari rekvizitlari
CARD_1_NUMBER = os.getenv("CARD_1_NUMBER", "4916 9903 2289 2321")
CARD_1_NAME = os.getenv("CARD_1_NAME", "Visa (Uzum Bank)")

CARD_2_NUMBER = os.getenv("CARD_2_NUMBER", "4790 7400 0008 4837")
CARD_2_NAME = os.getenv("CARD_2_NAME", "Visa (Kapitalbank)")

DEFAULT_CARD_NUMBER = CARD_1_NUMBER
DEFAULT_CARD_HOLDER = os.getenv("DEFAULT_CARD_HOLDER", "")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "admin")

# 1 Telegram Stars ning so'mdagi qiymati (Balans to'ldirish uchun)
STAR_RATE_UZS = int(os.getenv("STAR_RATE_UZS", "250"))

# Referal foizi (Taklif qilingan do'st hisobini to'ldirganda beriladigan bonus %)
REFERRAL_PERCENT = int(os.getenv("REFERRAL_PERCENT", "5"))

# Port (Render.com web service uchun)
PORT = int(os.getenv("PORT", "8080"))

# Database fayl yo'li
DB_PATH = os.getenv("DB_PATH", "smm_bot.db")
