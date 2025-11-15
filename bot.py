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
        "payment_details": "💳 *To'lov qilish uchun:*\n\n🏦 **HUMO:** `9860356622837710`\n📱 **Payme:** `mavjud emas`\n💳 **Uzumbank visa:** `4916990318695001`\n\n✅ To'lov qilgach, chek skrinshotini @baxtga_olga ga yuboring."
    },
    "stats": {
        "total_users": 0,
        "premium_users": 0
    }
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Yangi foydalanuvchi
    if str(user_id) not in data['users']:
        data['users'][str(user_id)] = {
            'name': user.first_name,
            'referrals': 0,
            'premium': False
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
    
    # Har bir o'yin uchun alohida koeffitsient
    for i, match in enumerate(today_coupons['matches'], 1):
        coupon_text += f"*{i}. {match['time']} - {match['league']}*\n"
        coupon_text += f"🏆 `{match['teams']}`\n"
        coupon_text += f"🎯 **Bashorat:** `{match['prediction']}`\n"
        coupon_text += f"📊 **Koeffitsient:** `{match['odds']}`\n"
        coupon_text += f"💎 **Ishonch:** {match['confidence']}\n\n"
    
    # Umumiy koeffitsientni hisoblash
    total_odds = 1.0
    for match in today_coupons['matches']:
        try:
            total_odds *= float(match['odds'])
        except:
            pass
    
    # Umumiy koeffitsientni alohida qator sifatida ko'rsatish
    coupon_text += "---\n\n"
    coupon_text += f"💰 *Umumiy Koeffitsient:* `{total_odds:.2f}` 🚀\n\n"
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
    
    # Har bir o'yin uchun alohida koeffitsient
    for i, match in enumerate(premium_coupons['matches'], 1):
        premium_text += f"*{i}. {match['time']} - {match['league']}*\n"
        premium_text += f"🏆 `{match['teams']}`\n"
        premium_text += f"🎯 **Bashorat:** `{match['prediction']}`\n"
        premium_text += f"📊 **Koeffitsient:** `{match['odds']}`\n"
        premium_text += f"💎 **Ishonch:** {match['confidence']}\n\n"
    
    # Umumiy koeffitsientni hisoblash
    total_odds = 1.0
    for match in premium_coupons['matches']:
        try:
            total_odds *= float(match['odds'])
        except:
            pass
    
    # Umumiy koeffitsientni alohida qator sifatida ko'rsatish
    premium_text += "---\n\n"
    premium_text += f"💰 *Umumiy Koeffitsient:* `{total_odds:.2f}` 💰\n\n"
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
3. @baxtga_olga ga yuboring
4. Premium ochiladi!

⏰ *Eslatma:* To'lov qilgach, tez orada premium ochiladi.
"""
    
    keyboard = [
        [InlineKeyboardButton("👥 Referal Orqali Olish", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔗 Do'stlarni Taklif Qilish", callback_data="share_referral")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
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

async def show_referral_link(query, user_id):
    bot_username = (await query.message._bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
    referrals_count = get_user_referrals(user_id)
    required_refs = data['settings']['min_referrals']
    
    text = f"""
📤 *REFERAL HAVOLANGIZ*

`{ref_link}`

📊 **Sizning statistikangiz:**
👥 Referallar: {referrals_count}/{required_refs} ta
🎯 Maqsad: {required_refs} ta (Bepul Premium)

💡 **Qanday ishlatish:**
1. Havolani nusxalang
2. Do'stlaringizga yuboring
3. Har bir yangi foydalanuvchi +1 referal
4. {required_refs} ta referal = Bepul Premium!

🔗 Havolani ko'proq odamga yuboring, tezroq Premiumga ega bo'ling!
"""
    
    keyboard = [
        [InlineKeyboardButton("🔗 TELEGRAMDA ULASHISH", callback_data="share_referral")],
        [InlineKeyboardButton("💎 Premium Olish", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def share_referral_link(query, user_id):
    """Havolani ulashish"""
    bot_username = (await query.message._bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
    
    share_text = f"""🎯 *Futbol Kuponlari Boti*

⚽ Kunlik bepul kuponlar
💎 Premium ekskluziv bashoratlar
💰 Yuqori daromadli stavkalar

🎁 10 ta referal yoki 100 so'm to'lov bilan Premium oching!

Botga kirib, daromad olishni boshlang:
{ref_link}"""

    keyboard = [
        [InlineKeyboardButton("📤 TELEGRAMDA ULASHISH", url=f"https://t.me/share/url?url={ref_link}&text=🎯 Futbol Kuponlari Boti - Kunlik bepul kuponlar va premium bashoratlar!")],
        [InlineKeyboardButton("👥 Referal Statistikasi", callback_data="get_referral_link")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔗 *Havolani quyidagi tugma orqali osongina ulashing:*\n\n"
        "Tugmani bosing va do'stlaringizga yuboring!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_help(query):
    text = """
ℹ️ *BOTDAN FOYDALANISH QO'LLANMASI*

⚽ *Kuponlar:*
• **Bugungi kuponlar** - Kunlik yangilanadigan bepul bashoratlar
• **Premium kuponlar** - Yuqori daromadli ekskluziv kuponlar

💎 *Premium Olish:*
• **10 ta referal** to'plang
• **100 so'm** to'lov qiling
• Premium kuponlarga ega bo'ling

🔗 *Referal Tizimi:*
• Do'stlaringizni taklif qiling
• Har bir referal sizga +1 ball
• 10 ta referal = Bepul Premium

📞 *Qo'llab-quvvatlash:*
Murojaatlar uchun: @baxtga_olga
🚀 *Bot har kuni yangilanadi va yangi kuponlar qo'shiladi!*
"""
    
    keyboard = [
        [InlineKeyboardButton("🔗 Havolani Ulashish", callback_data="share_referral")],
        [InlineKeyboardButton("💎 Premium Olish", callback_data="premium_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ADMIN FUNCTIONS
async def show_admin_panel(query):
    today_status = "🟢 Faol" if data['coupons']['today']['active'] else "🔴 Nofaol"
    premium_status = "🟢 Faol" if data['coupons']['premium']['active'] else "🔴 Nofaol"
    today_count = len(data['coupons']['today']['matches'])
    premium_count = len(data['coupons']['premium']['matches'])
    
    text = f"""
👑 *ADMIN PANELI*

📊 **Bot Statistikasi:**
👥 Foydalanuvchilar: {data['stats']['total_users']} ta
💎 Premium foydalanuvchilar: {sum(1 for user in data['users'].values() if user.get('premium', False))} ta

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
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_coupon_type_selection(query):
    text = "📋 *Qaysi kupon turiga kupon qo'shmoqchisiz?*"
    
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kupon", callback_data="add_today")],
        [InlineKeyboardButton("💎 Premium Kupon", callback_data="add_premium")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def start_adding_coupon(query, context: ContextTypes.DEFAULT_TYPE, coupon_type: str):
    context.user_data['adding_coupon'] = True
    context.user_data['coupon_type'] = coupon_type
    
    coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
    
    await query.edit_message_text(
        f"✏️ *{coupon_name} Kupon Qo'shish*\n\n"
        "Quyidagi formatda ma'lumot yuboring:\n\n"
        "`sana|vaqt|liga|jamoalar|bashorat|koeffitsient|ishonch|1xbet_kodi|melbet_kodi|dbbet_kodi`\n\n"
        "*Misol:*\n"
        "`2024-01-20|20:00|Premier League|Man City vs Arsenal|1X|1.50|85%|1XBET123|MELBET456|DBBET789`\n\n"
        "📝 *Eslatma:* Bir nechta kupon qo'shish uchun har birini alohida yuboring.",
        parse_mode='Markdown'
    )

async def toggle_coupons_selection(query):
    text = "🔄 *Qaysi kuponlarni o'zgartirmoqchisiz?*"
    
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="toggle_today")],
        [InlineKeyboardButton("💎 Premium Kuponlar", callback_data="toggle_premium")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def toggle_specific_coupons(query, coupon_type: str):
    data['coupons'][coupon_type]['active'] = not data['coupons'][coupon_type]['active']
    save_data(data)
    
    coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
    status = "faol" if data['coupons'][coupon_type]['active'] else "nofaol"
    await query.message.reply_text(f"✅ {coupon_name} kuponlar {status} holatga o'zgartirildi!")
    await show_admin_panel(query)

async def clear_coupons_selection(query):
    text = "🗑️ *Qaysi kuponlarni tozalamoqchisiz?*"
    
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="clear_today")],
        [InlineKeyboardButton("💎 Premium Kuponlar", callback_data="clear_premium")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def clear_specific_coupons(query, coupon_type: str):
    data['coupons'][coupon_type]['matches'] = []
    # Yangi kodlar yaratish
    data['coupons'][coupon_type]['coupon_codes'] = {
        "1xbet": generate_coupon_code(),
        "melbet": generate_coupon_code(),
        "dbbet": generate_coupon_code()
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
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def start_editing_codes(query, context: ContextTypes.DEFAULT_TYPE, coupon_type: str):
    context.user_data['editing_codes'] = True
    context.user_data['coupon_type'] = coupon_type
    
    current_codes = data['coupons'][coupon_type]['coupon_codes']
    coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
    
    text = f"""
✏️ *{coupon_name} Kupon Kodlarini O'zgartirish*

🆔 **Joriy kodlar:**
• 1xBet: `{current_codes.get('1xbet', 'Mavjud emas')}`
• MelBet: `{current_codes.get('melbet', 'Mavjud emas')}`
• DB Bet: `{current_codes.get('dbbet', 'Mavjud emas')}`

Yangi kodlarni quyidagi formatda yuboring:

`1xbet_kodi|melbet_kodi|dbbet_kodi`

*Misol:*
`1XBET123|MELBET456|DBBET789`
"""
    
    await query.edit_message_text(text, parse_mode='Markdown')

async def show_payment_settings(query):
    payment_details = data['settings']['payment_details']
    
    text = f"""
💳 *TO'LOV SOZLAMALARI*

💰 **Premium narxi:** {data['settings']['premium_price']} {data['settings']['currency']}
👥 **Referal talabi:** {data['settings']['min_referrals']} ta

📋 **Joriy to'lov rekvizitlari:**
{payment_details}

To'lov rekvizitlarini o'zgartirish uchun yangi matn yuboring.
"""
    
    keyboard = [
        [InlineKeyboardButton("✏️ Rekvizitlarni Tahrirlash", callback_data="edit_payment_details")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    # Kupon qo'shish rejimi
    if context.user_data.get('adding_coupon'):
        await process_coupon_addition(update, context)
        return
    
    # Kodlarni o'zgartirish rejimi
    if context.user_data.get('editing_codes'):
        await process_codes_edit(update, context)
        return
    
    # To'lov rekvizitlarini tahrirlash
    if context.user_data.get('editing_payment'):
        await process_payment_edit(update, context)
        return

async def process_coupon_addition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_text = update.message.text
        parts = message_text.split('|')
        
        if len(parts) < 10:
            await update.message.reply_text("❌ Noto'g'ri format! 10 ta parametr kerak.")
            return
        
        date, time, league, teams, prediction, odds, confidence, code_1xbet, code_melbet, code_dbbet = parts[:10]
        coupon_type = context.user_data.get('coupon_type', 'today')
        
        new_match = {
            'time': time.strip(),
            'league': league.strip(),
            'teams': teams.strip(),
            'prediction': prediction.strip(),
            'odds': odds.strip(),
            'confidence': confidence.strip()
        }
        
        # Birinchi kupon qo'shilganda kodlarni saqlash
        if not data['coupons'][coupon_type]['matches']:
            data['coupons'][coupon_type]['coupon_codes'] = {
                "1xbet": code_1xbet.strip(),
                "melbet": code_melbet.strip(),
                "dbbet": code_dbbet.strip()
            }
        
        data['coupons'][coupon_type]['matches'].append(new_match)
        data['coupons'][coupon_type]['date'] = date.strip()
        save_data(data)
        
        coupon_codes = data['coupons'][coupon_type]['coupon_codes']
        coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
        matches_count = len(data['coupons'][coupon_type]['matches'])
        
        await update.message.reply_text(
            f"✅ *{coupon_name} kupon qo'shildi!*\n\n"
            f"🔑 **Kupon Kodlari:**\n"
            f"• 1xBet: `{coupon_codes.get('1xbet', '')}`\n"
            f"• MelBet: `{coupon_codes.get('melbet', '')}`\n"
            f"• DB Bet: `{coupon_codes.get('dbbet', '')}`\n\n"
            f"📊 **Jami kuponlar:** {matches_count} ta\n"
            f"📅 **Sana:** {date}\n\n"
            f"Yana kupon qo'shishingiz mumkin yoki /start buyrug'i orqali bosh menyuga qayting.",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")
    
    context.user_data.pop('adding_coupon', None)
    context.user_data.pop('coupon_type', None)

async def process_codes_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_text = update.message.text
        parts = message_text.split('|')
        
        if len(parts) < 3:
            await update.message.reply_text("❌ Noto'g'ri format! 3 ta kod kerak.")
            return
        
        code_1xbet, code_melbet, code_dbbet = parts[:3]
        coupon_type = context.user_data.get('coupon_type', 'today')
        
        # Yangi kodlarni saqlash
        data['coupons'][coupon_type]['coupon_codes'] = {
            "1xbet": code_1xbet.strip(),
            "melbet": code_melbet.strip(),
            "dbbet": code_dbbet.strip()
        }
        save_data(data)
        
        coupon_name = "Bugungi" if coupon_type == "today" else "Premium"
        
        await update.message.reply_text(
            f"✅ *{coupon_name} kupon kodlari yangilandi!*\n\n"
            f"🔑 **Yangi kodlar:**\n"
            f"• 1xBet: `{code_1xbet.strip()}`\n"
            f"• MelBet: `{code_melbet.strip()}`\n"
            f"• DB Bet: `{code_dbbet.strip()}`",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")
    
    context.user_data.pop('editing_codes', None)
    context.user_data.pop('coupon_type', None)

async def process_payment_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_payment_details = update.message.text
        data['settings']['payment_details'] = new_payment_details
        save_data(data)
        
        await update.message.reply_text("✅ To'lov rekvizitlari yangilandi!")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")
    
    context.user_data.pop('editing_payment', None)

async def back_to_main(query):
    user = query.from_user
    user_id = user.id
    
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
    
    await query.edit_message_text(
        "🎯 *Asosiy Menyu*\n\n"
        "Quyidagi tugmalardan foydalanib botdan to'liq foydalaning! 🚀",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handlerlar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
        
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        print("🤖 Bot ishlayapti...")
        print(f"👑 Admin ID: {ADMIN_ID}")
        print("🎰 Bukmeker tugmalari qo'shildi: 1xBet, MelBet, DB Bet")
        print("📊 Koeffitsientlar alohida va umumiy ko'rsatiladi!")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
