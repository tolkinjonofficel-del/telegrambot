import os
import json
import logging
import random
import string
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta

# Bot tokeni
TOKEN = "7454675594:AAE5Obhl2WUxIMYpbw7o31QArwxZr7DQYck"

# Admin ID
ADMIN_ID = 7081746531

# Ma'lumotlarni saqlash fayli
DATA_FILE = "data.json"

# Bukmekerlar havolalari
BUKMAKER_LINKS = {
    "1xbet": "https://reffpa.com/L?tag=d_4147173m_1599c_&site=4147173&ad=1599&r=registration",
    "melbet": "https://refpa42380.com/L?tag=s_4856673m_57037c_&site=4856673&ad=57037", 
    "dbbet": "https://refpa96317.com/L?tag=d_4585917m_11213c_&site=4585917&ad=11213"
}

# Loggerni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Boshlang'ich ma'lumotlar
default_data = {
    "users": {},
    "coupons": {
        "today": {
            "date": "2024-01-20",
            "matches": [
                {
                    "time": "20:00",
                    "league": "Premier League",
                    "teams": "Man City vs Arsenal",
                    "prediction": "1X",
                    "odds": "1.50",
                    "confidence": "85%"
                }
            ],
            "description": "🎯 Bugungi Ishonchli Kuponlar",
            "active": True,
            "coupon_codes": {
                "1xbet": "1XBET123",
                "melbet": "MELBET456",
                "dbbet": "DBBET789"
            }
        },
        "premium": {
            "date": "2024-01-20",
            "matches": [
                {
                    "time": "21:00",
                    "league": "La Liga",
                    "teams": "Real Madrid vs Barcelona",
                    "prediction": "Over 2.5",
                    "odds": "1.80",
                    "confidence": "90%"
                }
            ],
            "description": "💎 Premium Ekskluziv Kuponlar",
            "active": True,
            "coupon_codes": {
                "1xbet": "PREMIUM1X",
                "melbet": "PREMIUMMEL",
                "dbbet": "PREMIUMDB"
            }
        }
    },
    "settings": {
        "min_referrals": 10,
        "premium_price": 100000,
        "currency": "so'm",
        "payment_details": "💳 *To'lov qilish uchun:*\n\n🏦 **HUMO:** `9860356622837710`\n📱 **Payme:** `mavjud emas`\n💳 **Uzumbank visa:** `4916990318695001`\n\n✅ To'lov qilgach, chek skrinshotini @baxtga_olga ga yuboring."
    },
    "stats": {
        "total_users": 0,
        "premium_users": 0,
        "today_users": 0,
        "week_users": 0,
        "month_users": 0
    }
}

def load_data():
    """Ma'lumotlarni yuklash"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ma'lumotlarni yuklash xatosi: {e}")
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

def calculate_user_stats():
    """Foydalanuvchi statistikasini hisoblash"""
    try:
        now = datetime.now()
        today = now.date()
        week_ago = (now - timedelta(days=7)).date()
        month_ago = (now - timedelta(days=30)).date()
        
        today_count = 0
        week_count = 0
        month_count = 0
        
        for user_id, user_data in data['users'].items():
            if 'joined_date' in user_data:
                try:
                    join_date = datetime.fromisoformat(user_data['joined_date']).date()
                    if join_date == today:
                        today_count += 1
                    if join_date >= week_ago:
                        week_count += 1
                    if join_date >= month_ago:
                        month_count += 1
                except Exception as e:
                    logger.error(f"Sanani tahlil qilish xatosi: {e}")
                    continue
        
        data['stats']['today_users'] = today_count
        data['stats']['week_users'] = week_count
        data['stats']['month_users'] = month_count
        save_data(data)
    except Exception as e:
        logger.error(f"Statistika hisoblash xatosi: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"Start bosildi: {user.first_name} (ID: {user_id})")
        
        # Yangi foydalanuvchi
        if str(user_id) not in data['users']:
            data['users'][str(user_id)] = {
                'name': user.first_name,
                'username': user.username,
                'referrals': 0,
                'premium': False,
                'joined_date': str(update.message.date),
                'last_active': str(update.message.date)
            }
            data['stats']['total_users'] += 1
            save_data(data)
            calculate_user_stats()
            logger.info(f"Yangi foydalanuvchi qo'shildi: {user.first_name}")
        else:
            # Faollik vaqtini yangilash
            data['users'][str(user_id)]['last_active'] = str(update.message.date)
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
                        logger.info(f"Yangi referal: {user_id} -> {referrer_id}")
                except Exception as e:
                    logger.error(f"Referal tekshirish xatosi: {e}")

        # Chiroyli va 3 qatorli tugmalar
        keyboard = [
            [
                InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons"),
                InlineKeyboardButton("💎 100% kupon", callback_data="premium_coupons")
            ],
            [
                InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link"),
                InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")
            ],
            [
                InlineKeyboardButton("💳 Premium Sotib Olish", callback_data="buy_premium"),
                InlineKeyboardButton("ℹ️ Yordam", callback_data="help")
            ]
        ]
        
        if is_admin(user_id):
            keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
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
• 10 ta referal yoki 100 000 so'm
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
        
    except Exception as e:
        logger.error(f"Start funksiyasida xato: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qayta urining.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        callback_data = query.data
        
        logger.info(f"Tugma bosildi: {callback_data} (User: {user_id})")
        
        # Foydalanuvchi faolligini yangilash
        if str(user_id) in data['users']:
            data['users'][str(user_id)]['last_active'] = str(query.message.date)
            save_data(data)
        
        # Callback ma'lumotlariga qarab ishlov berish
        if callback_data == "today_coupons":
            await send_today_coupons(query)
        elif callback_data == "premium_coupons":
            await handle_premium_coupons(query, user_id)
        elif callback_data == "get_referral_link":
            await show_referral_link(query, user_id)
        elif callback_data == "share_referral":
            await share_referral_link(query, user_id)
        elif callback_data == "buy_premium":
            await show_premium_payment(query, user_id)
        elif callback_data == "help":
            await show_help(query)
        elif callback_data == "back":
            await back_to_main(query)
        elif callback_data == "back_to_coupons":
            await back_to_coupons(query)
        elif callback_data == "admin":
            if is_admin(user_id):
                await show_admin_panel(query)
            else:
                await query.message.reply_text("❌ Siz admin emassiz!")
        elif callback_data == "admin_add_coupon":
            await show_coupon_type_selection(query)
        elif callback_data == "admin_toggle_coupons":
            await toggle_coupons_selection(query)
        elif callback_data == "admin_clear_coupons":
            await clear_coupons_selection(query)
        elif callback_data == "admin_edit_codes":
            await edit_coupon_codes_selection(query)
        elif callback_data == "admin_payment_settings":
            await show_payment_settings(query)
        elif callback_data == "admin_user_stats":
            await show_user_statistics(query)
        elif callback_data == "admin_broadcast":
            await start_broadcast(query, context)
        elif callback_data == "admin_user_list":
            await show_user_list(query)
        elif callback_data.startswith("user_detail_"):
            user_detail_id = callback_data.replace("user_detail_", "")
            await show_user_detail(query, user_detail_id)
        elif callback_data.startswith("add_"):
            coupon_type = callback_data.replace("add_", "")
            await start_adding_coupon(query, context, coupon_type)
        elif callback_data.startswith("clear_"):
            coupon_type = callback_data.replace("clear_", "")
            await clear_specific_coupons(query, coupon_type)
        elif callback_data.startswith("edit_codes_"):
            coupon_type = callback_data.replace("edit_codes_", "")
            await start_editing_codes(query, context, coupon_type)
        elif callback_data.startswith("toggle_"):
            coupon_type = callback_data.replace("toggle_", "")
            await toggle_specific_coupons(query, coupon_type)
        elif callback_data == "get_free_premium":
            await activate_free_premium(query, user_id)
        elif callback_data.startswith("bet_"):
            await show_bet_platform(query, callback_data.replace("bet_", ""))
        else:
            await query.message.reply_text("❌ Noma'lum tugma!")
            
    except Exception as e:
        logger.error(f"Button handler xatosi: {e}")
        try:
            await query.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qayta urining.")
        except:
            pass

async def send_today_coupons(query):
    try:
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
        
        # Bukmekerlar tugmalari
        keyboard = [
            [
                InlineKeyboardButton("🎰 1xBet", callback_data="bet_1xbet"),
                InlineKeyboardButton("🎯 MelBet", callback_data="bet_melbet"),
                InlineKeyboardButton("💰 DB Bet", callback_data="bet_dbbet")
            ],
            [InlineKeyboardButton("🔗 Do'stlarni Taklif Qilish", callback_data="share_referral")],
            [InlineKeyboardButton("💎 Premium Kuponlar", callback_data="premium_coupons")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            coupon_text, 
            reply_markup=reply_markup, 
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"send_today_coupons xatosi: {e}")
        await query.message.reply_text("❌ Kuponlarni yuklashda xatolik!")

async def handle_premium_coupons(query, user_id):
    try:
        if is_premium(user_id):
            await send_premium_coupons(query)
        else:
            await show_premium_offer(query, user_id)
    except Exception as e:
        logger.error(f"handle_premium_coupons xatosi: {e}")

async def send_premium_coupons(query):
    try:
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
        
        # Bukmekerlar tugmalari
        keyboard = [
            [
                InlineKeyboardButton("🎰 1xBet", callback_data="bet_1xbet"),
                InlineKeyboardButton("🎯 MelBet", callback_data="bet_melbet"),
                InlineKeyboardButton("💰 DB Bet", callback_data="bet_dbbet")
            ],
            [InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")],
            [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            premium_text, 
            reply_markup=reply_markup, 
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"send_premium_coupons xatosi: {e}")
        await query.message.reply_text("❌ Premium kuponlarni yuklashda xatolik!")

async def show_bet_platform(query, platform):
    """Bukmeker platformasini ko'rsatish"""
    try:
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
            [
                InlineKeyboardButton("🌐 Saytga O'tish", url=platform_link),
                InlineKeyboardButton("📱 APK Yuklash", url="https://t.me/bonusliapkbot")
            ],
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
        
    except Exception as e:
        logger.error(f"show_bet_platform xatosi: {e}")
        await query.message.reply_text("❌ Platformani ko'rsatishda xatolik!")

async def back_to_coupons(query):
    """Kuponlar sahifasiga qaytish"""
    try:
        if "premium" in query.message.text.lower():
            await send_premium_coupons(query)
        else:
            await send_today_coupons(query)
    except Exception as e:
        logger.error(f"back_to_coupons xatosi: {e}")

async def back_to_main(query):
    """Asosiy menyuga qaytish"""
    try:
        user = query.from_user
        user_id = user.id
        
        keyboard = [
            [
                InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons"),
                InlineKeyboardButton("💎 100% kupon", callback_data="premium_coupons")
            ],
            [
                InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link"),
                InlineKeyboardButton("🔗 Ulashish", callback_data="share_referral")
            ],
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
    except Exception as e:
        logger.error(f"back_to_main xatosi: {e}")

# ... (qolgan funksiyalar o'zgarmaydi, faqat try-catch qo'shildi)

async def show_premium_offer(query, user_id):
    try:
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
        
    except Exception as e:
        logger.error(f"show_premium_offer xatosi: {e}")

async def show_referral_link(query, user_id):
    try:
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
        
    except Exception as e:
        logger.error(f"show_referral_link xatosi: {e}")

# ... (qolgan funksiyalar ham shu tarzda try-catch bilan)

def main():
    try:
        # Application yaratish
        application = Application.builder().token(TOKEN).build()
        
        # Handlerlar
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
        application.add_handler(MessageHandler(filters.PHOTO, handle_admin_message))
        
        # Xatolik handler
        application.add_error_handler(error_handler)
        
        logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")
        logger.info("🤖 Bot ishlayapti...")
        logger.info(f"👑 Admin ID: {ADMIN_ID}")
        logger.info("🎰 Tugmalar faollashtirildi!")
        
        # Polling ni ishga tushirish
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"❌ Bot ishga tushmadi: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xatolarni qayta ishlash"""
    logger.error(f"Xatolik: {context.error}", exc_info=context.error)

if __name__ == "__main__":
    main()
