import aiosqlite
import logging
from datetime import datetime
from config import (
    DB_PATH,
    DEFAULT_CARD_NUMBER,
    DEFAULT_CARD_HOLDER,
    CARD_1_NUMBER,
    CARD_1_NAME,
    CARD_2_NUMBER,
    CARD_2_NAME,
    CARD_3_NUMBER,
    CARD_3_NAME,
    ADMIN_IDS,
    SUPPORT_USERNAME,
    PROVIDER_API_URL,
    PROVIDER_API_KEY
)

logger = logging.getLogger(__name__)

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # 1. Users jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance REAL DEFAULT 0.0,
                spent REAL DEFAULT 0.0,
                orders_count INTEGER DEFAULT 0,
                referrer_id INTEGER,
                referral_earnings REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_banned INTEGER DEFAULT 0
            )
        """)

        # 2. Services (Xizmatlar) jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                name TEXT,
                price_per_1000 REAL,
                min_amount INTEGER,
                max_amount INTEGER,
                description TEXT,
                provider_service_id INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            )
        """)

        # 3. Orders (Buyurtmalar) jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_id INTEGER,
                service_name TEXT,
                target_link TEXT,
                quantity INTEGER,
                total_price REAL,
                provider_order_id TEXT DEFAULT NULL,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Payments (To'lovlar) jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                method TEXT,
                receipt_photo_id TEXT DEFAULT NULL,
                status TEXT DEFAULT 'PENDING',
                stars_charge_id TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 5. Settings (Sozlamalar) jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        await db.commit()

        # Standart xizmatlar borligini tekshirish va to'ldirish
        cursor = await db.execute("SELECT COUNT(*) as count FROM services")
        row = await cursor.fetchone()
        if row["count"] == 0:
            default_services = [
                # TELEGRAM
                ("telegram", "👥 Telegram Obunachi (Kafolatli 30 kun)", 8500.0, 50, 50000, "Yuqori sifatli, 30 kunlik to'liq kafolatli faol obunachilar. Chiqib ketish ehtimoli minimal.", 1),
                ("telegram", "👤 Telegram Obunachi (Kafolatsiz tezkor)", 4500.0, 50, 50000, "Tezkor tushadigan arzon obunachilar. Kanal va guruhlar uchun mos.", 2),
                ("telegram", "👁 Telegram Ko'rishlar (So'nggi post)", 400.0, 100, 100000, "Kanal postingizga tezkor va real ko'rishlar oqimi.", 3),
                ("telegram", "❤️ Telegram Reaksiyalar (Aralash/Tanlangan)", 600.0, 50, 50000, "Postlarga pozitiv reaksiyalar (👍, ❤️, 🔥, 🎉, 👏).", 4),
                ("telegram", "🗳 Telegram Ovozlar (So'rovnoma)", 3000.0, 50, 20000, "Kanal so'rovnomalarida tanlangan javobga ovoz berish.", 5),

                # INSTAGRAM
                ("instagram", "👥 Instagram Obunachi (Kafolatli 30 kun)", 9000.0, 50, 50000, "Avto-qayta to'ldirish (Auto-Refill) kafolatli obunachilar.", 10),
                ("instagram", "👤 Instagram Obunachi (Kafolatsiz tezkor)", 5000.0, 50, 50000, "Tezkor va arzon obunachilar. Profil ko'rinishini oshirish uchun.", 11),
                ("instagram", "❤️ Instagram Layklar (Sifatli tezkor)", 2500.0, 50, 50000, "Post va reelslar uchun tezkor layklar.", 12),
                ("instagram", "👁 Instagram Reels Ko'rishlar", 800.0, 100, 100000, "Reels videolar uchun tavsiya (rekomendatsiya) ko'rishlari.", 13),
                ("instagram", "🔖 Instagram Saqlash va Ulashishlar", 1500.0, 50, 50000, "Post algoritmini faollashtirish uchun saqlashlar.", 14),

                # TIKTOK
                ("tiktok", "👥 TikTok Obunachi", 12000.0, 50, 30000, "TikTok profilingiz uchun sifatli obunachilar.", 20),
                ("tiktok", "❤️ TikTok Layklar", 3000.0, 50, 50000, "Videolaringizga tezkor layklar oqimi.", 21),
                ("tiktok", "👁 TikTok Ko'rishlar (Tezkor)", 600.0, 100, 200000, "Videolarni trendga chiqarish uchun ko'rishlar.", 22),
                ("tiktok", "↗️ TikTok Ulashishlar (Shares)", 1500.0, 50, 50000, "Algoritmga video mashhurligini oshirib beradi.", 23),

                # YOUTUBE
                ("youtube", "👥 YouTube Obunachi (Kafolatli)", 25000.0, 50, 10000, "Monetizatsiya va kanal rivojlantirish uchun kafolatli obunachilar.", 30),
                ("youtube", "👁 YouTube Video Ko'rishlar", 12000.0, 100, 50000, "Yuqori ushlab turish ko'rsatkichi (Retention) bilan ko'rishlar.", 31),
                ("youtube", "❤️ YouTube Layklar", 5000.0, 50, 20000, "Videolarga layklar.", 32),
                ("youtube", "⚡ YouTube Shorts Ko'rishlar", 4000.0, 100, 100000, "Shorts videolarga tezkor ko'rishlar.", 33),

                # TELEGRAM STARS (Paketlar - narx 1000 ta uchun emas, to'liq paket narxi)
                ("stars", "🌟 50 Telegram Stars", 12000.0, 1, 1, "Kanal va botlar uchun 50 ta rasmiy Telegram Stars.", 40),
                ("stars", "🌟 100 Telegram Stars", 23000.0, 1, 1, "Kanal va botlar uchun 100 ta rasmiy Telegram Stars.", 41),
                ("stars", "🌟 250 Telegram Stars", 55000.0, 1, 1, "Kanal va botlar uchun 250 ta rasmiy Telegram Stars.", 42),
                ("stars", "🌟 500 Telegram Stars", 105000.0, 1, 1, "Kanal va botlar uchun 500 ta rasmiy Telegram Stars.", 43),
                ("stars", "🌟 1000 Telegram Stars", 200000.0, 1, 1, "Kanal va botlar uchun 1000 ta rasmiy Telegram Stars.", 44),
            ]

            await db.executemany("""
                INSERT INTO services (category, name, price_per_1000, min_amount, max_amount, description, provider_service_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, default_services)
            await db.commit()

        # Standart sozlamalar
        default_settings = [
            ("card_number", DEFAULT_CARD_NUMBER),
            ("card_holder", DEFAULT_CARD_HOLDER),
            ("card_1_number", CARD_1_NUMBER),
            ("card_1_name", CARD_1_NAME),
            ("card_2_number", CARD_2_NUMBER),
            ("card_2_name", CARD_2_NAME),
            ("card_3_number", CARD_3_NUMBER),
            ("card_3_name", CARD_3_NAME),
            ("support_username", SUPPORT_USERNAME),
            ("provider_api_url", PROVIDER_API_URL),
            ("provider_api_key", PROVIDER_API_KEY),
            ("min_deposit", "5000"),
        ]
        for key, val in default_settings:
            await db.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            """, (key, val))
        # Asosiy kartani yangilash
        await db.execute("UPDATE settings SET value = ? WHERE key = 'card_1_number'", (CARD_1_NUMBER,))
        await db.execute("UPDATE settings SET value = ? WHERE key = 'card_1_name'", (CARD_1_NAME,))
        await db.execute("UPDATE settings SET value = ? WHERE key = 'card_number'", (CARD_1_NUMBER,))
        await db.commit()
    logger.info("Database muvaffaqiyatli ishga tushirildi.")

# ==================== FOYDALANUVCHILAR ====================

async def get_or_create_user(user_id: int, username: str = None, full_name: str = None, referrer_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = await cursor.fetchone()

        if user:
            # Username va ismni yangilab qo'yamiz
            await db.execute("""
                UPDATE users SET username = ?, full_name = ? WHERE user_id = ?
            """, (username, full_name, user_id))
            await db.commit()
            cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return dict(await cursor.fetchone())

        # Yangi foydalanuvchi
        # O'zini o'zi taklif qilolmaydi
        valid_ref = None
        if referrer_id and referrer_id != user_id:
            ref_cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (referrer_id,))
            if await ref_cur.fetchone():
                valid_ref = referrer_id

        await db.execute("""
            INSERT INTO users (user_id, username, full_name, referrer_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, full_name, valid_ref))
        await db.commit()

        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return dict(await cursor.fetchone())

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def update_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET balance = balance + ? WHERE user_id = ?
        """, (amount, user_id))
        await db.commit()

async def record_user_order(user_id: int, spent_amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET balance = balance - ?,
                spent = spent + ?,
                orders_count = orders_count + 1
            WHERE user_id = ?
        """, (spent_amount, spent_amount, user_id))
        await db.commit()

async def add_referral_earnings(referrer_id: int, earning: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users 
            SET balance = balance + ?,
                referral_earnings = referral_earnings + ?
            WHERE user_id = ?
        """, (earning, earning, referrer_id))
        await db.commit()

async def get_referral_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE referrer_id = ?", (user_id,))
        row = await cursor.fetchone()
        count = row["count"] if row else 0

        user = await get_user(user_id)
        earnings = user["referral_earnings"] if user else 0.0
        return count, earnings

async def get_all_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT COUNT(*) as count FROM users")
        row = await cursor.fetchone()
        return row["count"] if row else 0

async def get_today_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE date(created_at) = date('now')")
        row = await cursor.fetchone()
        return row["count"] if row else 0

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [row["user_id"] for row in rows]

# ==================== XIZMATLAR ====================

async def get_services_by_category(category: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM services WHERE category = ? AND is_active = 1", (category,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

async def get_all_services():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM services ORDER BY category, id")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

async def get_service(service_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def update_service_price(service_id: int, new_price: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE services SET price_per_1000 = ? WHERE id = ?", (new_price, service_id))
        await db.commit()

async def update_service_provider_id(service_id: int, provider_service_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE services SET provider_service_id = ? WHERE id = ?", (provider_service_id, service_id))
        await db.commit()

# ==================== BUYURTMALAR ====================

async def create_order(user_id: int, service_id: int, service_name: str, target_link: str, quantity: int, total_price: float, provider_order_id: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO orders (user_id, service_id, service_name, target_link, quantity, total_price, provider_order_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, service_id, service_name, target_link, quantity, total_price, provider_order_id, 'PROCESSING' if provider_order_id else 'PENDING'))
        await db.commit()
        return cursor.lastrowid

async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def update_order_status(order_id: int, status: str, provider_order_id: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if provider_order_id:
            await db.execute("UPDATE orders SET status = ?, provider_order_id = ? WHERE id = ?", (status, provider_order_id, order_id))
        else:
            await db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        await db.commit()

async def get_user_orders(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

async def get_all_orders_count():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT COUNT(*) as count FROM orders")
        row = await cursor.fetchone()
        return row["count"] if row else 0

async def get_total_spent():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT SUM(total_price) as total FROM orders")
        row = await cursor.fetchone()
        return row["total"] if row and row["total"] else 0.0

# ==================== TO'LOVLAR ====================

async def create_payment(user_id: int, amount: float, method: str, receipt_photo_id: str = None, stars_charge_id: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        status = 'APPROVED' if method == 'STARS' else 'PENDING'
        cursor = await db.execute("""
            INSERT INTO payments (user_id, amount, method, receipt_photo_id, stars_charge_id, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, amount, method, receipt_photo_id, stars_charge_id, status))
        await db.commit()
        return cursor.lastrowid

async def get_payment(payment_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def update_payment_status(payment_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE payments SET status = ? WHERE id = ?", (status, payment_id))
        await db.commit()

# ==================== SOZLAMALAR ====================

async def get_setting(key: str, default: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row["value"] if row else default

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        await db.commit()

# ==================== ADMINLAR ====================

async def get_admin_ids() -> list[int]:
    admins = set(ADMIN_IDS)
    admin_id_setting = await get_setting("admin_id", "")
    if admin_id_setting:
        for x in admin_id_setting.split(","):
            if x.strip().isdigit():
                admins.add(int(x.strip()))
    return list(admins)

async def is_admin(user_id: int) -> bool:
    admin_ids = await get_admin_ids()
    return user_id in admin_ids

