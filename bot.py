import os
import json
import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Bot tokeni
TOKEN = "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g"

# Admin ID
ADMIN_ID = 7633561058

# Ma'lumotlarni saqlash fayli
DATA_FILE = "data.json"

# Bukmekerlar havolalari
BUKMAKER_LINKS = {
    "1xbet": "https://1xbet.com",
    "melbet": "https://melbet.com", 
    "dbbet": "https://dbbet.com"
}

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
            "description": "🎯 Bugungi Ishonchli Kuponlar",
            "active": True,
            "coupon_codes": {
                "1xbet": "",
                "melbet": "",
                "dbbet": ""
            }
        },
        "premium": {
            "date": "",
            "matches": [],
            "description": "💎 Premium Ekskluziv Kuponlar",
            "active": True,
            "coupon_codes": {
                "1xbet": "",
                "melbet": "",
                "dbbet": ""
            }
        }
    },
    "settings": {
        "min_referrals": 10,
        "premium_price": 100,
        "currency": "so'm",
        "payment_details": "💳 *To'lov qilish uchun:*\n\n🏦 **Click:** `1234 5678 9012 3456`\n📱 **Payme:** `+998901234567`\n💳 **Uzumbank:** `8600 1234 5678 9012`\n\n✅ To'lov qilgach, chek skrinshotini shu yerga yuboring."
    },
    "stats": {
        "total_users": 0,
        "premium_users": 0
    },
    "payments": {}  # Yangi: To'lovlar ma'lumotlari
}

def load_data():
    """Ma'lumotlarni yuklash"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data

def save_data(data):
    """Ma'lumotlarni saqlash"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Saqlash xatosi: {e}")
        return False

# Ma'lumotlarni yuklash
data = load_data()

def is_admin(user_id):
    return user_id == ADMIN_ID

def is_premium(user_id):
    user_data = data['users'].get(str(user_id), {})
    return user_data.get('premium', False)

def get_user_referrals(user_id):
    user_data = data['users'].get(str(user_id), {})
    return user_data.get('referrals', 0)

def generate_coupon_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_payment_id():
    return ''.join(random.choices(string.digits, k=6))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Yangi foydalanuvchi
    if str(user_id) not in data['users']:
        data['users'][str(user_id)] = {
            'name': user.first_name,
            'referrals': 0,
            'premium': False,
            'joined_date': str(update.message.date)
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
            except:
                pass

    # Chiroyli va 3 qatorli tugmalar
    keyboard = [
        # 1-qator: Asosiy kuponlar
        [
            InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons"),
            InlineKeyboardButton("💎 Premium Kuponlar", callback_data="premium_coupons")
        ],
        # 2-qator: Referal va ulashish
        [
            InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link"),
            InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")
        ],
        # 3-qator: Yordam va to'lov
        [
            InlineKeyboardButton("💳 Premium Sotib Olish", callback_data="buy_premium"),
            InlineKeyboardButton("ℹ️ Yordam", callback_data="help")
        ]
    ]
    
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Chiroyli va ishonarli start xabari
    welcome_text = f"""
🎉 *Salom {user.first_name}!* 👋

⚽ *Futbol Kuponlari Botiga Xush Kelibsiz!*

📊 *Har kuni yangilanadigan ishonchli kuponlar:*
• ⚽ **Kunlik bepul kuponlar**
• 💎 **Premium ekskluziv bashoratlar** 
• 📈 **Yuqori daromadli stavkalar**

🎯 *Bizning afzalliklarimiz:*
✅ Kunlik yangilanish
✅ 85-95% ishonchlilik
✅ Professional tahlillar
✅ Tez natijalar

💰 *Premium imkoniyatlari:*
• 10 ta referal yoki 100 so'm
• Ekskluziv kuponlar
• Statistik tahlillar
• Shaxsiy qo'llab-quvvatlash

*Botdan to'liq foydalanish uchun quyidagi tugmalardan foydalaning!* 🚀
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "today_coupons":
        await send_today_coupons(query)
    elif query.data == "premium_coupons":
        await handle_premium_coupons(query, user_id)
    elif query.data == "get_referral_link":
        await show_referral_link(query, user_id)
    elif query.data == "share_referral":
        await share_referral_link(query, user_id)
    elif query.data == "buy_premium":
        await show_premium_payment(query, user_id)
    elif query.data == "help":
        await show_help(query)
    elif query.data == "back":
        await back_to_main(query)
    elif query.data == "back_to_coupons":
        await back_to_coupons(query)
    elif query.data == "admin":
        if is_admin(user_id):
            await show_admin_panel(query)
        else:
            await query.message.reply_text("❌ Siz admin emassiz!")
    elif query.data == "admin_add_coupon":
        await show_coupon_type_selection(query)
    elif query.data == "admin_toggle_coupons":
        await toggle_coupons_selection(query)
    elif query.data == "admin_clear_coupons":
        await clear_coupons_selection(query)
    elif query.data == "admin_edit_codes":
        await edit_coupon_codes_selection(query)
    elif query.data == "admin_payment_settings":
        await show_payment_settings(query)
    elif query.data == "admin_pending_payments":
        await show_pending_payments(query)
    elif query.data.startswith("add_"):
        coupon_type = query.data.replace("add_", "")
        await start_adding_coupon(query, context, coupon_type)
    elif query.data.startswith("clear_"):
        coupon_type = query.data.replace("clear_", "")
        await clear_specific_coupons(query, coupon_type)
    elif query.data.startswith("edit_codes_"):
        coupon_type = query.data.replace("edit_codes_", "")
        await start_editing_codes(query, context, coupon_type)
    elif query.data.startswith("toggle_"):
        coupon_type = query.data.replace("toggle_", "")
        await toggle_specific_coupons(query, coupon_type)
    elif query.data == "get_free_premium":
        await activate_free_premium(query, user_id)
    elif query.data.startswith("bet_"):
        await show_bet_platform(query, query.data.replace("bet_", ""))
    elif query.data == "upload_screenshot":
        await request_screenshot(query, user_id)
    elif query.data.startswith("approve_"):
        payment_id = query.data.replace("approve_", "")
        await approve_payment(query, payment_id)
    elif query.data.startswith("reject_"):
        payment_id = query.data.replace("reject_", "")
        await reject_payment(query, payment_id)

async def send_today_coupons(query):
    today_coupons = data['coupons']['today']
    
    if not today_coupons['active'] or not today_coupons['matches']:
        await query.edit_message_text(
            "📭 *Hozircha kuponlar mavjud emas*\n\n"
            "Kuponlar tez orada yangilanadi. Iltimos, keyinroq tekshiring! 🔄",
            parse_mode='Markdown'
        )
        return
    
    coupon_text = f"🎯 *{today_coupons['description']}*\n\n"
    coupon_text += f"📅 **Sana:** {today_coupons['date']}\n\n"
    
    # Har bir bukmeker uchun kodlar
    coupon_text += "🔑 *Kupon Kodlari:*\n"
    coupon_text += f"• 1xBet: `{today_coupons['coupon_codes'].get('1xbet', 'Kod mavjud emas')}`\n"
    coupon_text += f"• MelBet: `{today_coupons['coupon_codes'].get('melbet', 'Kod mavjud emas')}`\n"
    coupon_text += f"• DB Bet: `{today_coupons['coupon_codes'].get('dbbet', 'Kod mavjud emas')}`\n\n"
    
    coupon_text += "---\n\n"
    
    for i, match in enumerate(today_coupons['matches'], 1):
        coupon_text += f"*{i}. {match['time']} - {match['league']}*\n"
        coupon_text += f"🏆 `{match['teams']}`\n"
        coupon_text += f"🎯 **Bashorat:** `{match['prediction']}`\n"
        coupon_text += f"📊 **Koeffitsient:** `{match['odds']}`\n"
        coupon_text += f"💎 **Ishonch:** {match['confidence']}\n\n"
    
    # Umumiy koeffitsient
    total_odds = 1.0
    for match in today_coupons['matches']:
        try:
            total_odds *= float(match['odds'])
        except:
            pass
    
    coupon_text += f"💰 **Umumiy koeffitsient:** `{total_odds:.2f}` 🚀\n\n"
    coupon_text += "⏰ *Eslatma:* Stavkalarni o'yin boshlanishidan oldin qo'ying!\n"
    
    # Bukmekerlar tugmalari qo'shildi
    keyboard = [
        # 1-qator: Bukmekerlar
        [
            InlineKeyboardButton("🎰 1xBet", callback_data="bet_1xbet"),
            InlineKeyboardButton("🎯 MelBet", callback_data="bet_melbet"),
            InlineKeyboardButton("💰 DB Bet", callback_data="bet_dbbet")
        ],
        # 2-qator: Boshqa tugmalar
        [InlineKeyboardButton("🔗 Do'stlarni Taklif Qilish", callback_data="share_referral")],
        [InlineKeyboardButton("💎 Premium Kuponlar", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(coupon_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_premium_coupons(query, user_id):
    if is_premium(user_id):
        await send_premium_coupons(query)
    else:
        await show_premium_offer(query, user_id)

async def send_premium_coupons(query):
    premium_coupons = data['coupons']['premium']
    
    if not premium_coupons['active'] or not premium_coupons['matches']:
        await query.edit_message_text(
            "💎 *Premium kuponlar tez orada yangilanadi!*\n\n"
            "Biz yuqori daromadli ekskluziv kuponlar ustida ishlamoqdamiz. 🔄",
            parse_mode='Markdown'
        )
        return
    
    premium_text = f"💎 *{premium_coupons['description']}*\n\n"
    premium_text += f"📅 **Sana:** {premium_coupons['date']}\n\n"
    
    # Har bir bukmeker uchun kodlar
    premium_text += "🔑 *Premium Kupon Kodlari:*\n"
    premium_text += f"• 1xBet: `{premium_coupons['coupon_codes'].get('1xbet', 'Kod mavjud emas')}`\n"
    premium_text += f"• MelBet: `{premium_coupons['coupon_codes'].get('melbet', 'Kod mavjud emas')}`\n"
    premium_text += f"• DB Bet: `{premium_coupons['coupon_codes'].get('dbbet', 'Kod mavjud emas')}`\n\n"
    
    premium_text += "---\n\n"
    
    for i, match in enumerate(premium_coupons['matches'], 1):
        premium_text += f"*{i}. {match['time']} - {match['league']}*\n"
        premium_text += f"🏆 `{match['teams']}`\n"
        premium_text += f"🎯 **Bashorat:** `{match['prediction']}`\n"
        premium_text += f"📊 **Koeffitsient:** `{match['odds']}`\n"
        premium_text += f"💎 **Ishonch:** {match['confidence']}\n\n"
    
    # Umumiy koeffitsient
    total_odds = 1.0
    for match in premium_coupons['matches']:
        try:
            total_odds *= float(match['odds'])
        except:
            pass
    
    premium_text += f"💰 **Umumiy koeffitsient:** `{total_odds:.2f}` 💰\n\n"
    premium_text += "✅ *Premium a'zo bo'lganingiz uchun rahmat!*\n"
    
    # Bukmekerlar tugmalari qo'shildi
    keyboard = [
        # 1-qator: Bukmekerlar
        [
            InlineKeyboardButton("🎰 1xBet", callback_data="bet_1xbet"),
            InlineKeyboardButton("🎯 MelBet", callback_data="bet_melbet"),
            InlineKeyboardButton("💰 DB Bet", callback_data="bet_dbbet")
        ],
        # 2-qator: Boshqa tugmalar
        [InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")],
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(premium_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_bet_platform(query, platform):
    """Bukmeker platformasini ko'rsatish"""
    platform_names = {
        "1xbet": "1xBet",
        "melbet": "MelBet", 
        "dbbet": "DB Bet"
    }
    
    platform_name = platform_names.get(platform, platform)
    platform_link = BUKMAKER_LINKS.get(platform, "")
    
    # Kupon kodini olish
    coupon_type = "today"  # Default bugungi kupon
    if "premium" in query.message.text.lower():
        coupon_type = "premium"
    
    coupon_code = data['coupons'][coupon_type]['coupon_codes'].get(platform, "Kod mavjud emas")
    
    text = f"""
🎰 *{platform_name}*

🔑 **Kupon Kodi:** `{coupon_code}`

📱 **Platformaga o'tish uchun quyidagi tugmalardan foydalaning:**
"""
    
    # Shaffof tugmalar qatorlari
    keyboard = [
        # 1-qator: Asosiy sayt va APK yuklash
        [
            InlineKeyboardButton("🌐 Saytga O'tish", url=platform_link),
            InlineKeyboardButton("📱 APK Yuklash", url="https://t.me/bonusliapkbot")
        ],
        # 2-qator: Orqaga tugmasi
        [InlineKeyboardButton("🔙 Kuponlarga Qaytish", callback_data="back_to_coupons")]
    ]
    
    text += f"\n💡 *Qanday foydalanish:*\n"
    text += f"1. Saytga o'ting yoki APK yuklang\n"
    text += f"2. Ro'yxatdan o'ting/Hisobingizga kiring\n"
    text += f"3. Kupon kodini kiriting: `{coupon_code}`\n"
    text += f"4. Kuponni qo'shing va stavka qiling!\n\n"
    text += f"✅ *Eslatma:* Kupon kodini faqat bir marta ishlatish mumkin."
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def back_to_coupons(query):
    """Kuponlar sahifasiga qaytish"""
    if "premium" in query.message.text.lower():
        await send_premium_coupons(query)
    else:
        await send_today_coupons(query)

async def show_premium_offer(query, user_id):
    referrals_count = get_user_referrals(user_id)
    required_refs = data['settings']['min_referrals']
    
    text = f"""
💎 *PREMIUM KUPONLARGA KIRISH*

📊 **Sizning holatingiz:**
👥 Referallar: {referrals_count}/{required_refs} ta
💰 To'lov: {data['settings']['premium_price']} {data['settings']['currency']}

🎯 *Premium afzalliklari:*
• ✅ Yuqori daromadli kuponlar
• ✅ Ekskluziv bashoratlar  
• ✅ 90-95% ishonchlilik
• ✅ Statistik tahlillar
• ✅ Shaxsiy qo'llab-quvvatlash

💡 *Premium olish usullari:*
"""
    
    keyboard = []
    
    if referrals_count >= required_refs:
        keyboard.append([InlineKeyboardButton("🎁 BEPUL PREMIUM OCHISH", callback_data="get_free_premium")])
        text += f"1. 🎁 **{required_refs} ta referal** - Bepul premium!\n"
    else:
        text += f"1. 👥 **{required_refs} ta referal** to'plang\n"
    
    text += f"2. 💳 **{data['settings']['premium_price']} {data['settings']['currency']}** to'lov qiling\n\n"
    text += "💎 Premium orqali yuqori daromadli kuponlarga ega bo'ling!"
    
    keyboard.extend([
        [InlineKeyboardButton("👥 Referal Orqali", callback_data="get_referral_link")],
        [InlineKeyboardButton("💳 To'lov Orqali", callback_data="buy_premium")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_premium_payment(query, user_id):
    """To'lov sahifasi"""
    payment_details = data['settings']['payment_details']
    
    text = f"""
💳 *PREMIUM A'ZOLIK*

💰 **Narxi:** {data['settings']['premium_price']} {data['settings']['currency']}

{payment_details}

📋 *Qadamlar:*
1. Yuqoridagi raqamlarga to'lov qiling
2. Chek skrinshotini oling
3. Quyidagi tugma orqali skrinshotni yuboring
4. Admin tekshirib, Premium ochadi!

⏰ *Eslatma:* To'lov qilgach, tez orada premium ochiladi.
"""
    
    keyboard = [
        [InlineKeyboardButton("📸 Skrinshot Yuborish", callback_data="upload_screenshot")],
        [InlineKeyboardButton("👥 Referal Orqali Olish", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔗 Do'stlarni Taklif Qilish", callback_data="share_referral")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def request_screenshot(query, user_id):
    """Skrinshot yuborish so'rovini yuborish"""
    text = """
📸 *Skrinshot Yuborish*

Endi to'lov chekining skrinshotini shu yerga yuboring:

📎 *Eslatmalar:*
• Rasm yoki skrinshot bo'lishi kerak
• To'lov summasi va vaqti ko'rinishi kerak
• Hisob raqami ko'rinishi kerak

🕐 *Tekshirish vaqti:* 1-24 soat

✅ Tekshirib bo'lingach, sizga Premium ochiladi!
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="buy_premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'lov skrinshotini qabul qilish"""
    user_id = update.effective_user.id
    
    if update.message.photo:
        # Rasm qabul qilindi
        photo = update.message.photo[-1]
        payment_id = generate_payment_id()
        
        # To'lov ma'lumotlarini saqlash
        data['payments'][payment_id] = {
            'user_id': user_id,
            'user_name': update.effective_user.first_name,
            'photo_id': photo.file_id,
            'status': 'pending',
            'date': str(update.message.date),
            'amount': data['settings']['premium_price'],
            'currency': data['settings']['currency']
        }
        save_data(data)
        
        # Adminlarga xabar berish
        await notify_admins_about_payment(payment_id, context)
        
        await update.message.reply_text(
            f"✅ *Skrinshot qabul qilindi!*\n\n"
            f"🆔 **To'lov ID:** `{payment_id}`\n"
            f"💰 **Summa:** {data['settings']['premium_price']} {data['settings']['currency']}\n\n"
            f"⏳ *Holat:* Admin tekshiruvi kutilmoqda\n"
            f"🕐 Tekshirish vaqti: 1-24 soat\n\n"
            f"Tasdiqlanganidan so'ng Premium avtomatik ochiladi!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Iltimos, to'lov chekining *skrinshotini* (rasm) yuboring!",
            parse_mode='Markdown'
        )

async def notify_admins_about_payment(payment_id, context: ContextTypes.DEFAULT_TYPE):
    """Adminlarga yangi to'lov haqida xabar berish"""
    payment = data['payments'][payment_id]
    user_id = payment['user_id']
    user_name = payment['user_name']
    
    text = f"""
🆕 *YANGI TO'LOV SO'ROVI*

🆔 **To'lov ID:** `{payment_id}`
👤 **Foydalanuvchi:** {user_name} (ID: {user_id})
💰 **Summa:** {payment['amount']} {payment['currency']}
📅 **Sana:** {payment['date']}

Tasdiqlash yoki rad etish uchun quyidagi tugmalardan foydalaning:
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{payment_id}"),
            InlineKeyboardButton("❌ Rad Etish", callback_data=f"reject_{payment_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Adminlarga xabar yuborish
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=payment['photo_id'],
            caption=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Adminga xabar yuborishda xato: {e}")

async def approve_payment(query, payment_id):
    """To'lovni tasdiqlash"""
    if payment_id in data['payments']:
        payment = data['payments'][payment_id]
        user_id = payment['user_id']
        
        # Premium ochish
        data['users'][str(user_id)]['premium'] = True
        data['payments'][payment_id]['status'] = 'approved'
        data['stats']['premium_users'] += 1
        save_data(data)
        
        # Foydalanuvchiga xabar
        try:
            await query.bot.send_message(
                chat_id=user_id,
                text=f"""
🎉 *TABRIKLAYMIZ!*

✅ To'lovingiz tasdiqlandi!
💎 Premium a'zoligingiz faollashtirildi!

Endi siz Premium kuponlardan foydalanishingiz mumkin.

📊 **Premium afzalliklari:**
• Yuqori daromadli kuponlar
• Ekskluziv bashoratlar
• 90-95% ishonchlilik
• Statistik tahlillar

🚀 Premium kuponlarni ko'rish uchun /start buyrug'idan foydalaning!
""",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Foydalanuvchiga xabar yuborishda xato: {e}")
        
        await query.edit_message_text(
            f"✅ *To'lov tasdiqlandi!*\n\n"
            f"🆔 To'lov ID: `{payment_id}`\n"
            f"👤 Foydalanuvchi: {payment['user_name']}\n"
            f"💰 Summa: {payment['amount']} {payment['currency']}\n\n"
            f"Premium muvaffaqiyatli ochildi!",
            parse_mode='Markdown'
        )
    else:
        await query.answer("❌ To'lov topilmadi!")

async def reject_payment(query, payment_id):
    """To'lovni rad etish"""
    if payment_id in data['payments']:
        payment = data['payments'][payment_id]
        user_id = payment['user_id']
        
        data['payments'][payment_id]['status'] = 'rejected'
        save_data(data)
        
        # Foydalanuvchiga xabar
        try:
            await query.bot.send_message(
                chat_id=user_id,
                text=f"""
❌ *To'lov rad etildi*

To'lov chekingiz quyidagi sabablarga ko'ra rad etildi:
• Noto'g'ri skrinshot
• Summa noto'g'ri
• Boshqa muammolar

Iltimos, qaytadan to'lov qiling va to'g'ri skrinshot yuboring.

📞 Yordam kerak bo'lsa: @admin
""",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Foydalanuvchiga xabar yuborishda xato: {e}")
        
        await query.edit_message_text(
            f"❌ *To'lov rad etildi!*\n\n"
            f"🆔 To'lov ID: `{payment_id}`\n"
            f"👤 Foydalanuvchi: {payment['user_name']}\n"
            f"💰 Summa: {payment['amount']} {payment['currency']}",
            parse_mode='Markdown'
        )
    else:
        await query.answer("❌ To'lov topilmadi!")

async def show_pending_payments(query):
    """Kutilayotgan to'lovlarni ko'rsatish"""
    pending_payments = {k: v for k, v in data['payments'].items() if v['status'] == 'pending'}
    
    if not pending_payments:
        text = "📭 *Kutilayotgan to'lovlar yo'q*"
    else:
        text = f"⏳ *Kutilayotgan To'lovlar:* {len(pending_payments)} ta\n\n"
        for payment_id, payment in list(pending_payments.items())[:10]:  # Faqat 10 tasini ko'rsatish
            text += f"🆔 `{payment_id}` - {payment['user_name']} - {payment['amount']} {payment['currency']}\n"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
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

Siz muvaffaqiyatli Premium a'zoga aylandingiz! 🎊

💎 *Endi siz quyidagi imkoniyatlarga ega bo'ldingiz:*
• ✅ Yuqori daromadli kuponlar
• ✅ Ekskluziv bashoratlar
• ✅ 90-95% ishonchlilik
• ✅ Statistik tahlillar
• ✅ Shaxsiy qo'llab-quvvatlash

🚀 Endi Premium kuponlardan foydalanishingiz mumkin!
"""
        
        keyboard = [
            [InlineKeyboardButton("💎 Premium Kuponlar", callback_data="premium_coupons")],
            [InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
    else:
        text = f"""
❌ *Hozircha Premium ocholmaysiz!*

📊 **Sizning holatingiz:**
👥 Referallar: {referrals_count}/{required_refs} ta

📤 Ko'proq do'stlaringizni taklif qiling va Premiumga ega bo'ling!
"""
        
        keyboard = [
            [InlineKeyboardButton("👥 Referal Havola", callback_data="get_referral_link")],
            [InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="premium_coupons")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ... (qolgan funksiyalar o'zgarmaydi, faqat admin paneliga yangi tugma qo'shildi)

async def show_admin_panel(query):
    today_status = "🟢 Faol" if data['coupons']['today']['active'] else "🔴 Nofaol"
    premium_status = "🟢 Faol" if data['coupons']['premium']['active'] else "🔴 Nofaol"
    today_count = len(data['coupons']['today']['matches'])
    premium_count = len(data['coupons']['premium']['matches'])
    
    pending_payments = sum(1 for p in data['payments'].values() if p['status'] == 'pending')
    
    text = f"""
👑 *ADMIN PANELI*

📊 **Bot Statistikasi:**
👥 Foydalanuvchilar: {data['stats']['total_users']} ta
💎 Premium foydalanuvchilar: {data['stats']['premium_users']} ta
⏳ Kutilayotgan to'lovlar: {pending_payments} ta

⚽ **Kuponlar Holati:**
📅 Bugungi kuponlar: {today_status} ({today_count} ta)
💎 Premium kuponlar: {premium_status} ({premium_count} ta)

🎯 **Admin Imkoniyatlari:**
"""
    
    keyboard = [
        [InlineKeyboardButton("➕ Kupon Qo'shish", callback_data="admin_add_coupon")],
        [InlineKeyboardButton("🔑 Kupon Kodlarini O'zgartirish", callback_data="admin_edit_codes")],
        [InlineKeyboardButton("🔄 Faol/O'chirish", callback_data="admin_toggle_coupons")],
        [InlineKeyboardButton("🗑️ Kuponlarni Tozalash", callback_data="admin_clear_coupons")],
        [InlineKeyboardButton("💳 To'lov Sozlamalari", callback_data="admin_payment_settings")],
        [InlineKeyboardButton("⏳ Kutilayotgan To'lovlar", callback_data="admin_pending_payments")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ... (qolgan funksiyalar bir xil)

def main():
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handlerlar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
        app.add_handler(MessageHandler(filters.PHOTO, handle_payment_screenshot))
        
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        print("🤖 Bot ishlayapti...")
        print(f"👑 Admin ID: {ADMIN_ID}")
        print("🎰 Bukmeker tugmalari yangilandi!")
        print("💳 To'lov tizimi qo'shildi!")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
