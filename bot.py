# bot.py
import os
import json
import logging
import random
import string
import tempfile
import requests
import urllib.parse
from typing import Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ---------------- Configuration ----------------
# Prefer environment variables for security; fallback to values below only if env not set.
TOKEN = os.environ.get("8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g") or "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g"
ADMIN_ID = int(os.environ.get("7633561058") or 7633561058)

# DATA_DIR: Railway friendly writable location
DATA_DIR = os.environ.get("DATA_DIR", "/tmp/botdata")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "data.json")

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- Default data ----------------
default_data = {
    "users": {},
    "coupons": {
        "today": {
            "date": "",
            "matches": [],
            "description": "🎯 Bugungi Ishonchli Kuponlar",
            "active": True,
            "coupon_codes": {"1xbet": "", "melbet": "", "dbbet": ""},
        },
        "premium": {
            "date": "",
            "matches": [],
            "description": "💎 Premium Ekskluziv Kuponlar",
            "active": True,
            "coupon_codes": {"1xbet": "", "melbet": "", "dbbet": ""},
        },
    },
    "settings": {
        "min_referrals": 10,
        "premium_price": 100,
        "currency": "so'm",
        "payment_details": "💳 *To'lov qilish uchun:*\n\n🏦 **Click:** `1234 5678 9012 3456`\n📱 **Payme:** `+998901234567`\n💳 **Uzumbank:** `8600 1234 5678 9012`\n\n✅ To'lov qilgach, chek skrinshotini @admin ga yuboring.",
    },
    "stats": {"total_users": 0, "premium_users": 0},
}


# ---------------- Data load/save (atomic) ----------------
def load_data() -> Dict[str, Any]:
    try:
        if not os.path.exists(DATA_FILE):
            logger.info("Data file not found. Creating new one at %s", DATA_FILE)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            return json.loads(json.dumps(default_data))
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.exception("JSON decode error for data file. Recreating from default.")
        try:
            with open(DATA_FILE + ".bak", "w", encoding="utf-8") as bak:
                with open(DATA_FILE, "r", encoding="utf-8") as orig:
                    bak.write(orig.read())
        except Exception:
            logger.exception("Failed to backup corrupted data file.")
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return json.loads(json.dumps(default_data))
    except Exception:
        logger.exception("Unexpected error loading data file.")
        raise


def save_data(data: Dict[str, Any]) -> bool:
    try:
        dirpath = os.path.dirname(os.path.abspath(DATA_FILE)) or "."
        fd, tmp_path = tempfile.mkstemp(dir=dirpath)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, DATA_FILE)
        return True
    except Exception:
        logger.exception("Failed to save data atomically.")
        return False


# ---------------- Globals ----------------
data = load_data()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def is_premium(user_id: int) -> bool:
    return data.get("users", {}).get(str(user_id), {}).get("premium", False)


def get_user_referrals(user_id: int) -> int:
    return data.get("users", {}).get(str(user_id), {}).get("referrals", 0)


def generate_coupon_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


# ---------------- Bookmaker URL helper ----------------
def bookmaker_url(bookmaker: str, code: str) -> str:
    code = (code or "").strip()
    if bookmaker == "1xbet":
        base = "https://1xbet.com"
    elif bookmaker == "melbet":
        base = "https://melbet.com"
    elif bookmaker == "dbbet":
        base = "https://dbbet.com"
    else:
        base = "https://www.google.com"

    if code:
        # Simple promo param addition; adjust to real affiliate URLs if you have them
        return f"{base}/?promo={urllib.parse.quote_plus(code)}"
    return base


# ---------------- Telegram handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None:
        return
    user_id = user.id

    # Yangi foydalanuvchi
    if str(user_id) not in data["users"]:
        data["users"][str(user_id)] = {"name": user.first_name or "", "referrals": 0, "premium": False}
        data["stats"]["total_users"] = sum(1 for _ in data["users"])
        save_data(data)

    # Referal tekshirish
    if context.args:
        ref_id = context.args[0]
        if isinstance(ref_id, str) and ref_id.startswith("ref"):
            try:
                referrer_id = int(ref_id[3:])
                if str(referrer_id) in data["users"] and referrer_id != user_id:
                    data["users"][str(referrer_id)]["referrals"] = data["users"][str(referrer_id)].get("referrals", 0) + 1
                    save_data(data)
            except Exception:
                logger.exception("Failed to parse referral id: %s", ref_id)

    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons"),
         InlineKeyboardButton("💎 Premium Kuponlar", callback_data="premium_coupons")],
        [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link"),
         InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")],
        [InlineKeyboardButton("💳 Premium Sotib Olish", callback_data="buy_premium"),
         InlineKeyboardButton("ℹ️ Yordam", callback_data="help")],
    ]
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"🎉 *Salom {user.first_name or ''}!* 👋\n\n"
        "⚽ *Futbol Kuponlari Botiga Xush Kelibsiz!*\n\n"
        "📊 *Har kuni yangilanadigan ishonchli kuponlar:*\n"
        "• ⚽ **Kunlik bepul kuponlar**\n"
        "• 💎 **Premium ekskluziv bashoratlar** \n"
        "• 📈 **Yuqori daromadli stavkalar**\n\n"
        "🎯 *Bizning afzalliklarimiz:*\n"
        "✅ Kunlik yangilanish\n✅ 85-95% ishonchlilik\n✅ Professional tahlillar\n✅ Tez natijalar\n\n"
        "💰 *Premium imkoniyatlari:*\n• 10 ta referal yoki 100 so'm\n• Ekskluziv kuponlar\n• Statistik tahlillar\n• Shaxsiy qo'llab-quvvatlash\n\n"
        "*Botdan to'liq foydalanish uchun quyidagi tugmalardan foydalaning!* 🚀"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")


async def send_today_coupons(query):
    today_coupons = data["coupons"]["today"]

    if not today_coupons["active"] or not today_coupons["matches"]:
        await query.edit_message_text(
            "📭 *Hozircha kuponlar mavjud emas*\n\nKuponlar tez orada yangilanadi. Iltimos, keyinroq tekshiring! 🔄",
            parse_mode="Markdown",
        )
        return

    coupon_text = f"🎯 *{today_coupons['description']}*\n\n"
    coupon_text += f"📅 **Sana:** {today_coupons['date']}\n\n"
    coupon_text += "🔑 *Kupon Kodlari:*\n"
    coupon_text += f"• 1xBet: `{today_coupons['coupon_codes'].get('1xbet', 'Kod mavjud emas')}`\n"
    coupon_text += f"• MelBet: `{today_coupons['coupon_codes'].get('melbet', 'Kod mavjud emas')}`\n"
    coupon_text += f"• DB Bet: `{today_coupons['coupon_codes'].get('dbbet', 'Kod mavjud emas')}`\n\n"
    coupon_text += "---\n\n"

    total_odds = 1.0
    for i, match in enumerate(today_coupons["matches"], 1):
        coupon_text += f"*{i}. {match.get('time', '')} - {match.get('league', '')}*\n"
        coupon_text += f"🏆 `{match.get('teams', '')}`\n"
        coupon_text += f"🎯 **Bashorat:** `{match.get('prediction', '')}`\n"
        coupon_text += f"📊 **Koeffitsient:** `{match.get('odds', '')}`\n"
        coupon_text += f"💎 **Ishonch:** {match.get('confidence', '')}\n\n"
        try:
            total_odds *= float(match.get("odds", 1.0))
        except Exception:
            pass

    coupon_text += f"💰 **Umumiy koeffitsient:** `{total_odds:.2f}` 🚀\n\n"
    coupon_text += "⏰ *Eslatma:* Stavkalarni o'yin boshlanishidan oldin qo'ying!\n"

    code_1x = today_coupons["coupon_codes"].get("1xbet", "")
    code_mel = today_coupons["coupon_codes"].get("melbet", "")
    code_db = today_coupons["coupon_codes"].get("dbbet", "")

    btn_bookmakers = [
        InlineKeyboardButton("1xBet ▸", url=bookmaker_url("1xbet", code_1x)),
        InlineKeyboardButton("MelBet ▸", url=bookmaker_url("melbet", code_mel)),
        InlineKeyboardButton("DBBet ▸", url=bookmaker_url("dbbet", code_db)),
    ]

    keyboard = [
        [InlineKeyboardButton("🔗 Do'stlarni Taklif Qilish", callback_data="share_referral")],
        btn_bookmakers,
        [InlineKeyboardButton("💎 Premium Kuponlar", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(coupon_text, reply_markup=reply_markup, parse_mode="Markdown")


async def send_premium_coupons(query):
    premium_coupons = data["coupons"]["premium"]

    if not premium_coupons["active"] or not premium_coupons["matches"]:
        await query.edit_message_text(
            "💎 *Premium kuponlar tez orada yangilanadi!*\n\nBiz yuqori daromadli ekskluziv kuponlar ustida ishlamoqdamiz. 🔄",
            parse_mode="Markdown",
        )
        return

    premium_text = f"💎 *{premium_coupons['description']}*\n\n"
    premium_text += f"📅 **Sana:** {premium_coupons['date']}\n\n"
    premium_text += "🔑 *Premium Kupon Kodlari:*\n"
    premium_text += f"• 1xBet: `{premium_coupons['coupon_codes'].get('1xbet', 'Kod mavjud emas')}`\n"
    premium_text += f"• MelBet: `{premium_coupons['coupon_codes'].get('melbet', 'Kod mavjud emas')}`\n"
    premium_text += f"• DB Bet: `{premium_coupons['coupon_codes'].get('dbbet', 'Kod mavjud emas')}`\n\n"
    premium_text += "---\n\n"

    total_odds = 1.0
    for i, match in enumerate(premium_coupons["matches"], 1):
        premium_text += f"*{i}. {match.get('time', '')} - {match.get('league', '')}*\n"
        premium_text += f"🏆 `{match.get('teams', '')}`\n"
        premium_text += f"🎯 **Bashorat:** `{match.get('prediction', '')}`\n"
        premium_text += f"📊 **Koeffitsient:** `{match.get('odds', '')}`\n"
        premium_text += f"💎 **Ishonch:** {match.get('confidence', '')}\n\n"
        try:
            total_odds *= float(match.get("odds", 1.0))
        except Exception:
            pass

    premium_text += f"💰 **Umumiy koeffitsient:** `{total_odds:.2f}` 💰\n\n"
    premium_text += "✅ *Premium a'zo bo'lganingiz uchun rahmat!*\n"

    code_1x = premium_coupons["coupon_codes"].get("1xbet", "")
    code_mel = premium_coupons["coupon_codes"].get("melbet", "")
    code_db = premium_coupons["coupon_codes"].get("dbbet", "")

    btn_bookmakers = [
        InlineKeyboardButton("1xBet ▸", url=bookmaker_url("1xbet", code_1x)),
        InlineKeyboardButton("MelBet ▸", url=bookmaker_url("melbet", code_mel)),
        InlineKeyboardButton("DBBet ▸", url=bookmaker_url("dbbet", code_db)),
    ]

    keyboard = [
        btn_bookmakers,
        [InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")],
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(premium_text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_premium_offer(query, user_id: int):
    referrals_count = get_user_referrals(user_id)
    required_refs = data["settings"]["min_referrals"]

    text = (
        "💎 *PREMIUM KUPONLARGA KIRISH*\n\n"
        f"📊 **Sizning holatingiz:**\n👥 Referallar: {referrals_count}/{required_refs} ta\n"
        f"💰 To'lov: {data['settings']['premium_price']} {data['settings']['currency']}\n\n"
        "🎯 *Premium afzalliklari:*\n• ✅ Yuqori daromadli kuponlar\n• ✅ Ekskluziv bashoratlar\n• ✅ 90-95% ishonchlilik\n• ✅ Statistik tahlillar\n• ✅ Shaxsiy qo'llab-quvvatlash\n\n"
        "💡 *Premium olish usullari:*\n"
    )

    keyboard = []
    if referrals_count >= required_refs:
        keyboard.append([InlineKeyboardButton("🎁 BEPUL PREMIUM OCHISH", callback_data="get_free_premium")])
        text += f"1. 🎁 **{required_refs} ta referal** - Bepul premium!\n"
    else:
        text += f"1. 👥 **{required_refs} ta referal** to'plang\n"

    text += f"2. 💳 **{data['settings']['premium_price']} {data['settings']['currency']}** to'lov qiling\n\n"
    text += "💎 Premium orqali yuqori daromadli kuponlarga ega bo'ling!"

    keyboard.extend(
        [
            [InlineKeyboardButton("👥 Referal Orqali", callback_data="get_referral_link")],
            [InlineKeyboardButton("💳 To'lov Orqali", callback_data="buy_premium")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back")],
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_premium_payment(query, user_id: int):
    payment_details = data["settings"]["payment_details"]
    text = (
        "💳 *PREMIUM A'ZOLIK*\n\n"
        f"💰 **Narxi:** {data['settings']['premium_price']} {data['settings']['currency']}\n\n"
        f"{payment_details}\n\n"
        "📋 *Qadamlar:*\n1. Yuqoridagi raqamlarga to'lov qiling\n2. Chek skrinshotini oling\n3. @admin ga yuboring\n4. Premium ochiladi!\n\n⏰ *Eslatma:* To'lov qilgach, tez orada premium ochiladi."
    )

    keyboard = [
        [InlineKeyboardButton("👥 Referal Orqali Olish", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔗 Do'stlarni Taklif Qilish", callback_data="share_referral")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def activate_free_premium(query, user_id: int):
    referrals_count = get_user_referrals(user_id)
    required_refs = data["settings"]["min_referrals"]

    if referrals_count >= required_refs:
        data["users"][str(user_id)]["premium"] = True
        save_data(data)
        text = (
            "🎉 *TABRIKLAYMIZ!*\n\n"
            "Siz muvaffaqiyatli Premium a'zoga aylandingiz! 🎊\n\n"
            "💎 *Endi siz quyidagi imkoniyatlarga ega bo'ldingiz:*\n"
            "• ✅ Yuqori daromadli kuponlar\n• ✅ Ekskluziv bashoratlar\n• ✅ 90-95% ishonchlilik\n• ✅ Statistik tahlillar\n• ✅ Shaxsiy qo'llab-quvvatlash\n\n🚀 Endi Premium kuponlardan foydalanishingiz mumkin!"
        )
        keyboard = [
            [InlineKeyboardButton("💎 Premium Kuponlar", callback_data="premium_coupons")],
            [InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")],
        ]
    else:
        text = (
            "❌ *Hozircha Premium ocholmaysiz!*\n\n"
            f"📊 **Sizning holatingiz:**\n👥 Referallar: {referrals_count}/{required_refs} ta\n\n📤 Ko'proq do'stlaringizni taklif qiling va Premiumga ega bo'ling!"
        )
        keyboard = [
            [InlineKeyboardButton("👥 Referal Havola", callback_data="get_referral_link")],
            [InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="premium_coupons")],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_referral_link(query, user_id: int):
    bot_username = (await query.message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
    referrals_count = get_user_referrals(user_id)
    required_refs = data["settings"]["min_referrals"]

    text = (
        "📤 *REFERAL HAVOLANGIZ*\n\n"
        f"`{ref_link}`\n\n"
        f"📊 **Sizning statistikangiz:**\n👥 Referallar: {referrals_count}/{required_refs} ta\n🎯 Maqsad: {required_refs} ta (Bepul Premium)\n\n"
        "💡 **Qanday ishlatish:**\n1. Havolani nusxalang\n2. Do'stlaringizga yuboring\n3. Har bir yangi foydalanuvchi +1 referal\n4. {required_refs} ta referal = Bepul Premium!\n\n"
        "🔗 Havolani ko'proq odamga yuboring, tezroq Premiumga ega bo'ling!"
    )

    keyboard = [
        [InlineKeyboardButton("🔗 TELEGRAMDA ULASHISH", callback_data="share_referral")],
        [InlineKeyboardButton("💎 Premium Olish", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def share_referral_link(query, user_id: int):
    bot_username = (await query.message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"

    encoded_link = urllib.parse.quote_plus(ref_link)
    text_for_share = urllib.parse.quote_plus("🎯 Futbol Kuponlari Boti - Kunlik bepul kuponlar va premium bashoratlar!")

    keyboard = [
        [
            InlineKeyboardButton(
                "📤 TELEGRAMDA ULASHISH",
                url=f"https://t.me/share/url?url={encoded_link}&text={text_for_share}",
            )
        ],
        [InlineKeyboardButton("👥 Referal Statistikasi", callback_data="get_referral_link")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🔗 *Havolani quyidagi tugma orqali osongina ulashing:*\n\nTugmani bosing va do'stlaringizga yuboring!",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def show_help(query):
    text = (
        "ℹ️ *BOTDAN FOYDALANISH QO'LLANMASI*\n\n"
        "⚽ *Kuponlar:*\n• **Bugungi kuponlar** - Kunlik yangilanadigan bepul bashoratlar\n"
        "• **Premium kuponlar** - Yuqori daromadli ekskluziv kuponlar\n\n"
        "💎 *Premium Olish:*\n• **10 ta referal** to'plang\n• **100 so'm** to'lov qiling\n• Premium kuponlarga ega bo'ling\n\n"
        "🔗 *Referal Tizimi:*\n• Do'stlaringizni taklif qiling\n• Har bir referal sizga +1 ball\n• 10 ta referal = Bepul Premium\n\n"
        "📞 *Qo'llab-quvvatlash:*\nMurojaatlar uchun: @admin\n\n🚀 *Bot har kuni yangilanadi va yangi kuponlar qo‘shiladi!*"
    )
    keyboard = [
        [InlineKeyboardButton("🔗 Havolani Ulashish", callback_data="share_referral")],
        [InlineKeyboardButton("💎 Premium Olish", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# ---------------- Admin functions (add/edit/clear/toggle) ----------------
async def show_admin_panel(query):
    today_status = "🟢 Faol" if data["coupons"]["today"]["active"] else "🔴 Nofaol"
    premium_status = "🟢 Faol" if data["coupons"]["premium"]["active"] else "🔴 Nofaol"
    today_count = len(data["coupons"]["today"]["matches"])
    premium_count = len(data["coupons"]["premium"]["matches"])

    premium_users = sum(1 for user in data["users"].values() if user.get("premium", False))

    text = (
        "👑 *ADMIN PANELI*\n\n"
        f"📊 **Bot Statistikasi:**\n👥 Foydalanuvchilar: {data['stats'].get('total_users', 0)} ta\n"
        f"💎 Premium foydalanuvchilar: {premium_users} ta\n\n"
        "⚽ **Kuponlar Holati:**\n"
        f"📅 Bugungi kuponlar: {today_status} ({today_count} ta)\n"
        f"💎 Premium kuponlar: {premium_status} ({premium_count} ta)\n\n"
        "🎯 **Admin Imkoniyatlari:**"
    )

    keyboard = [
        [InlineKeyboardButton("➕ Kupon Qo'shish", callback_data="admin_add_coupon")],
        [InlineKeyboardButton("🔑 Kupon Kodlarini O'zgartirish", callback_data="admin_edit_codes")],
        [InlineKeyboardButton("🔄 Faol/O'chirish", callback_data="admin_toggle_coupons")],
        [InlineKeyboardButton("🗑️ Kuponlarni Tozalash", callback_data="admin_clear_coupons")],
        [InlineKeyboardButton("💳 To'lov Sozlamalari", callback_data="admin_payment_settings")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_coupon_type_selection(query):
    text = "📋 *Qaysi kupon turiga kupon qo'shmoqchisiz?*"
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kupon", callback_data="add_today")],
        [InlineKeyboardButton("💎 Premium Kupon", callback_data="add_premium")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def start_adding_coupon(query, context: ContextTypes.DEFAULT_TYPE, coupon_type: str):
    context.user_data["adding_coupon"] = True
    context.user_data["coupon_type"] = coupon_type
    coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
    await query.edit_message_text(
        f"✏️ *{coupon_name} Kupon Qo'shish*\n\n"
        "Quyidagi formatda ma'lumot yuboring:\n\n"
        "`sana|vaqt|liga|jamoalar|bashorat|koeffitsient|ishonch|1xbet_kodi|melbet_kodi|dbbet_kodi`\n\n"
        "*Misol:*\n"
        "`2024-01-20|20:00|Premier League|Man City vs Arsenal|1X|1.50|85%|1XBET123|MELBET456|DBBET789`\n\n"
        "📝 *Eslatma:* Bir nechta kupon qo'shish uchun har birini alohida yuboring.",
        parse_mode="Markdown",
    )


async def toggle_coupons_selection(query):
    text = "🔄 *Qaysi kuponlarni o'zgartirmoqchisiz?*"
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="toggle_today")],
        [InlineKeyboardButton("💎 Premium Kuponlar", callback_data="toggle_premium")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def toggle_specific_coupons(query, coupon_type: str):
    data["coupons"][coupon_type]["active"] = not data["coupons"][coupon_type]["active"]
    save_data(data)
    coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
    status = "faol" if data["coupons"][coupon_type]["active"] else "nofaol"
    await query.message.reply_text(f"✅ {coupon_name} kuponlar {status} holatga o'zgartirildi!")
    await show_admin_panel(query)


async def clear_coupons_selection(query):
    text = "🗑️ *Qaysi kuponlarni tozalamoqchisiz?*"
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="clear_today")],
        [InlineKeyboardButton("💎 Premium Kuponlar", callback_data="clear_premium")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def clear_specific_coupons(query, coupon_type: str):
    data["coupons"][coupon_type]["matches"] = []
    data["coupons"][coupon_type]["coupon_codes"] = {
        "1xbet": generate_coupon_code(),
        "melbet": generate_coupon_code(),
        "dbbet": generate_coupon_code(),
    }
    save_data(data)
    coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
    await query.message.reply_text(f"✅ {coupon_name} kuponlar tozalandi va yangi kodlar yaratildi!")
    await show_admin_panel(query)


async def edit_coupon_codes_selection(query):
    text = "🔑 *Qaysi kupon kodlarini o'zgartirmoqchisiz?*"
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kupon Kodlari", callback_data="edit_codes_today")],
        [InlineKeyboardButton("💎 Premium Kupon Kodlari", callback_data="edit_codes_premium")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def start_editing_codes(query, context: ContextTypes.DEFAULT_TYPE, coupon_type: str):
    context.user_data["editing_codes"] = True
    context.user_data["coupon_type"] = coupon_type
    current_codes = data["coupons"][coupon_type]["coupon_codes"]
    coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
    text = (
        f"✏️ *{coupon_name} Kupon Kodlarini O'zgartirish*\n\n"
        "🆔 **Joriy kodlar:**\n"
        f"• 1xBet: `{current_codes.get('1xbet', 'Mavjud emas')}`\n"
        f"• MelBet: `{current_codes.get('melbet', 'Mavjud emas')}`\n"
        f"• DB Bet: `{current_codes.get('dbbet', 'Mavjud emas')}`\n\n"
        "Yangi kodlarni quyidagi formatda yuboring:\n\n`1xbet_kodi|melbet_kodi|dbbet_kodi`\n\n"
        "*Misol:*\n`1XBET123|MELBET456|DBBET789`"
    )
    await query.edit_message_text(text, parse_mode="Markdown")


async def show_payment_settings(query):
    payment_details = data["settings"]["payment_details"]
    text = (
        "💳 *TO'LOV SOZLAMALARI*\n\n"
        f"💰 **Premium narxi:** {data['settings']['premium_price']} {data['settings']['currency']}\n"
        f"👥 **Referal talabi:** {data['settings']['min_referrals']} ta\n\n"
        f"📋 **Joriy to'lov rekvizitlari:**\n{payment_details}\n\n"
        "To'lov rekvizitlarini o'zgartirish uchun yangi matn yuboring."
    )
    keyboard = [
        [InlineKeyboardButton("✏️ Rekvizitlarni Tahrirlash", callback_data="edit_payment_details")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def process_coupon_addition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_text = update.message.text
        parts = message_text.split("|")
        if len(parts) < 10:
            await update.message.reply_text("❌ Noto'g'ri format! 10 ta parametr kerak.")
            return

        date, time, league, teams, prediction, odds, confidence, code_1xbet, code_melbet, code_dbbet = [p.strip() for p in parts[:10]]
        coupon_type = context.user_data.get("coupon_type", "today")
        new_match = {"time": time, "league": league, "teams": teams, "prediction": prediction, "odds": odds, "confidence": confidence}

        if not data["coupons"][coupon_type]["matches"]:
            data["coupons"][coupon_type]["coupon_codes"] = {"1xbet": code_1xbet, "melbet": code_melbet, "dbbet": code_dbbet}

        data["coupons"][coupon_type]["matches"].append(new_match)
        data["coupons"][coupon_type]["date"] = date
        save_data(data)

        coupon_codes = data["coupons"][coupon_type]["coupon_codes"]
        coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
        matches_count = len(data["coupons"][coupon_type]["matches"])

        await update.message.reply_text(
            f"✅ *{coupon_name} kupon qo'shildi!*\n\n🔑 **Kupon Kodlari:**\n"
            f"• 1xBet: `{coupon_codes.get('1xbet', '')}`\n• MelBet: `{coupon_codes.get('melbet', '')}`\n• DB Bet: `{coupon_codes.get('dbbet', '')}`\n\n"
            f"📊 **Jami kuponlar:** {matches_count} ta\n📅 **Sana:** {date}\n\nYana kupon qo'shishingiz mumkin yoki /start buyrug'i orqali bosh menyuga qayting.",
            parse_mode="Markdown",
        )
    except Exception:
        logger.exception("process_coupon_addition failed")
        await update.message.reply_text("❌ Kupon qo'shishda xatolik yuz berdi.")
    finally:
        context.user_data.pop("adding_coupon", None)
        context.user_data.pop("coupon_type", None)


async def process_codes_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_text = update.message.text
        parts = message_text.split("|")
        if len(parts) < 3:
            await update.message.reply_text("❌ Noto'g'ri format! 3 ta kod kerak.")
            return
        code_1xbet, code_melbet, code_dbbet = [p.strip() for p in parts[:3]]
        coupon_type = context.user_data.get("coupon_type", "today")
        data["coupons"][coupon_type]["coupon_codes"] = {"1xbet": code_1xbet, "melbet": code_melbet, "dbbet": code_dbbet}
        save_data(data)
        coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
        await update.message.reply_text(
            f"✅ *{coupon_name} kupon kodlari yangilandi!*\n\n🔑 **Yangi kodlar:**\n"
            f"• 1xBet: `{code_1xbet}`\n• MelBet: `{code_melbet}`\n• DB Bet: `{code_dbbet}`",
            parse_mode="Markdown",
        )
    except Exception:
        logger.exception("process_codes_edit failed")
        await update.message.reply_text("❌ Kodlarni yangilashda xatolik yuz berdi.")
    finally:
        context.user_data.pop("editing_codes", None)
        context.user_data.pop("coupon_type", None)


async def process_payment_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_payment_details = update.message.text
        data["settings"]["payment_details"] = new_payment_details
        save_data(data)
        await update.message.reply_text("✅ To'lov rekvizitlari yangilandi!")
    except Exception:
        logger.exception("process_payment_edit failed")
        await update.message.reply_text("❌ To'lov rejalarini yangilashda xato.")
    finally:
        context.user_data.pop("editing_payment", None)


# ---------------- Message handler for admin actions ----------------
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    if context.user_data.get("adding_coupon"):
        await process_coupon_addition(update, context)
        return
    if context.user_data.get("editing_codes"):
        await process_codes_edit(update, context)
        return
    if context.user_data.get("editing_payment"):
        await process_payment_edit(update, context)
        return


# ---------------- CallbackQuery handler (main) ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data_cb = query.data

    # admin callbacks and others
    if data_cb == "today_coupons":
        await send_today_coupons(query)
    elif data_cb == "premium_coupons":
        await (send_premium_coupons(query) if is_premium(user_id) else show_premium_offer(query, user_id))
    elif data_cb == "get_referral_link":
        await show_referral_link(query, user_id)
    elif data_cb == "share_referral":
        await share_referral_link(query, user_id)
    elif data_cb == "buy_premium":
        await show_premium_payment(query, user_id)
    elif data_cb == "help":
        await show_help(query)
    elif data_cb == "back":
        await back_to_main(query)
    elif data_cb == "admin":
        if is_admin(user_id):
            await show_admin_panel(query)
        else:
            await query.message.reply_text("❌ Siz admin emassiz!")
    elif data_cb == "admin_add_coupon":
        await show_coupon_type_selection(query)
    elif data_cb == "admin_toggle_coupons":
        await toggle_coupons_selection(query)
    elif data_cb == "admin_clear_coupons":
        await clear_coupons_selection(query)
    elif data_cb == "admin_edit_codes":
        await edit_coupon_codes_selection(query)
    elif data_cb == "admin_payment_settings":
        await show_payment_settings(query)
    elif data_cb.startswith("add_"):
        coupon_type = data_cb.replace("add_", "")
        await start_adding_coupon(query, context, coupon_type)
    elif data_cb.startswith("clear_"):
        coupon_type = data_cb.replace("clear_", "")
        await clear_specific_coupons(query, coupon_type)
    elif data_cb.startswith("edit_codes_"):
        coupon_type = data_cb.replace("edit_codes_", "")
        await start_editing_codes(query, context, coupon_type)
    elif data_cb.startswith("toggle_"):
        coupon_type = data_cb.replace("toggle_", "")
        await toggle_specific_coupons(query, coupon_type)
    elif data_cb == "get_free_premium":
        await activate_free_premium(query, user_id)
    elif data_cb == "edit_payment_details":
        if is_admin(user_id):
            context.user_data["editing_payment"] = True
            await query.edit_message_text("✏️ Iltimos, yangi to'lov rekvizitlarini yuboring (plain text).")
        else:
            await query.answer("❌ Siz admin emassiz!", show_alert=True)


# ---------------- Back to main ----------------
async def back_to_main(query):
    user = query.from_user
    user_id = user.id
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons"),
         InlineKeyboardButton("💎 Premium Kuponlar", callback_data="premium_coupons")],
        [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link"),
         InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")],
        [InlineKeyboardButton("💳 Premium Sotib Olish", callback_data="buy_premium"),
         InlineKeyboardButton("ℹ️ Yordam", callback_data="help")],
    ]
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🎯 *Asosiy Menyu*\n\nQuyidagi tugmalardan foydalanib botdan to'liq foydalaning! 🚀", reply_markup=reply_markup, parse_mode="Markdown")


# ---------------- Error handler and startup checks ----------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled exception: %s", context.error)
    try:
        if isinstance(update, Update) and update.effective_user:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Bot ichida xato yuz berdi: {context.error}")
    except Exception:
        logger.exception("Failed to notify admin about the error.")


def delete_webhook_if_set(token: str):
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/deleteWebhook", timeout=10)
        logger.info("deleteWebhook result: %s", r.text)
    except Exception:
        logger.exception("deleteWebhook request failed")


def log_getme(token: str):
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        logger.info("getMe: %s", r.text)
    except Exception:
        logger.exception("getMe request failed")


# ---------------- Main ----------------
def main():
    if not TOKEN:
        logger.error("BOT_TOKEN not set. Set BOT_TOKEN environment variable or edit the script.")
        raise RuntimeError("BOT_TOKEN is required")

    # diagnostic
    delete_webhook_if_set(TOKEN)
    log_getme(TOKEN)
    logger.info("Using DATA_FILE: %s", DATA_FILE)

    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Register message handler (admin flows)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))

    # Error handler
    app.add_error_handler(error_handler)

    logger.info("✅ Bot ishga tushmoqda (run_polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()
