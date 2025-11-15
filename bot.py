import os
import json
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Bot tokeni
TOKEN = "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g"

# Admin ID (o'zingizning ID ingizni qo'ying)
ADMIN_ID = 123456789  # O'z ID ingizni qo'ying

# Ma'lumotlarni saqlash fayli
DATA_FILE = "data.json"

# Loggerni sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Boshlang'ich ma'lumotlar
default_data = {
    "users": {},
    "coupons": {
        "today": {
            "date": "",
            "matches": [],
            "description": "📊 Bugungi ishonchli kuponlar",
            "active": True
        },
        "tomorrow": {
            "date": "",
            "matches": [],
            "description": "📈 Ertangi kun kuponlari",
            "active": True
        }
    },
    "settings": {
        "min_referrals": 3,
        "max_referrals": 10,
        "premium_price": 50000,
        "currency": "so'm"
    },
    "stats": {
        "total_users": 0,
        "premium_users": 0,
        "total_coupons_sent": 0
    },
    "bookmakers": {
        "1xbet": {
            "name": "1xBet",
            "url": "https://1xbet.com",
            "bonus": "100% bonus to'ldirish",
            "active": True
        },
        "melbet": {
            "name": "MelBet",
            "url": "https://melbet.com",
            "bonus": "110% bonus to'ldirish",
            "active": True
        },
        "olympusbet": {
            "name": "OlympusBet",
            "url": "https://olympusbet.com",
            "bonus": "120% bonus to'ldirish",
            "active": True
        }
    }
}

# Ma'lumotlarni yuklash
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        save_data(default_data)
        return default_data
    except Exception as e:
        logger.error(f"Ma'lumotlarni yuklashda xato: {e}")
        return default_data

# Ma'lumotlarni saqlash
def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ma'lumotlarni saqlashda xato: {e}")
        return False

# Ma'lumotlarni yuklab olish
data = load_data()

def is_admin(user_id):
    """Admin tekshirish"""
    return user_id == ADMIN_ID

def is_premium(user_id):
    """Premium foydalanuvchi tekshirish"""
    user_data = data['users'].get(str(user_id), {})
    return user_data.get('premium', False)

def get_user_referrals(user_id):
    """Foydalanuvchi referallar soni"""
    user_data = data['users'].get(str(user_id), {})
    return user_data.get('referrals', 0)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user = update.effective_user
    user_id = user.id
    
    # Yangi foydalanuvchini qo'shish
    if str(user_id) not in data['users']:
        data['users'][str(user_id)] = {
            'name': user.first_name,
            'username': user.username,
            'referrals': 0,
            'premium': False,
            'joined_date': datetime.now().isoformat(),
            'last_coupon_date': None
        }
        data['stats']['total_users'] += 1
        save_data(data)
    
    # Referal tekshirish
    if context.args:
        ref_id = context.args[0]
        if ref_id.startswith('ref'):
            try:
                referrer_id = int(ref_id[3:])
                if str(referrer_id) in data['users'] and referrer_id != user_id:
                    data['users'][str(referrer_id)]['referrals'] += 1
                    save_data(data)
                    await update.message.reply_text(
                        "✅ Siz do'stingiz taklifi orqali qo'shildingiz! "
                        "Endi siz ham referal yigishingiz mumkin."
                    )
            except:
                pass

    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons")],
        [InlineKeyboardButton("📅 Ertangi Kuponlar", callback_data="tomorrow_coupons")],
        [InlineKeyboardButton("🎯 Premium Kuponlar", callback_data="premium_coupons")],
        [InlineKeyboardButton("🏆 Bukmekerlar", callback_data="bookmakers")],
        [InlineKeyboardButton("👥 Referal Tizimi", callback_data="referral_system")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]
    
    # Admin paneli
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚽ Salom {user.first_name}!\n\n"
        "📊 *Futbol Kuponlari Botiga Xush Kelibsiz!*\n\n"
        "🎯 *Bizning bot orqali siz:*\n"
        "• ⚽ Bepul kuponlar olasiz\n"
        "• 📈 Premium kuponlarga ega bo'lasiz\n"
        "• 💰 Referal orqali daromad topshasiz\n"
        "• 🏆 Ishonchli bukmekerlar bilan ishlaysiz",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalarni boshqarish"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "today_coupons":
        await send_today_coupons(query, user_id)
    
    elif query.data == "tomorrow_coupons":
        await send_tomorrow_coupons(query, user_id)
    
    elif query.data == "premium_coupons":
        await handle_premium_coupons(query, user_id)
    
    elif query.data == "bookmakers":
        await show_bookmakers(query)
    
    elif query.data == "referral_system":
        await show_referral_system(query, user_id)
    
    elif query.data == "help":
        await show_help(query)
    
    elif query.data == "admin":
        if is_admin(user_id):
            await show_admin_panel(query)
        else:
            await query.message.reply_text("❌ Siz admin emassiz!")
    
    elif query.data.startswith("admin_"):
        if is_admin(user_id):
            await handle_admin_actions(query, context)
    
    elif query.data == "buy_premium":
        await show_premium_payment(query, user_id)
    
    elif query.data == "get_referral_link":
        await show_referral_link(query, user_id)

async def send_today_coupons(query, user_id):
    """Bugungi kuponlarni yuborish"""
    today_coupons = data['coupons']['today']
    
    if not today_coupons['matches']:
        await query.edit_message_text(
            "❌ Bugun uchun kuponlar hali tayyor emas.\n"
            "Iltimos, keyinroq urinib ko'ring yoki ertangi kun kuponlarini tekshiring.",
            parse_mode='Markdown'
        )
        return
    
    coupon_text = f"⚽ *{today_coupons['description']}*\n"
    coupon_text += f"📅 Sana: {today_coupons['date']}\n\n"
    
    for i, match in enumerate(today_coupons['matches'], 1):
        coupon_text += f"*{i}. {match['time']} - {match['league']}*\n"
        coupon_text += f"🏆 {match['teams']}\n"
        coupon_text += f"🎯 Bashorat: *{match['prediction']}*\n"
        coupon_text += f"📊 Koeffitsient: *{match['odds']}*\n"
        coupon_text += f"💎 Ishonch: {match['confidence']}\n\n"
    
    coupon_text += "💰 *Umumiy koeffitsient:* 🚀\n"
    coupon_text += "⏰ *Muhim:* Stavkalarni o'yin boshlanishidan oldin qo'ying!\n\n"
    coupon_text += "📱 *Stavka qo'yish uchun:*\n"
    
    keyboard = [
        [InlineKeyboardButton("🏆 1xBet", url=data['bookmakers']['1xbet']['url'])],
        [InlineKeyboardButton("🎯 MelBet", url=data['bookmakers']['melbet']['url'])],
        [InlineKeyboardButton("⚽ OlympusBet", url=data['bookmakers']['olympusbet']['url'])],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(coupon_text, reply_markup=reply_markup, parse_mode='Markdown')

async def send_tomorrow_coupons(query, user_id):
    """Ertangi kun kuponlarini yuborish"""
    tomorrow_coupons = data['coupons']['tomorrow']
    
    if not tomorrow_coupons['matches']:
        await query.edit_message_text(
            "❌ Ertangi kun uchun kuponlar hali tayyor emas.\n"
            "Iltimos, keyinroq urinib ko'ring.",
            parse_mode='Markdown'
        )
        return
    
    coupon_text = f"📈 *{tomorrow_coupons['description']}*\n"
    coupon_text += f"📅 Sana: {tomorrow_coupons['date']}\n\n"
    
    for i, match in enumerate(tomorrow_coupons['matches'], 1):
        coupon_text += f"*{i}. {match['time']} - {match['league']}*\n"
        coupon_text += f"🏆 {match['teams']}\n"
        coupon_text += f"🎯 Bashorat: *{match['prediction']}*\n"
        coupon_text += f"📊 Koeffitsient: *{match['odds']}*\n"
        coupon_text += f"💎 Ishonch: {match['confidence']}\n\n"
    
    coupon_text += "💰 *Umumiy koeffitsient:* 🚀\n"
    coupon_text += "⏰ *Eslatma:* Kuponlar ertaga yangilanadi!\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(coupon_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_premium_coupons(query, user_id):
    """Premium kuponlarni ko'rsatish"""
    if is_premium(user_id):
        await send_premium_coupons(query, user_id)
    else:
        await show_premium_offer(query, user_id)

async def send_premium_coupons(query, user_id):
    """Premium kuponlarni yuborish"""
    premium_text = """
🎯 *PREMIUM KUPONLAR*

💎 *Ekskluziv imkoniyatlar:*
• Yuqori daromadli kuponlar
• VIP bashoratlar
• Statistik tahlillar
• Shaxsiy maslahatlar

📊 *Bugungi Premium Kupon:*

⚽ *Champions League - 1/8 Final*
🏆 Real Madrid vs Bayern Munich
🎯 Bashorat: *1X & Over 2.5*
📊 Koeffitsient: *3.50*
💎 Ishonch: 95%

⚽ *Premier League*
🏆 Manchester City vs Arsenal  
🎯 Bashorat: *BTTS - Ha*
📊 Koeffitsient: *1.80*
💎 Ishonch: 88%

💰 *Umumiy koeffitsient:* 6.30 🚀

🎁 *Premium a'zo bo'lganingiz uchun rahmat!*"""

    keyboard = [
        [InlineKeyboardButton("🏆 Stavka qo'yish", url=data['bookmakers']['1xbet']['url'])],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(premium_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_premium_offer(query, user_id):
    """Premium taklifini ko'rsatish"""
    referrals_count = get_user_referrals(user_id)
    required_refs = data['settings']['min_referrals']
    
    premium_text = f"""
🎯 *PREMIUM KUPONLARGA KIRISH*

💎 *Premium a'zo bo'lish usullari:*

1️⃣ *Referal orqali* ({referrals_count}/{required_refs})
   - {required_refs} ta do'stingizni taklif qiling
   - Bepul premium oching

2️⃣ *To'lov orqali*
   - {data['settings']['premium_price']:,} {data['settings']['currency']}
   - Darhol premium oching

📊 *Premium afzalliklari:*
• Yuqori daromadli kuponlar
• Ekskluziv bashoratlar  
• Statistik tahlillar
• 95% gacha ishonch
• Shaxsiy qo'llab-quvvatlash"""

    keyboard = []
    
    if referrals_count >= required_refs:
        keyboard.append([InlineKeyboardButton("🎁 Bepul Premium Ochish", callback_data="get_free_premium")])
    else:
        keyboard.append([InlineKeyboardButton("👥 Do'stlarni Taklif Qilish", callback_data="get_referral_link")])
    
    keyboard.extend([
        [InlineKeyboardButton("💳 Premium Sotib Olish", callback_data="buy_premium")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(premium_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_bookmakers(query):
    """Bukmekerlar ro'yxati"""
    text = """
🏆 *Ishonchli Bukmekerlar*

Quyidagi bukmekerlar orqali stavka qo'yishingiz mumkin:"""

    keyboard = []
    
    for bookmaker_id, bookmaker in data['bookmakers'].items():
        if bookmaker['active']:
            keyboard.append([
                InlineKeyboardButton(
                    f"🎯 {bookmaker['name']} - {bookmaker['bonus']}", 
                    url=bookmaker['url']
                )
            ])
    
    keyboard.append([InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_referral_system(query, user_id):
    """Referal tizimi"""
    referrals_count = get_user_referrals(user_id)
    required_refs = data['settings']['min_referrals']
    
    text = f"""
👥 *Referal Tizimi*

📊 Sizning referallaringiz: *{referrals_count} ta*
🎯 Maqsad: *{required_refs} ta* (Premium uchun)

💰 *Referal mukofotlari:*
• 3 ta referal = Bepul Premium
• Har bir referal = Qo'shimcha imkoniyatlar

📤 *Do'stlaringizni taklif qiling va premiumga ega bo'ling!*"""

    keyboard = [
        [InlineKeyboardButton("📤 Referal Havolam", callback_data="get_referral_link")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_referral_link(query, user_id):
    """Referal havolasini ko'rsatish"""
    bot_username = (await query.message._bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
    referrals_count = get_user_referrals(user_id)
    
    text = f"""
📤 *Referal Havolangiz*

`{ref_link}`

👥 *Qanday ishlatish:*
1. Ushbu havolani do'stlaringizga yuboring
2. Har bir yangi foydalanuvchi sizga +1 referal
3. {data['settings']['min_referrals']} ta referal = Bepul Premium

📊 *Sizning referallaringiz:* {referrals_count} ta

💡 *Maslahat:* Havolani ko'proq odamga yuboring, tezroq premiumga ega bo'ling!"""

    keyboard = [
        [InlineKeyboardButton("👥 Referal Tizimi", callback_data="referral_system")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_premium_payment(query, user_id):
    """Premium to'lov ma'lumotlari"""
    text = f"""
💳 *Premium A'zolik*

💰 Narxi: *{data['settings']['premium_price']:,} {data['settings']['currency']}*

📋 *To'lov usullari:*
• Click 💰
• Payme 📱  
• Uzumbank 🏦
• Oson 💸

💎 *Premium afzalliklari:*
• Yuqori daromadli kuponlar
• Ekskluziv bashoratlar
• 95% gacha ishonch
• Shaxsiy qo'llab-quvvatlash

📞 *To'lov qilgach, admin bilan bog'laning:* @admin_username"""

    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="premium_coupons")],
        [InlineKeyboardButton("🏠 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_help(query):
    """Yordam menyusi"""
    text = """
ℹ️ *Botdan Foydalanish Qo'llanmasi*

⚽ *Kuponlar:*
• *Bugungi kuponlar* - Kunlik bepul bashoratlar
• *Ertangi kuponlar* - Keyingi kun uchun tayyorlov
• *Premium kuponlar* - Yuqori daromadli ekskluziv bashoratlar

👥 *Referal Tizimi:*
• Do'stlaringizni taklif qiling
• 3 ta referal = Bepul premium
• Daromad oshiring

💎 *Premium A'zolik:*
• Yuqori daromadli kuponlar
• Ekskluziv bashoratlar
• Statistik tahlillar

🏆 *Bukmekerlar:*
• Ishonchli bukmekerlar
• Bonuslar va takliflar
• Tez to'lovlar

📞 *Qo'llab-quvvatlash:* @admin_username"""

    keyboard = [[InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ADMIN PANEL FUNCTIONS
async def show_admin_panel(query):
    """Admin paneli"""
    text = """
👑 *Admin Panel*

Quyidagi imkoniyatlar:"""

    keyboard = [
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("⚽ Kuponlarni Boshqarish", callback_data="admin_coupons")],
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="admin_settings")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_admin_actions(query, context: ContextTypes.DEFAULT_TYPE):
    """Admin harakatlari"""
    action = query.data
    
    if action == "admin_stats":
        await show_admin_stats(query)
    
    elif action == "admin_coupons":
        await show_coupon_management(query)
    
    elif action == "admin_users":
        await show_user_management(query)
    
    elif action == "admin_settings":
        await show_admin_settings(query)
    
    elif action.startswith("admin_add_coupon_"):
        coupon_type = action.replace("admin_add_coupon_", "")
        await add_coupon(query, context, coupon_type)

async def show_admin_stats(query):
    """Admin statistikasi"""
    stats = data['stats']
    premium_users = sum(1 for user in data['users'].values() if user.get('premium', False))
    
    text = f"""
📊 *Bot Statistikasi*

👥 Jami foydalanuvchilar: `{stats['total_users']}`
💎 Premium foydalanuvchilar: `{premium_users}`
📤 Jami kuponlar yuborilgan: `{stats['total_coupons_sent']}`

📈 *Faol bukmekerlar:*"""
    
    for bookmaker_id, bookmaker in data['bookmakers'].items():
        if bookmaker['active']:
            text += f"\n• {bookmaker['name']} - 🟢 Faol"
        else:
            text += f"\n• {bookmaker['name']} - 🔴 Nofaol"

    keyboard = [[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_coupon_management(query):
    """Kuponlarni boshqarish"""
    text = """
⚽ *Kuponlarni Boshqarish*

Quyidagi kuponlarni tahrirlashingiz mumkin:"""

    keyboard = [
        [InlineKeyboardButton("📅 Bugungi Kuponlar", callback_data="admin_edit_today")],
        [InlineKeyboardButton("📈 Ertangi Kuponlar", callback_data="admin_edit_tomorrow")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_user_management(query):
    """Foydalanuvchilarni boshqarish"""
    text = f"""
👥 *Foydalanuvchilarni Boshqarish*

Jami foydalanuvchilar: {data['stats']['total_users']}

Foydalanuvchi ID sini yuboring premium qilish uchun:"""

    keyboard = [[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Contextga ma'lumot saqlaymiz
    context = query.message._bot.context
    context.user_data['waiting_for_user_id'] = True
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_admin_settings(query):
    """Admin sozlamalari"""
    settings = data['settings']
    
    text = f"""
⚙️ *Sozlamalar*

👥 Minimal referal: `{settings['min_referrals']}`
💰 Premium narxi: `{settings['premium_price']:,} {settings['currency']}`

Sozlamalarni o'zgartirish uchun /settings buyrug'idan foydalaning."""

    keyboard = [[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin xabarlarini qayta ishlash"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    if 'waiting_for_user_id' in context.user_data:
        user_id_to_premium = update.message.text
        await make_user_premium(update, user_id_to_premium)

async def make_user_premium(update: Update, user_id_str: str):
    """Foydalanuvchini premium qilish"""
    try:
        user_id = int(user_id_str)
        if str(user_id) in data['users']:
            data['users'][str(user_id)]['premium'] = True
            save_data(data)
            await update.message.reply_text(f"✅ {user_id} premium a'zo qilindi!")
        else:
            await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri ID format!")

# Admin buyruqlari
async def admin_settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sozlamalarni o'zgartirish"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Sozlamalarni o'zgartirish:\n\n"
            "Minimal referal:\n"
            "/settings min_ref son\n\n"
            "Premium narxi:\n"
            "/settings premium_price son\n\n"
            "Valyuta:\n"
            "/settings currency valyuta"
        )
        return
    
    if context.args[0] == "min_ref" and len(context.args) > 1:
        try:
            data['settings']['min_referrals'] = int(context.args[1])
            save_data(data)
            await update.message.reply_text("✅ Minimal referal yangilandi!")
        except:
            await update.message.reply_text("❌ Noto'g'ri son!")
    
    elif context.args[0] == "premium_price" and len(context.args) > 1:
        try:
            data['settings']['premium_price'] = int(context.args[1])
            save_data(data)
            await update.message.reply_text("✅ Premium narxi yangilandi!")
        except:
            await update.message.reply_text("❌ Noto'g'ri son!")
    
    elif context.args[0] == "currency" and len(context.args) > 1:
        data['settings']['currency'] = context.args[1]
        save_data(data)
        await update.message.reply_text("✅ Valyuta yangilandi!")

async def add_coupon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kupon qo'shish"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    if len(context.args) < 6:
        await update.message.reply_text(
            "Kupon qo'shish:\n\n"
            "Format: /add_coupon tur sana vahta liga jamoalar bashorat koeffitsient ishonch\n\n"
            "Misol: /add_coupon today '2024-01-20' '20:00' 'Premier League' 'Man City vs Arsenal' '1X' '1.50' '85%'"
        )
        return
    
    coupon_type = context.args[0]
    date = context.args[1]
    time = context.args[2]
    league = context.args[3]
    teams = context.args[4]
    prediction = context.args[5]
    odds = context.args[6]
    confidence = context.args[7] if len(context.args) > 7 else "85%"
    
    new_match = {
        'time': time,
        'league': league,
        'teams': teams,
        'prediction': prediction,
        'odds': odds,
        'confidence': confidence
    }
    
    if coupon_type in data['coupons']:
        data['coupons'][coupon_type]['matches'].append(new_match)
        data['coupons'][coupon_type]['date'] = date
        save_data(data)
        await update.message.reply_text("✅ Kupon muvaffaqiyatli qo'shildi!")
    else:
        await update.message.reply_text("❌ Noto'g'ri kupon turi!")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast xabar yuborish"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    if not context.args:
        await update.message.reply_text("Iltimos, xabar matnini yuboring.")
        return
    
    message_text = ' '.join(context.args)
    sent_count = 0
    
    for user_id_str in data['users']:
        try:
            await context.bot.send_message(
                chat_id=int(user_id_str),
                text=message_text,
                parse_mode='Markdown'
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Xabar yuborishda xato {user_id_str}: {e}")
    
    await update.message.reply_text(f"✅ Xabar {sent_count} ta foydalanuvchiga yuborildi!")

async def back_to_main(query):
    """Asosiy menyuga qaytish"""
    user = query.from_user
    user_id = user.id
    
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons")],
        [InlineKeyboardButton("📅 Ertangi Kuponlar", callback_data="tomorrow_coupons")],
        [InlineKeyboardButton("🎯 Premium Kuponlar", callback_data="premium_coupons")],
        [InlineKeyboardButton("🏆 Bukmekerlar", callback_data="bookmakers")],
        [InlineKeyboardButton("👥 Referal Tizimi", callback_data="referral_system")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]
    
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚽ Salom {user.first_name}!\n\n"
        "📊 *Futbol Kuponlari Botiga Xush Kelibsiz!*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Back handler
async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Orqaga tugmasi"""
    query = update.callback_query
    await query.answer()
    await back_to_main(query)

def main():
    """Asosiy dastur"""
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handlerlar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("settings", admin_settings_command))
        app.add_handler(CommandHandler("add_coupon", add_coupon_command))
        app.add_handler(CommandHandler("broadcast", broadcast_command))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(CallbackQueryHandler(back_handler, pattern="^back$"))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
        
        print("✅ Futbol Kuponlari Boti ishga tushdi!")
        print("🤖 Bot ishlayapti...")
        print(f"👑 Admin ID: {ADMIN_ID}")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
