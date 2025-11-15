import os
import json
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Bot tokeni
TOKEN = "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g"

# Admin ID (o'zingizning ID ingizni qo'ying)
ADMIN_ID = 7633561058  # O'z ID ingizni qo'ying

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
        }
    },
    "settings": {
        "min_referrals": 10,  # 10 ta referal talab qilinadi
        "premium_price": 100,  # 100 so'm
        "currency": "so'm",
        "payment_details": "💳 To'lov qilish uchun:\n\nClick: 1234 5678 9012 3456\nPayme: +998901234567\nUzumbank: 8600 1234 5678 9012\n\nTo'lov qilgach, chek skrinshotini @admin ga yuboring."
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
        [InlineKeyboardButton("🎯 Premium Kuponlar", callback_data="premium_coupons")],
        [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
        [InlineKeyboardButton("🏆 Bukmekerlar", callback_data="bookmakers")],
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
        "• 💎 Premium kuponlarga ega bo'lasiz\n"
        "• 👥 10 ta referal yoki 100 so'm to'lov\n"
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
    
    elif query.data == "premium_coupons":
        await handle_premium_coupons(query, user_id)
    
    elif query.data == "bookmakers":
        await show_bookmakers(query)
    
    elif query.data == "get_referral_link":
        await show_referral_link(query, user_id)
    
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
    
    elif query.data == "get_free_premium":
        await activate_free_premium(query, user_id)
    
    elif query.data == "back":
        await back_to_main(query)
    
    elif query.data == "admin_toggle_coupons":
        await toggle_coupons_active(query)

async def send_today_coupons(query, user_id):
    """Bugungi kuponlarni yuborish"""
    today_coupons = data['coupons']['today']
    
    if not today_coupons['active']:
        await query.edit_message_text(
            "❌ Bugungi kuponlar hozircha mavjud emas.\n"
            "Iltimos, keyinroq urinib ko'ring.",
            parse_mode='Markdown'
        )
        return
    
    if not today_coupons['matches']:
        await query.edit_message_text(
            "❌ Bugun uchun kuponlar hali tayyor emas.\n"
            "Iltimos, keyinroq urinib ko'ring.",
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
    
    # Umumiy koeffitsientni hisoblash
    total_odds = 1.0
    for match in today_coupons['matches']:
        try:
            total_odds *= float(match['odds'])
        except:
            pass
    
    coupon_text += f"💰 *Umumiy koeffitsient:* *{total_odds:.2f}* 🚀\n"
    coupon_text += "⏰ *Muhim:* Stavkalarni o'yin boshlanishidan oldin qo'ying!\n\n"
    coupon_text += "📱 *Stavka qo'yish uchun:*\n"
    
    keyboard = [
        [InlineKeyboardButton("🏆 1xBet", url=data['bookmakers']['1xbet']['url'])],
        [InlineKeyboardButton("🎯 MelBet", url=data['bookmakers']['melbet']['url'])],
        [InlineKeyboardButton("⚽ OlympusBet", url=data['bookmakers']['olympusbet']['url'])],
        [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    
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

⚽ *Serie A*
🏆 Juventus vs Inter Milan
🎯 Bashorat: *2X*
📊 Koeffitsient: *1.65*
💎 Ishonch: 82%

💰 *Umumiy koeffitsient:* 10.40 🚀

🎁 *Premium a'zo bo'lganingiz uchun rahmat!*"""

    keyboard = [
        [InlineKeyboardButton("🏆 Stavka qo'yish", url=data['bookmakers']['1xbet']['url'])],
        [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
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
        keyboard.append([InlineKeyboardButton("📤 Do'stlarni Taklif Qilish", callback_data="get_referral_link")])
    
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
    
    keyboard.append([InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")])
    keyboard.append([InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_referral_link(query, user_id):
    """Referal havolasini ko'rsatish"""
    bot_username = (await query.message._bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
    referrals_count = get_user_referrals(user_id)
    required_refs = data['settings']['min_referrals']
    
    text = f"""
📤 *Referal Havolangiz*

`{ref_link}`

👥 *Qanday ishlatish:*
1. Ushbu havolani do'stlaringizga yuboring
2. Har bir yangi foydalanuvchi sizga +1 referal
3. {required_refs} ta referal = Bepul Premium

📊 *Sizning referallaringiz:* {referrals_count} ta / {required_refs} ta

💡 *Maslahat:* Havolani ko'proq odamga yuboring, tezroq premiumga ega bo'ling!

📝 *Havolani tarqatish usullari:*
• Telegram guruh va kanallarda
• Do'stlaringizga shaxsiy xabar orqali
• Ijtimoiy tarmoqlarda"""

    keyboard = [
        [InlineKeyboardButton("👥 Premium Olish", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_premium_payment(query, user_id):
    """Premium to'lov ma'lumotlari"""
    payment_details = data['settings']['payment_details']
    
    text = f"""
💳 *Premium A'zolik*

💰 Narxi: *{data['settings']['premium_price']:,} {data['settings']['currency']}*

{payment_details}

✅ To'lov qilgach, chek skrinshotini @admin ga yuboring va Premium ochiladi."""

    keyboard = [
        [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="premium_coupons")],
        [InlineKeyboardButton("🏠 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def activate_free_premium(query, user_id):
    """Bepul premiumni faollashtirish"""
    referrals_count = get_user_referrals(user_id)
    required_refs = data['settings']['min_referrals']
    
    if referrals_count >= required_refs:
        data['users'][str(user_id)]['premium'] = True
        save_data(data)
        
        text = """
🎉 *TABRIKLAYMIZ!*

Siz muvaffaqiyatli Premium a'zoga aylandingiz!

💎 *Endi siz quyidagi imkoniyatlarga ega bo'ldingiz:*
• Yuqori daromadli kuponlar
• Ekskluziv bashoratlar
• Statistik tahlillar
• 95% gacha ishonch

📊 Premium kuponlarni ko'rish uchun 'Premium Kuponlar' bo'limiga o'ting."""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Premium Kuponlar", callback_data="premium_coupons")],
            [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
    else:
        text = f"""
❌ *Hozircha Premium ocholmaysiz!*

Sizda {referrals_count} ta referal mavjud, {required_refs} ta kerak.

📤 Ko'proq do'stlaringizni taklif qiling va Premiumga ega bo'ling!"""
        
        keyboard = [
            [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="premium_coupons")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# YANGILANGAN ADMIN PANEL
async def show_admin_panel(query):
    """Admin paneli"""
    today_status = "🟢 Faol" if data['coupons']['today']['active'] else "🔴 Nofaol"
    
    text = f"""
👑 *Admin Panel*

📊 Bugungi kuponlar: {today_status}
👥 Jami foydalanuvchilar: {data['stats']['total_users']}
💎 Premium foydalanuvchilar: {sum(1 for user in data['users'].values() if user.get('premium', False))}

Quyidagi imkoniyatlar:"""

    keyboard = [
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("⚽ Kuponlarni Boshqarish", callback_data="admin_coupons")],
        [InlineKeyboardButton("💰 To'lov Sozlamalari", callback_data="admin_payment")],
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="admin_settings")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
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
    
    elif action == "admin_payment":
        await show_payment_settings(query)
    
    elif action == "admin_users":
        await show_user_management(query)
    
    elif action == "admin_settings":
        await show_admin_settings(query)
    
    elif action == "admin_broadcast":
        await start_broadcast(query, context)
    
    elif action.startswith("admin_add_"):
        coupon_type = action.replace("admin_add_", "")
        await start_adding_coupon(query, context, coupon_type)
    
    elif action == "admin_toggle_coupons":
        await toggle_coupons_active(query)
    
    elif action == "admin_clear_coupons":
        await clear_coupons(query)
    
    elif action == "admin_edit_payment":
        await edit_payment_details(query, context)

async def show_coupon_management(query):
    """Kuponlarni boshqarish"""
    today_coupons = data['coupons']['today']
    status = "🟢 Faol" if today_coupons['active'] else "🔴 Nofaol"
    matches_count = len(today_coupons['matches'])
    
    text = f"""
⚽ *Kuponlarni Boshqarish*

📊 Holat: {status}
📈 Kuponlar soni: {matches_count} ta
📅 Oxirgi yangilangan: {today_coupons['date']}

Quyidagi amallarni bajarishingiz mumkin:"""

    keyboard = [
        [InlineKeyboardButton("➕ Yangi Kupon Qo'shish", callback_data="admin_add_today")],
        [InlineKeyboardButton("🔄 Kuponlarni Faollashtirish/O'chirish", callback_data="admin_toggle_coupons")],
        [InlineKeyboardButton("🗑️ Barcha Kuponlarni O'chirish", callback_data="admin_clear_coupons")],
        [InlineKeyboardButton("📋 Kuponlarni Ko'rish", callback_data="admin_view_coupons")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def start_adding_coupon(query, context: ContextTypes.DEFAULT_TYPE, coupon_type: str):
    """Kupon qo'shishni boshlash"""
    context.user_data['adding_coupon'] = True
    context.user_data['coupon_type'] = coupon_type
    
    text = f"""
✏️ *Yangi Kupon Qo'shish*

Quyidagi formatda ma'lumot yuboring:

`sana|vaqt|liga|jamoalar|bashorat|koeffitsient|ishonch`

*Misol:*
`2024-01-20|20:00|Premier League|Manchester City vs Arsenal|1X|1.50|85%`

*Eslatma:* Sana format: YYYY-MM-DD
*Bir nechta kupon qo'shish uchun har birini alohida yuboring.*"""

    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="admin_coupons")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def toggle_coupons_active(query):
    """Kuponlarni faollashtirish/o'chirish"""
    data['coupons']['today']['active'] = not data['coupons']['today']['active']
    save_data(data)
    
    status = "faol" if data['coupons']['today']['active'] else "nofaol"
    await query.message.reply_text(f"✅ Bugungi kuponlar {status} holatga o'zgartirildi!")
    await show_coupon_management(query)

async def clear_coupons(query):
    """Barcha kuponlarni o'chirish"""
    data['coupons']['today']['matches'] = []
    save_data(data)
    
    await query.message.reply_text("✅ Barcha kuponlar o'chirildi!")
    await show_coupon_management(query)

async def show_payment_settings(query):
    """To'lov sozlamalari"""
    payment_details = data['settings']['payment_details']
    
    text = f"""
💰 *To'lov Sozlamalari*

💳 Premium narxi: {data['settings']['premium_price']:,} {data['settings']['currency']}
👥 Referal talabi: {data['settings']['min_referrals']} ta

📋 *Joriy to'lov rekvizitlari:*
{payment_details}"""

    keyboard = [
        [InlineKeyboardButton("✏️ To'lov Rekvizitlarini Tahrirlash", callback_data="admin_edit_payment")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def edit_payment_details(query, context: ContextTypes.DEFAULT_TYPE):
    """To'lov rekvizitlarini tahrirlash"""
    context.user_data['editing_payment'] = True
    
    text = """
✏️ *To'lov Rekvizitlarini Tahrirlash*

Yangi to'lov rekvizitlarini yuboring.

*Format:*
