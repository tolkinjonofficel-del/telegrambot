import os
import json
import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta

# Bot tokeni
TOKEN = "8114630640:AAHqHzsEyL7s7yckyLXfOHltm8m8cYh4F2Q"

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
        "available": [],
        "purchased": {}
    },
    "settings": {
        "referral_points": 5,
        "coupon_price": 15,
        "min_exchange_points": 50,
        "exchange_rate": 10000,
        "daily_bonus": 10,
        "welcome_points": 30,
        "currency": "so'm"
    },
    "stats": {
        "total_users": 0,
        "total_points_given": 0,
        "total_coupons_sold": 0,
        "total_exchanges": 0,
        "last_daily_bonus": ""
    }
}

def load_data():
    """Ma'lumotlarni yuklash"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ma'lumotlarni yuklashda xato: {e}")
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data.copy()

def save_data(data):
    """Ma'lumotlarni saqlash"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Saqlash xatosi: {e}")
        return False

# Global data o'zgaruvchisini ishga tushirish
data = load_data()

def is_admin(user_id):
    return user_id == ADMIN_ID

def get_user_points(user_id):
    user_data = data['users'].get(str(user_id), {})
    return user_data.get('points', 0)

def get_user_referrals(user_id):
    user_data = data['users'].get(str(user_id), {})
    return user_data.get('referrals', 0)

def add_user_points(user_id, points, reason=""):
    """Foydalanuvchiga ball qo'shish"""
    user_id_str = str(user_id)
    if user_id_str not in data['users']:
        return False
    
    if 'points' not in data['users'][user_id_str]:
        data['users'][user_id_str]['points'] = 0
    
    data['users'][user_id_str]['points'] += points
    data['stats']['total_points_given'] += points
    
    if 'points_history' not in data['users'][user_id_str]:
        data['users'][user_id_str]['points_history'] = []
    
    data['users'][user_id_str]['points_history'].append({
        'points': points,
        'reason': reason,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'type': 'add'
    })
    
    return save_data(data)

def remove_user_points(user_id, points, reason=""):
    """Foydalanuvchidan ball olib tashlash"""
    user_id_str = str(user_id)
    if user_id_str not in data['users']:
        return False
    
    if data['users'][user_id_str].get('points', 0) < points:
        return False
    
    data['users'][user_id_str]['points'] -= points
    
    if 'points_history' not in data['users'][user_id_str]:
        data['users'][user_id_str]['points_history'] = []
    
    data['users'][user_id_str]['points_history'].append({
        'points': -points,
        'reason': reason,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'type': 'remove'
    })
    
    return save_data(data)

async def give_daily_bonus():
    """Har kuni barcha foydalanuvchilarga 10 ball berish"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Agar bugun bonus berilgan bo'lsa, qayta bermaslik
        if data['stats'].get('last_daily_bonus') == today:
            return
        
        bonus_points = data['settings']['daily_bonus']
        users_count = 0
        
        for user_id_str in data['users']:
            add_user_points(int(user_id_str), bonus_points, f"Kunlik bonus {today}")
            users_count += 1
        
        data['stats']['last_daily_bonus'] = today
        save_data(data)
        
        logger.info(f"Kunlik bonus berildi: {users_count} ta foydalanuvchi, {bonus_points} ball")
        
    except Exception as e:
        logger.error(f"Kunlik bonus berishda xato: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"Start command from user {user_id} ({user.first_name})")
        
        global data
        data = load_data()
        
        # Kunlik bonusni tekshirish
        await give_daily_bonus()
        
        # Yangi foydalanuvchi bo'lsa 30 ball berish
        is_new_user = False
        if str(user_id) not in data['users']:
            data['users'][str(user_id)] = {
                'name': user.first_name,
                'username': user.username,
                'referrals': 0,
                'points': data['settings']['welcome_points'],
                'joined_date': datetime.now().strftime("%Y-%m-%d"),
                'last_active': datetime.now().timestamp(),
                'points_history': [{
                    'points': data['settings']['welcome_points'],
                    'reason': "Yangi foydalanuvchi bonus",
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'type': 'add'
                }]
            }
            data['stats']['total_users'] += 1
            data['stats']['total_points_given'] += data['settings']['welcome_points']
            save_data(data)
            is_new_user = True
            logger.info(f"Yangi foydalanuvchi qo'shildi: {user_id} - 30 ball berildi")
        else:
            data['users'][str(user_id)]['last_active'] = datetime.now().timestamp()
            save_data(data)
        
        # Referal tizimi
        if context.args:
            ref_id = context.args[0]
            logger.info(f"Referal argument: {ref_id}")
            if ref_id.startswith('ref'):
                try:
                    referrer_id = int(ref_id[3:])
                    if str(referrer_id) in data['users'] and referrer_id != user_id:
                        data['users'][str(referrer_id)]['referrals'] += 1
                        
                        points_to_add = data['settings']['referral_points']
                        add_user_points(referrer_id, points_to_add, f"Referal taklif: {user.first_name}")
                        
                        save_data(data)
                        
                        try:
                            await context.bot.send_message(
                                chat_id=referrer_id,
                                text=f"🎉 *Tabriklaymiz!*\n\n"
                                     f"📤 Sizning referal havolangiz orqali yangi foydalanuvchi qo'shildi!\n"
                                     f"👤 Yangi foydalanuvchi: {user.first_name}\n"
                                     f"💰 Sizga {points_to_add} ball qo'shildi!\n"
                                     f"🎯 Jami ball: {get_user_points(referrer_id)}",
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"Referal bildirishnoma yuborishda xato: {e}")
                except Exception as e:
                    logger.error(f"Referal qayd etishda xato: {e}")

        welcome_text = f"""
🎉 *SALOM {user.first_name}!* 🏆

⚽ *FUTBOL BAHOLARI BOTIGA XUSH KELIBSIZ!*

💰 *BALL TIZIMI:*
• 🎁 *Yangi foydalanuvchi bonus:* 30 ball
• 📤 1 do'st taklif = *5 ball*
• 📅 *Kunlik bonus:* 10 ball
• 🎯 15 ball = *1 ta maxsus kupon*

📊 *SIZNING HOLATINGIZ:*
👥 Referallar: {get_user_referrals(user_id)} ta
💰 HISOBINGIZDA: {get_user_points(user_id)} ball
"""

        if is_new_user:
            welcome_text += f"\n🎁 *Sizga yangi foydalanuvchi bonus sifatida 30 ball berildi!*"

        welcome_text += f"\n\n🚀 *HOZIRROQ BOSHLANG!*\nBall to'plang va kuponlar oling! 🎯"

        keyboard = [
            [
                InlineKeyboardButton("🎯 KUPONLAR OLISH", callback_data="get_coupons"),
                InlineKeyboardButton("🎁 BONUSLAR", callback_data="bonuses")
            ],
            [
                InlineKeyboardButton("📊 MENING BALLIM", callback_data="my_points"),
                InlineKeyboardButton("📤 REFERAL HAVOLA", callback_data="get_referral_link")
            ]
        ]
        
        if is_admin(user_id):
            keyboard.append([InlineKeyboardButton("👑 ADMIN PANEL", callback_data="admin")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Start commandda xato: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        logger.info(f"Button handler: {query.data} from user {user_id}")
        
        global data
        data = load_data()
        
        # Kunlik bonusni tekshirish
        await give_daily_bonus()
        
        # Asosiy menyu tugmalari
        if query.data == "get_coupons":
            await show_coupon_selection(query, user_id)
        elif query.data == "get_ball_coupon":
            await get_ball_coupon(query, user_id)
        elif query.data == "bonuses":
            await show_bonuses(query)
        elif query.data == "my_points":
            await show_my_points(query, user_id)
        elif query.data == "get_referral_link":
            await show_referral_link(query, user_id)
        elif query.data == "share_referral":
            await share_referral_link(query, user_id)
        elif query.data == "back":
            await back_to_main(query)
        
        # ADMIN HANDLERLARI
        elif query.data == "admin":
            if is_admin(user_id):
                await show_admin_panel(query)
            else:
                await query.edit_message_text("❌ Siz admin emassiz!")
        elif query.data == "admin_stats":
            await show_admin_stats(query)
        elif query.data == "admin_add_coupon":
            await show_admin_add_coupon(query)
        elif query.data == "admin_broadcast":
            await show_admin_broadcast(query)
        elif query.data == "admin_manage_coupons":
            await show_admin_manage_coupons(query)
        elif query.data.startswith("admin_delete_coupon_"):
            coupon_id = query.data.replace("admin_delete_coupon_", "")
            await delete_coupon(query, coupon_id)
        elif query.data == "admin_view_coupons":
            await show_admin_view_coupons(query)
            
    except Exception as e:
        logger.error(f"Button handlerda xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# KUPON OLISH TIZIMI
async def show_coupon_selection(query, user_id):
    """Kupon olish sahifasi"""
    try:
        user_points = get_user_points(user_id)
        coupon_price = data['settings']['coupon_price']
        
        text = f"""
🎯 *KUPON OLISH*

💰 **Sizning balansingiz:** {user_points} ball
🎟️ **Kupon narxi:** {coupon_price} ball

💎 *Ballaringiz yetarli bo'lsa VIP kuponlar olishingiz mumkin:*
"""

        keyboard = []
        
        available_coupons = [c for c in data['coupons']['available'] 
                           if str(user_id) not in data['coupons']['purchased'].get(c['id'], [])]
        
        if available_coupons:
            if user_points >= coupon_price:
                keyboard.append([InlineKeyboardButton(f"💰 VIP KUPON OLISH ({coupon_price} ball)", callback_data="get_ball_coupon")])
                text += f"\n✅ *{len(available_coupons)} ta VIP kupon mavjud!*"
            else:
                text += f"\n❌ *Ball yetarli emas!* {coupon_price - user_points} ball yetishmayapti."
        else:
            text += f"\n📭 *Hozircha yangi kuponlar mavjud emas.*"
        
        keyboard.extend([
            [InlineKeyboardButton("📤 Bal To'plash", callback_data="get_referral_link")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_coupon_selection da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

async def get_ball_coupon(query, user_id):
    """VIP KUPON"""
    try:
        user_points = get_user_points(user_id)
        coupon_price = data['settings']['coupon_price']
        
        if user_points < coupon_price:
            await query.edit_message_text(
                f"❌ Ballaringiz yetarli emas!\n"
                f"💰 Sizda: {user_points} ball\n"
                f"💵 Kerak: {coupon_price} ball\n\n"
                f"📤 Ball to'plash uchun referal havolangizni tarqating yoki kunlik bonuslardan foydalaning!",
                parse_mode='Markdown'
            )
            return
        
        # Foydalanuvchi sotib olmagan kuponlarni topish
        available_coupons = [c for c in data['coupons']['available'] 
                           if str(user_id) not in data['coupons']['purchased'].get(c['id'], [])]
        
        if not available_coupons:
            await query.edit_message_text(
                "❌ Hozircha yangi kuponlar mavjud emas. Tez orada yangilanadi! 🔄",
                parse_mode='Markdown'
            )
            return
        
        coupon = random.choice(available_coupons)
        
        # Ballarni hisobdan olib tashlash
        data['users'][str(user_id)]['points'] -= coupon_price
        data['stats']['total_coupons_sold'] += 1
        
        # Kuponni sotib olinganlar ro'yxatiga qo'shish
        if coupon['id'] not in data['coupons']['purchased']:
            data['coupons']['purchased'][coupon['id']] = []
        
        data['coupons']['purchased'][coupon['id']].append(str(user_id))
        save_data(data)
        
        coupon_text = f"""
🎉 *TABRIKLAYMIZ!*

✅ Siz {coupon_price} ball evaziga kupon sotib oldingiz!

🎟️ *Kupon ma'lumotlari:*
🏆 **O'yin:** {coupon['teams']}
⏰ **Vaqt:** {coupon['time']}
🌍 **Liga:** {coupon['league']}
🎯 **Bashorat:** {coupon['prediction']}
📊 **Koeffitsient:** {coupon['odds']}
💎 **Ishonch:** {coupon['confidence']}

🔑 *Kupon kodlari:*
• 1xBet: `{coupon['codes']['1xbet']}`
• MelBet: `{coupon['codes']['melbet']}`
• DB Bet: `{coupon['codes']['dbbet']}`

💰 **Qolgan ball:** {get_user_points(user_id)}
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎰 1xBet", url=BUKMAKER_LINKS['1xbet']),
                InlineKeyboardButton("🎯 MelBet", url=BUKMAKER_LINKS['melbet']),
                InlineKeyboardButton("💰 DB Bet", url=BUKMAKER_LINKS['dbbet'])
            ],
            [InlineKeyboardButton("🔄 Yana Kupon Olish", callback_data="get_coupons")],
            [InlineKeyboardButton("💰 Mening Ballim", callback_data="my_points")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(coupon_text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"get_ball_coupon da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# BONUSLAR BO'LIMI
async def show_bonuses(query):
    """Bonuslar sahifasi"""
    try:
        text = """
🎁 *BONUSLAR*

💰 *Ball olish usullari:*
• 🎁 *Yangi foydalanuvchi bonus:* 30 ball
• 📅 *Kunlik bonus:* Har kuni 10 ball
• 📤 *Referal bonus:* Har bir do'st uchun 5 ball

🏆 *Bukmeker kontorlarida ro'yxatdan o'ting va bonus oling!*

🎰 **1xBet:**
• Yangi foydalanuvchilar uchun 100% bonus
• INSAYDER PROMOKODINI kiriting va Birinchi depozitga 100% gacha bonus

🎯 **MelBet:**
• Ro'yxatdan o'ting va bonus oling
• AIFUT promokodini kiriting

📱 **DB Bet:**
• Yangi foydalanuvchilar uchun maxsus takliflar
• Tezkor to'lovlar va yuqori koeffitsientlar
"""

        keyboard = [
            [
                InlineKeyboardButton("🎰 1xBet", url=BUKMAKER_LINKS['1xbet']),
                InlineKeyboardButton("🎯 MelBet", url=BUKMAKER_LINKS['melbet']),
                InlineKeyboardButton("💰 DB Bet", url=BUKMAKER_LINKS['dbbet'])
            ],
            [
                InlineKeyboardButton("🎯 Kupon Olish", callback_data="get_coupons"),
                InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")
            ],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_bonuses da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# FOYDALANUVCHI HISOBINI KO'RSATISH
async def show_my_points(query, user_id):
    """Foydalanuvchi ballari va statistikasi"""
    try:
        user_data = data['users'].get(str(user_id), {})
        points = user_data.get('points', 0)
        referrals = user_data.get('referrals', 0)
        coupon_price = data['settings']['coupon_price']
        
        text = f"""
🏆 *MENING HISOBIM*

💰 **HISOBINGIZDA:** {points} ball
👥 **Referallar:** {referrals} ta
💵 **1 referal:** {data['settings']['referral_points']} ball
📅 **Kunlik bonus:** {data['settings']['daily_bonus']} ball
🎟️ **Kupon narxi:** {coupon_price} ball

📊 **Kupon olish imkoniyatlari:**
"""

        if points >= coupon_price:
            text += f"✅ **Kupon olish mumkin!** - {points // coupon_price} ta kupon"
        else:
            text += f"❌ **Kupon uchun:** {coupon_price - points} ball yetishmayapti"
        
        # Kunlik bonus holati
        today = datetime.now().strftime("%Y-%m-%d")
        if data['stats'].get('last_daily_bonus') == today:
            text += "\n\n📅 *Bugun kunlik bonus olgansiz!*"
        else:
            text += "\n\n📅 *Bugun kunlik bonus olish uchun /start ni bosing!*"
        
        keyboard = [
            [InlineKeyboardButton("🎯 Kupon Olish", callback_data="get_coupons")],
            [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_my_points da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# REFERAL TIZIMI
async def show_referral_link(query, user_id):
    """Referal havolasini ko'rsatish"""
    try:
        bot_username = (await query.message._bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
        referrals_count = get_user_referrals(user_id)
        points_per_ref = data['settings']['referral_points']
        user_points = get_user_points(user_id)
        
        text = f"""
📤 *BAL TO'PLASH USULI*

🔗 **Sizning referal havolangiz:**
`{ref_link}`

💰 **Ball to'plash formulasi:**
• Har bir do'st = {points_per_ref} ball
• Ko'proq do'st = Ko'proq ball

📊 **Sizning holatingiz:**
• Do'stlar: {referrals_count} ta
• HISOBINGIZ: {user_points} ball
• Jami olingan ball: {referrals_count * points_per_ref} ball

💡 **Qanday ball to'plasaniz:**
1. Havolani nusxalang
2. Do'stlaringizga yuboring  
3. Har bir yangi do'st = {points_per_ref} ball
4. Ballarni kuponlarga aylantiring!

🚀 *Ko'proq do'st taklif qiling, tezroq ball to'plang!*
"""

        keyboard = [
            [InlineKeyboardButton("🔗 TELEGRAMDA ULASHISH", callback_data="share_referral")],
            [InlineKeyboardButton("🎯 Kupon Olish", callback_data="get_coupons")],
            [InlineKeyboardButton("💰 Mening Ballim", callback_data="my_points")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_referral_link da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

async def share_referral_link(query, user_id):
    """Havolani ulashish"""
    try:
        bot_username = (await query.message._bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
        
        share_text = f"""🎯 *Futbol Kuponlari Boti*

⚽ Kunlik bepul kuponlar
💰 Ball evaziga ekskluziv kuponlar
💎 Har bir do'st uchun 5 ball

🎁 Do'stlaringizni taklif qiling va bepul kuponlar oling!

Botga kirib, daromad olishni boshlang:
{ref_link}"""

        keyboard = [
            [InlineKeyboardButton("📤 TELEGRAMDA ULASHISH", url=f"https://t.me/share/url?url={ref_link}&text={share_text}")],
            [InlineKeyboardButton("💰 Mening Ballim", callback_data="my_points")],
            [InlineKeyboardButton("🎯 Kupon Olish", callback_data="get_coupons")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔗 *Havolani quyidagi tugma orqali osongina ulashing:*\n\n"
            "Tugmani bosing va do'stlaringizga yuboring!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"share_referral_link da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# ASOSIY MENYUGA QAYTISH
async def back_to_main(query):
    """Asosiy menyuga qaytish"""
    try:
        user = query.from_user
        user_id = user.id
        
        welcome_text = f"""
🎯 *Asosiy Menyu*

💰 **Sizning holatingiz:**
👥 Referallar: {get_user_referrals(user_id)} ta
💰 HISOBINGIZDA: {get_user_points(user_id)} ball

Ball to'plang va kuponlar oling! 🚀
"""

        keyboard = [
            [
                InlineKeyboardButton("🎯 KUPONLAR OLISH", callback_data="get_coupons"),
                InlineKeyboardButton("🎁 BONUSLAR", callback_data="bonuses")
            ],
            [
                InlineKeyboardButton("📊 MENING BALLIM", callback_data="my_points"),
                InlineKeyboardButton("📤 REFERAL HAVOLA", callback_data="get_referral_link")
            ]
        ]
        
        if is_admin(user_id):
            keyboard.append([InlineKeyboardButton("👑 ADMIN PANEL", callback_data="admin")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"back_to_main da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# ADMIN PANELI - YANGILANGAN
async def show_admin_panel(query):
    """Admin panelini ko'rsatish"""
    try:
        total_users = len(data['users'])
        total_points = sum(user.get('points', 0) for user in data['users'].values())
        
        # Eng ko'p referal qilgan foydalanuvchilar
        top_referrers = sorted(data['users'].items(), 
                             key=lambda x: x[1].get('referrals', 0), 
                             reverse=True)[:5]
        
        text = f"""
👑 *ADMIN PANELI*

📊 **Bot Statistikasi:**
👥 Jami foydalanuvchilar: {total_users} ta
💰 Jami ballar: {total_points} ball
🎟️ Sotilgan kuponlar: {data['stats']['total_coupons_sold']} ta
📂 Mavjud kuponlar: {len(data['coupons']['available'])} ta

🏆 **Top Referallar:**
"""
        for i, (user_id, user_data) in enumerate(top_referrers, 1):
            name = user_data.get('name', 'Noma\'lum')
            referrals = user_data.get('referrals', 0)
            text += f"{i}. {name} - {referrals} ta referal\n"

        text += "\n🎯 **Admin Vazifalari:**"

        keyboard = [
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton("🎯 Kupon Qo'shish", callback_data="admin_add_coupon")],
            [InlineKeyboardButton("📂 Kuponlarni Boshqarish", callback_data="admin_manage_coupons")],
            [InlineKeyboardButton("📢 Reklama Yuborish", callback_data="admin_broadcast")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_admin_panel da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

async def show_admin_stats(query):
    """Admin statistikasi"""
    try:
        total_users = len(data['users'])
        total_points = sum(user.get('points', 0) for user in data['users'].values())
        total_referrals = sum(user.get('referrals', 0) for user in data['users'].values())
        
        text = f"""
📊 *BATAFSIL STATISTIKA*

👥 **Foydalanuvchilar:**
• Jami: {total_users} ta
• Jami referallar: {total_referrals} ta
• O'rtacha referal: {total_referrals/total_users if total_users > 0 else 0:.1f} ta

💰 **Ball Tizimi:**
• Jami berilgan: {data['stats']['total_points_given']} ball
• Foydalanuvchilarda: {total_points} ball
• Sotilgan kuponlar: {data['stats']['total_coupons_sold']} ta

⚽ **Kuponlar:**
• Mavjud kuponlar: {len(data['coupons']['available'])} ta
• Sotilgan kuponlar: {sum(len(users) for users in data['coupons']['purchased'].values())} ta
"""

        keyboard = [
            [InlineKeyboardButton("👑 Admin Panel", callback_data="admin")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_admin_stats da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

async def show_admin_add_coupon(query):
    """Kupon qo'shish sahifasi"""
    try:
        text = """
🎯 *KUPON QO'SHISH*

Quyidagi formatda kupon qo'shing:

`vaqt|liga|jamoalar|bashorat|koeffitsient|ishonch|1xbet_kodi|melbet_kodi|dbbet_kodi`

📝 *Misol:*
`20:00|Premier League|Man City vs Arsenal|1X|1.50|85%|CODE123|CODE456|CODE789`

Yuborilgan xabar avtomatik tarzda qayta ishlanadi.
"""
        
        keyboard = [
            [InlineKeyboardButton("👑 Admin Panel", callback_data="admin")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_admin_add_coupon da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# YANGI: KUPONLARNI BOSHQARISH
async def show_admin_manage_coupons(query):
    """Kuponlarni boshqarish sahifasi"""
    try:
        available_coupons = data['coupons']['available']
        
        if not available_coupons:
            text = "📭 *Hozircha kuponlar mavjud emas*"
            keyboard = [
                [InlineKeyboardButton("🎯 Kupon Qo'shish", callback_data="admin_add_coupon")],
                [InlineKeyboardButton("👑 Admin Panel", callback_data="admin")],
                [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
            ]
        else:
            text = f"""
📂 *KUPONLARNI BOSHQARISH*

📊 **Mavjud kuponlar:** {len(available_coupons)} ta

🎯 **Kuponlar ro'yxati:**
"""
            keyboard = []
            
            for i, coupon in enumerate(available_coupons, 1):
                purchased_count = len(data['coupons']['purchased'].get(coupon['id'], []))
                text += f"\n{i}. {coupon['teams']} - {coupon['time']}\n"
                text += f"   🎯 {coupon['prediction']} | 📊 {coupon['odds']}\n"
                text += f"   👥 Sotilgan: {purchased_count} ta\n"
                
                # Har bir kupon uchun o'chirish tugmasi
                keyboard.append([
                    InlineKeyboardButton(
                        f"❌ {coupon['teams'][:20]}...", 
                        callback_data=f"admin_delete_coupon_{coupon['id']}"
                    )
                ])
            
            text += "\n🔧 **Harakatlar:**"
            keyboard.extend([
                [InlineKeyboardButton("📋 Kuponlarni Ko'rish", callback_data="admin_view_coupons")],
                [InlineKeyboardButton("🎯 Yangi Kupon Qo'shish", callback_data="admin_add_coupon")],
                [InlineKeyboardButton("👑 Admin Panel", callback_data="admin")],
                [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_admin_manage_coupons da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# YANGI: KUPONNI O'CHIRISH
async def delete_coupon(query, coupon_id):
    """Kuponni o'chirish"""
    try:
        # Kuponni topish
        coupon_to_delete = None
        for coupon in data['coupons']['available']:
            if coupon['id'] == coupon_id:
                coupon_to_delete = coupon
                break
        
        if not coupon_to_delete:
            await query.edit_message_text("❌ Kupon topilmadi!")
            return
        
        # Kuponni o'chirish
        data['coupons']['available'] = [c for c in data['coupons']['available'] if c['id'] != coupon_id]
        
        # Sotib olinganlar ro'yxatidan ham o'chirish
        if coupon_id in data['coupons']['purchased']:
            del data['coupons']['purchased'][coupon_id]
        
        save_data(data)
        
        await query.edit_message_text(
            f"✅ *Kupon muvaffaqiyatli o'chirildi!*\n\n"
            f"🏆 {coupon_to_delete['teams']}\n"
            f"⏰ {coupon_to_delete['time']}\n"
            f"🎯 {coupon_to_delete['prediction']}\n\n"
            f"📊 Qolgan kuponlar: {len(data['coupons']['available'])} ta",
            parse_mode='Markdown'
        )
        
        # Kuponlar boshqaruv sahifasiga qaytish
        await show_admin_manage_coupons(query)
        
    except Exception as e:
        logger.error(f"delete_coupon da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# YANGI: KUPONLARNI KO'RISH
async def show_admin_view_coupons(query):
    """Barcha kuponlarni ko'rish"""
    try:
        available_coupons = data['coupons']['available']
        
        if not available_coupons:
            text = "📭 *Hozircha kuponlar mavjud emas*"
        else:
            text = "📋 *BARCHA KUPONLAR*\n\n"
            
            for i, coupon in enumerate(available_coupons, 1):
                purchased_count = len(data['coupons']['purchased'].get(coupon['id'], []))
                text += f"🎟️ *Kupon {i}:*\n"
                text += f"🏆 **O'yin:** {coupon['teams']}\n"
                text += f"⏰ **Vaqt:** {coupon['time']}\n"
                text += f"🌍 **Liga:** {coupon['league']}\n"
                text += f"🎯 **Bashorat:** {coupon['prediction']}\n"
                text += f"📊 **Koeffitsient:** {coupon['odds']}\n"
                text += f"💎 **Ishonch:** {coupon['confidence']}\n"
                text += f"👥 **Sotilgan:** {purchased_count} ta\n"
                text += f"🔑 **Kodlar:** 1xBet: `{coupon['codes']['1xbet']}`, MelBet: `{coupon['codes']['melbet']}`, DB Bet: `{coupon['codes']['dbbet']}`\n"
                text += f"📅 **Qo'shilgan:** {coupon['added_date']}\n"
                text += f"🆔 **ID:** {coupon['id']}\n\n"
                text += "─" * 30 + "\n\n"
        
        keyboard = [
            [InlineKeyboardButton("📂 Kuponlarni Boshqarish", callback_data="admin_manage_coupons")],
            [InlineKeyboardButton("👑 Admin Panel", callback_data="admin")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_admin_view_coupons da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

async def show_admin_broadcast(query):
    """Reklama yuborish sahifasi"""
    try:
        text = f"""
📢 *REKLAMA YUBORISH*

Barcha {len(data['users'])} ta foydalanuvchilaga xabar yuborish uchun oddiy matn yuboring.

Xabar barcha foydalanuvchilarga yuboriladi.
"""
        
        keyboard = [
            [InlineKeyboardButton("👑 Admin Panel", callback_data="admin")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_admin_broadcast da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# ADMIN XABARLARNI QAYTA ISHLASH
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin xabarlarini qayta ishlash"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    try:
        message = update.message
        message_text = message.text.strip()
        
        # Kupon qo'shish
        if '|' in message_text:
            parts = message_text.split('|')
            
            if len(parts) == 9:  # Kupon format
                time, league, teams, prediction, odds, confidence, code_1xbet, code_melbet, code_dbbet = parts
                
                new_coupon = {
                    'id': str(random.randint(1000, 9999)),
                    'time': time.strip(),
                    'league': league.strip(),
                    'teams': teams.strip(),
                    'prediction': prediction.strip(),
                    'odds': odds.strip(),
                    'confidence': confidence.strip(),
                    'codes': {
                        '1xbet': code_1xbet.strip(),
                        'melbet': code_melbet.strip(),
                        'dbbet': code_dbbet.strip()
                    },
                    'added_date': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                data['coupons']['available'].append(new_coupon)
                save_data(data)
                
                await message.reply_text(
                    f"✅ *Kupon qo'shildi!*\n\n"
                    f"🏆 {teams.strip()}\n"
                    f"⏰ {time.strip()} | {league.strip()}\n"
                    f"🎯 {prediction.strip()} | 📊 {odds.strip()}\n"
                    f"💰 Narxi: {data['settings']['coupon_price']} ball\n\n"
                    f"📊 Jami kuponlar: {len(data['coupons']['available'])} ta",
                    parse_mode='Markdown'
                )
        
        # Reklama yuborish
        else:
            total_users = len(data['users'])
            successful = 0
            
            progress_msg = await message.reply_text(f"📤 Xabar yuborilmoqda... 0/{total_users}")
            
            for i, user_id_str in enumerate(data['users']):
                try:
                    await context.bot.send_message(
                        chat_id=int(user_id_str),
                        text=message_text,
                        parse_mode='Markdown'
                    )
                    successful += 1
                    
                    if i % 10 == 0:
                        await progress_msg.edit_text(f"📤 Xabar yuborilmoqda... {i}/{total_users}")
                        
                except Exception as e:
                    logger.error(f"Foydalanuvchiga xabar yuborishda xato {user_id_str}: {e}")
                    continue
            
            await progress_msg.edit_text(
                f"📊 *Reklama yuborildi!*\n\n"
                f"👥 Jami foydalanuvchi: {total_users} ta\n"
                f"✅ Muvaffaqiyatli: {successful} ta\n"
                f"❌ Xatolik: {total_users - successful} ta",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"handle_admin_message da xato: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# ASOSIY DASTUR
def main():
    """Asosiy dastur"""
    try:
        application = Application.builder().token(TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
        
        logger.info("Bot ishga tushmoqda...")
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        print("🤖 Bot ishlayapti...")
        print(f"👑 Admin ID: {ADMIN_ID}")
        print("🎯 YANGILANGAN TIZIM:")
        print("   • 🎁 Yangi foydalanuvchi: 30 ball")
        print("   • 📅 Kunlik bonus: 10 ball") 
        print("   • 📤 Referal: 5 ball")
        print("   • 🎯 Kupon narxi: 15 ball")
        print("   • 📂 Kuponlarni boshqarish funksiyasi QO'SHILDI")
        print("   • ❌ Pul ishlash funksiyasi O'CHIRILDI")
        print("   • ❌ Yordam tugmasi O'CHIRILDI")
        print("   • 🔄 Har bir kuponni hamma foydalanuvchi 1 marta sotib oladi")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Main da xato: {e}")
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
