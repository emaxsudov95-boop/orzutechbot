# 🚀 Telegram SMM Bot (@smm_kerakmibot)

Professional darajadagi zamonaviy **Telegram SMM Bot** (@PixelSmmUzBot analogi). Ushbu bot orqali foydalanuvchilar Telegram, Instagram, TikTok, YouTube ijtimoiy tarmoqlariga obunachi, layk, ko'rishlar (nakrutka) hamda rasmiy **Telegram Stars** sotib olishlari mumkin.

Bot to'liq **Aiogram 3**, **SQLite (aiosqlite)**, **SMM Provider API (v2 API)** va **Render.com** qo'llab-quvvatlashi bilan yozilgan.

---

## 🌟 Asosiy Imkoniyatlar

1. **📱 Ijtimoiy Tarmoqlar Katalogi**:
   - **Telegram**:
     - 👥 Kafolatli obunachilar (30 kunlik kafolat) — **8 500 so'm / 1 000 ta**
     - 👤 Kafolatsiz tezkor obunachilar — **4 500 so'm / 1 000 ta**
     - 👁 Post ko'rishlar (eng tezkor) — **400 so'm / 1 000 ta**
     - ❤️ Reaksiyalar (Aralash/Tanlangan) — **600 so'm / 1 000 ta**
     - 🗳 Ovozlar (So'rovnoma) — **3 000 so'm / 1 000 ta**
   - **Instagram**:
     - 👥 Kafolatli obunachilar — **9 000 so'm / 1 000 ta**
     - 👤 Kafolatsiz tezkor obunachilar — **5 000 so'm / 1 000 ta**
     - ❤️ Sifatli layklar — **2 500 so'm / 1 000 ta**
     - 👁 Reels / Video ko'rishlar — **800 so'm / 1 000 ta**
     - 🔖 Saqlash va ulashishlar — **1 500 so'm / 1 000 ta**
   - **TikTok**:
     - 👥 Obunachilar — **12 000 so'm / 1 000 ta**
     - ❤️ Layklar — **3 000 so'm / 1 000 ta**
     - 👁 Video ko'rishlar — **600 so'm / 1 000 ta**
     - ↗️ Ulashishlar (Shares) — **1 500 so'm / 1 000 ta**
   - **YouTube**:
     - 👥 Obunachilar (Kafolatli) — **25 000 so'm / 1 000 ta**
     - 👁 Ko'rishlar (Organik) — **12 000 so'm / 1 000 ta**
     - ❤️ Layklar — **5 000 so'm / 1 000 ta**
     - ⚡ Shorts ko'rishlar — **4 000 so'm / 1 000 ta**
   - **⭐ Telegram Stars**:
     - 🌟 50 Stars — **12 000 so'm**
     - 🌟 100 Stars — **23 000 so'm**
     - 🌟 250 Stars — **55 000 so'm**
     - 🌟 500 Stars — **105 000 so'm**
     - 🌟 1 000 Stars — **200 000 so'm**

2. **💰 To'lov Tizimi**:
   - 💳 **Karta orqali** (Uzcard / Humo / Payme / Click): foydalanuvchi to'lov qilib chekni yuboradi, admin tugma orqali tasdiqlaydi.
   - ⭐ **Telegram Stars to'lovi**: Telegram ichidagi rasmiy Stars valyutasi (`XTR`) orqali to'lov 1 soniyada avtomatik balansa qo'shiladi!

3. **🌐 SMM Provayder API Integratsiyasi (Standard v2 API)**:
   - Mediasmm, JustSMM, Peakerr, JAP va boshqa barcha standart SMM panellari bilan mos keladi.
   - Bot ichidagi admin panelidan API URL va API Key kiritilishi bilanoq, buyurtmalar avtomatik ravishda provayderga uzatiladi.
   - Provayder hisobidagi qoldiq mablag'ni (balance) to'g'ridan-to'g'ri bot ichida tekshirish mumkin.

4. **👑 Keng Qamrovli Admin Panel**:
   - 📊 **Statistika**: Jami foydalanuvchilar, bugungi yangilar, jami buyurtmalar, umumiy tushum.
   - 💰 **Balans boshqaruvi**: Foydalanuvchi ID si bo'yicha balans qo'shish yoki yechib olish.
   - 📢 **Xabar tarqatish (Broadcast)**: Barcha foydalanuvchilarga xabar (matn, rasm, video) yuborish.
   - 💵 **Narxlarni o'zgartirish**: Botni to'xtatmasdan xizmatlar narxi va provayder ID sini o'zgartirish.
   - 💳 **To'lov rekvizitlari**: Karta raqami va karta egasini o'zgartirish.

5. **👥 Referal Dasturi**:
   - Har bir foydalanuvchining o'z shaxsiy referal havolasi bo'ladi.
   - Taklif etilgan do'sti hisobini to'ldirganda **5% naqd bonus** avtomatik hisobiga tushadi.

---

## 🛠 O'rnatish va Ishga Tushirish

### 1. Lokal kompyuterda ishga tushirish:

1. Kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

2. `.env` faylida o'z ma'lumotlaringizni tekshiring:
```env
BOT_TOKEN=8020362562:AAHRf8gPyDu7U5R1aXl2zDCe0lUxwy3OOao
ADMIN_IDS=SIZNING_TELEGRAM_ID
PROVIDER_API_URL=
PROVIDER_API_KEY=
DEFAULT_CARD_NUMBER=8600 0000 0000 0000
DEFAULT_CARD_HOLDER=SMM BOT ADMIN
SUPPORT_USERNAME=admin
PORT=8080
```
> *(Eslatma: Agar `ADMIN_IDS` ga o'z ID raqamingizni yozmasangiz ham, botga birinchi kirib `/admin` deb yozganingizda bot sizni avtomatik Bosh Admin qilib belgilaydi).*

3. Botni ishga tushiring:
```bash
python bot.py
```

---

## ☁️ Render.com ga Deploy Qilish (Qadamma-Qadam)

Bot Render.com da bepul 24/7 ishlashi uchun to'liq moslashtirilgan (ichida portni ushlab turuvchi maxsus Health-Check serveri mavjud).

### 1-qadam: GitHub ga yuklash
1. [GitHub.com](https://github.com) ga kiring va yangi repository oching (masalan, `smm-bot`).
2. Ushbu papkadagi fayllarni o'sha repo ga yuklang (push qiling).

### 2-qadam: Render.com da sozlash
1. [Render.com](https://render.com) ga kiring va ro'yxatdan o'ting / kiring.
2. Bosh sahifada **"New +"** tugmasini bosing va **"Web Service"** ni tanlang.
3. O'zingizning GitHub repositoryingizni tanlang (`smm-bot`).
4. Quyidagi parametrlarni kiriting:
   - **Name:** `smm-bot` (yoki ixtiyoriy nom)
   - **Region:** `Frankfurt (EU Central)`
   - **Branch:** `main` yoki `master`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
   - **Instance Type:** `Free`

### 3-qadam: Muhit o'zgaruvchilari (Environment Variables)
Sahifaning pastki qismidagi **"Environment Variables"** bo'limida quyidagilarni qo'shing:
- `BOT_TOKEN` = `8020362562:AAHRf8gPyDu7U5R1aXl2zDCe0lUxwy3OOao`
- `ADMIN_IDS` = `Sizning_Telegram_ID_Raqamingiz` (masalan: `123456789`)
- `PORT` = `8080`
- `PROVIDER_API_URL` = *(agar provayderingiz bo'lsa, masalan: `https://justsmm.com/api/v2`)*
- `PROVIDER_API_KEY` = *(provayder API kalitingiz)*

### 4-qadam: "Create Web Service"
**"Create Web Service"** tugmasini bosing. Render loyihani avtomatik yig'adi va bot 2-3 daqiqada 24/7 rejimida to'liq ishga tushadi!

---

## 📂 Loyiha Tuzilishi

```
├── bot.py                  # Asosiy ishga tushirish fayli va Render HTTP serveri
├── config.py               # Konfiguratsiya va muhit o'zgaruvchilari
├── database.py             # Asinxron SQLite bazasi (aiosqlite)
├── smm_api.py              # SMM Provider v2 API mijozi
├── requirements.txt        # Kerakli kutubxonalar ro'yxati
├── Dockerfile              # Docker konteyner fayli
├── render.yaml             # Render Blueprint konfiguratsiyasi
├── Procfile                # Render start konfiguratsiyasi
├── .env                    # Maxfiy ma'lumotlar fayli
├── handlers/               # Bot buyruqlari va jarayonlari
│   ├── start.py            # /start, referal va menyu
│   ├── services.py         # Nakrutka xizmatlari va buyurtma berish
│   ├── balance.py          # Karta va Telegram Stars to'lovlari
│   ├── profile.py          # Foydalanuvchi kabineti va buyurtmalar tarixi
│   ├── help.py             # Yordam va qoidalar
│   └── admin.py            # To'liq admin panel
├── keyboards/              # Klaviaturaguruhlari
│   ├── reply.py            # Asosiy menyu klaviaturalari
│   └── inline.py           # Inline xizmatlar, toifalar va to'lov tugmalari
└── utils/                  # Qo'shimcha yordamchilar
    ├── states.py           # FSM holatlari
    └── formatters.py       # Narx va statuslarni formatlash
```
