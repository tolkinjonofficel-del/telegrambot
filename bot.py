import os
import json
import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta

# Bot tokeni
TOKEN = "7454675594:AAH7oaObYNXszfVx4z3TJx5kdy6-qjcVjBQ"

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
        "ball_coupons": {
            "available": [],
            "purchased": {},
            "price": 15,
            "last_update": ""
        }
    },
    "settings": {
        "min_referrals": 20,
        "referral_points": 5,
        "coupon_price": 15,
        "premium_price": 100000,
        "currency": "so'm",
        "min_exchange_points": 50,
        "exchange_rate": 10000,
        "daily_bonus": 15,
        "welcome_points": 40,
        "payment_details": "💳 *To'lov qilish uchun:*\n\n🏦 **HUMO:** `9860356622837710`\n📱 **Payme:** `mavjud emas`\n💳 **Uzumbank visa:** `4916990318695001`\n\n✅ To'lov qilgach, chek skrinshotini @baxtga_olga ga yuboring."
    },
    "stats": {
        "total_users": 0,
        "premium_users": 0,
        "today_users": 0,
        "today_referrals": 0,
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
    """Har kuni barcha foydalanuvchilarga 15 ball berish"""
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
        
        # Yangi foydalanuvchi bo'lsa 40 ball berish
        is_new_user = False
        if str(user_id) not in data['users']:
            data['users'][str(user_id)] = {
                'name': user.first_name,
                'username': user.username,
                'referrals': 0,
                'points': data['settings']['welcome_points'],  # 40 ball bilan boshlash
                'premium': False,
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
            logger.info(f"Yangi foydalanuvchi qo'shildi: {user_id} - 40 ball berildi")
        else:
            data['users'][str(user_id)]['last_active'] = datetime.now().timestamp()
            save_data(data)
        
        if context.args:
            ref_id = context.args[0]
            logger.info(f"Referal argument: {ref_id}")
            if ref_id.startswith('ref'):
                try:
                    referrer_id = int(ref_id[3:])
                    if str(referrer_id) in data['users'] and referrer_id != user_id:
                        data['users'][str(referrer_id)]['referrals'] += 1
                        data['stats']['today_referrals'] += 1
                        
                        points_to_add = data['settings']['referral_points']
                        add_user_points(referrer_id, points_to_add, f"Referal taklif: {user.first_name}")
                        
                        save_data(data)
                        
                        try:
                            await context.bot.send_message(
                                chat_id=referrer_id,
                                text=f"🎉 *Tabriklaymiz!*\n\n"
                                     f"📤 Sizning referal havolangiz orqali yangi foydalanuvchi qo'shildi!\n"
                                     f"👤 Yangi foydalanuvchi: {user.first_name}\n"
                                     f"💰 Sizga {points_to_add} ball qo'shildi! (1 referal = 5 ball)\n"
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
• 🎁 *Yangi foydalanuvchi bonus:* 40 ball
• 📤 1 do'st taklif = *5 ball*
• 📅 *Kunlik bonus:* 15 ball
• 💰 50 ball = *10,000 so'm*
• 🎯 15 ball = *1 ta maxsus kupon*

📊 *SIZNING HOLATINGIZ:*
👥 Referallar: {get_user_referrals(user_id)} ta
💰 HISOBINGIZDA: {get_user_points(user_id)} ball
"""

        if is_new_user:
            welcome_text += f"\n🎁 *Sizga yangi foydalanuvchi bonus sifatida 40 ball berildi!*"

        welcome_text += f"\n\n🚀 *HOZIRROQ BOSHLANG!*\nBall to'plang, kuponlar oling va yutuqlarga erishing!"

        keyboard = [
            [
                InlineKeyboardButton("🎯 KUPONLAR OLISH", callback_data="get_coupons"),
                InlineKeyboardButton("💰 PUL ISHLASH", callback_data="exchange_points")
            ],
            [
                InlineKeyboardButton("🎁 BONUSLAR", callback_data="bonuses"),
                InlineKeyboardButton("📊 MENING BALLIM", callback_data="my_points")
            ],
            [
                InlineKeyboardButton("📤 REFERAL HAVOLA", callback_data="get_referral_link"),
                InlineKeyboardButton("ℹ️ YORDAM", callback_data="help")
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
        elif query.data == "exchange_points":
            await show_exchange_points(query, user_id)
        elif query.data == "bonuses":
            await show_bonuses(query)
        elif query.data == "my_points":
            await show_my_points(query, user_id)
        elif query.data == "get_referral_link":
            await show_referral_link(query, user_id)
        elif query.data == "share_referral":
            await share_referral_link(query, user_id)
        elif query.data == "help":
            await show_help(query)
        elif query.data == "back":
            await back_to_main(query)
        elif query.data == "back_to_coupons":
            await back_to_coupon_selection(query)
        elif query.data == "process_exchange":
            await exchange_points_handler(query, user_id)
        
        # ADMIN HANDLERLARI
        elif query.data == "admin":
            if is_admin(user_id):
                await show_admin_panel(query)
            else:
                await query.edit_message_text("❌ Siz admin emassiz!")
        elif query.data == "admin_stats":
            await show_admin_stats(query)
        elif query.data == "admin_users":
            await show_admin_users(query)
        elif query.data == "admin_manage_balance":
            await show_admin_manage_balance(query)
        elif query.data == "admin_add_coupon":
            await show_admin_add_coupon(query)
        elif query.data == "admin_broadcast":
            await show_admin_broadcast(query)
        elif query.data == "admin_search_user":
            await admin_search_user(query, context)
        
        # BALL QO'SHISH/OLISH HANDLERLARI
        elif query.data.startswith("admin_add_points_"):
            try:
                user_id_to_edit = query.data.replace("admin_add_points_", "")
                context.user_data['editing_user'] = user_id_to_edit
                context.user_data['action'] = 'add_points'
                
                user_data = data['users'].get(user_id_to_edit, {})
                user_name = user_data.get('name', 'Noma\'lum')
                current_points = user_data.get('points', 0)
                
                await query.edit_message_text(
                    f"👤 *Foydalanuvchi:* {user_name}\n"
                    f"💰 *Joriy ball:* {current_points} ball\n"
                    f"💳 *Qancha ball qo'shmoqchisiz?*\n\n"
                    f"Raqam kiriting:",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"admin_add_points da xato: {e}")
                await query.edit_message_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
            
        elif query.data.startswith("admin_remove_points_"):
            try:
                user_id_to_edit = query.data.replace("admin_remove_points_", "")
                context.user_data['editing_user'] = user_id_to_edit
                context.user_data['action'] = 'remove_points'
                
                user_data = data['users'].get(user_id_to_edit, {})
                user_name = user_data.get('name', 'Noma\'lum')
                current_points = user_data.get('points', 0)
                
                await query.edit_message_text(
                    f"👤 *Foydalanuvchi:* {user_name}\n"
                    f"💰 *Joriy ball:* {current_points} ball\n"
                    f"💳 *Qancha ball olib tashlamoqchisiz?*\n\n"
                    f"Raqam kiriting:",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"admin_remove_points da xato: {e}")
                await query.edit_message_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
        
        else:
            await query.edit_message_text("❌ Noma'lum buyruq!")
            
    except Exception as e:
        logger.error(f"Button handlerda xato: {e}")
        try:
            await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        except:
            await query.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

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
        
        ball_coupons_count = len(data['coupons']['ball_coupons']['available'])
        
        if ball_coupons_count > 0:
            if user_points >= coupon_price:
                keyboard.append([InlineKeyboardButton(f"💰 VIP KUPON OLISH ({coupon_price} ball)", callback_data="get_ball_coupon")])
                text += f"\n✅ *{ball_coupons_count} ta VIP kupon mavjud!*"
            else:
                text += f"\n❌ *Ball yetarli emas!* {coupon_price - user_points} ball yetishmayapti."
        else:
            text += f"\n📭 *Hozircha ball kuponlar mavjud emas.*"
        
        keyboard.extend([
            [InlineKeyboardButton("💰 PUL ISHLASH", callback_data="exchange_points")],
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
        
        ball_coupons = data['coupons']['ball_coupons']['available']
        if not ball_coupons:
            await query.edit_message_text(
                "❌ Hozircha mavjud kuponlar yo'q. Tez orada yangilanadi! 🔄",
                parse_mode='Markdown'
            )
            return
        
        coupon = random.choice(ball_coupons)
        
        # Ballarni hisobdan olib tashlash
        data['users'][str(user_id)]['points'] -= coupon_price
        data['stats']['total_coupons_sold'] += 1
        
        if 'purchased' not in data['coupons']['ball_coupons']:
            data['coupons']['ball_coupons']['purchased'] = {}
        
        if str(user_id) not in data['coupons']['ball_coupons']['purchased']:
            data['coupons']['ball_coupons']['purchased'][str(user_id)] = []
        
        data['coupons']['ball_coupons']['purchased'][str(user_id)].append({
            **coupon,
            'purchased_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'price_paid': coupon_price
        })
        
        data['coupons']['ball_coupons']['available'].remove(coupon)
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

# PUL ISHLASH TIZIMI
async def show_exchange_points(query, user_id):
    """Ball almashish sahifasi"""
    try:
        user_points = get_user_points(user_id)
        min_points = data['settings']['min_exchange_points']
        exchange_rate = data['settings']['exchange_rate']
        
        text = f"""
💰 *PUL ISHLASH*

🎯 **Sizning ballaringiz:** {user_points} ball
💵 **Minimal talab:** {min_points} ball
💰 **Almashish kursi:** {min_points} ball = {exchange_rate} {data['settings']['currency']}

📊 **Hisob-kitob:**
• {min_points} ball = {exchange_rate} {data['settings']['currency']}
• {min_points * 2} ball = {exchange_rate * 2} {data['settings']['currency']}
• {min_points * 5} ball = {exchange_rate * 5} {data['settings']['currency']}

⚠️ *DIQQAT:* Tugmani bosganingizda {min_points} ball hisobingizdan oladi va so'rov @baxtga_olga ga yuboriladi.
"""

        keyboard = []
        
        if user_points >= min_points:
            keyboard.append([InlineKeyboardButton(f"💰 {min_points} BALLNI PULGA AYLANTIRISH", callback_data="process_exchange")])
        else:
            text += f"\n❌ *Ball yetarli emas!* {min_points - user_points} ball yetishmayapti."
            keyboard.append([InlineKeyboardButton("📤 Bal To'plash", callback_data="get_referral_link")])
        
        keyboard.extend([
            [InlineKeyboardButton("🎯 Kupon Olish", callback_data="get_coupons")],
            [InlineKeyboardButton("💰 Mening Ballim", callback_data="my_points")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_exchange_points da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

async def exchange_points_handler(query, user_id):
    """Pul ishlash tugmasi bosilganda"""
    try:
        user_points = get_user_points(user_id)
        min_points = data['settings']['min_exchange_points']
        
        if user_points < min_points:
            await query.edit_message_text(
                f"❌ Ballaringiz yetarli emas!\n"
                f"💰 Sizda: {user_points} ball\n"
                f"💵 Minimal talab: {min_points} ball\n\n"
                f"📤 Ball to'plash uchun:\n"
                f"• Kunlik bonuslardan foydalaning\n"
                f"• Referal havolangizni tarqating\n"
                f"• Do'stlaringizni taklif qiling",
                parse_mode='Markdown'
            )
            return
        
        # Ballarni hisobdan olib tashlash
        if remove_user_points(user_id, min_points, f"Pulga almashish uchun yuborildi"):
            # Admin ga xabar yuborish
            user_data = data['users'].get(str(user_id), {})
            user_name = user_data.get('name', 'Noma\'lum')
            user_username = user_data.get('username', '')
            
            admin_message = f"""
💸 *YANGI PUL ALMASHISH SO'ROVI*

👤 *Foydalanuvchi:*
Ism: {user_name}
Username: @{user_username if user_username else 'mavjud emas'}
ID: `{user_id}`

💰 *So'rov tafsilotlari:*
Ball: {min_points} ball
Parol: 1234
Xabar: "Salom men foydalanuvchi id raqami {user_id} xisobimdan {min_points} balni pulga aylantirmoqchiman parol 1234"

⏰ Vaqt: {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
            
            try:
                await query.message._bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_message,
                    parse_mode='Markdown'
                )
                
                # Foydalanuvchiga tasdiqlash xabari
                await query.edit_message_text(
                    f"✅ *So'rovingiz qabul qilindi!*\n\n"
                    f"💰 *Sizning {min_points} ballingiz hisobingizdan olindi*\n"
                    f"🎯 *Qolgan ball:* {get_user_points(user_id)} ball\n\n"
                    f"📨 *So'rovingiz @baxtga_olga ga yuborildi*\n"
                    f"⏰ *Tez orada siz bilan bog'lanishadi*\n\n"
                    f"💡 *Parol:* 1234\n"
                    f"📝 Xabar: \"Salom men foydalanuvchi id raqami {user_id} xisobimdan {min_points} balni pulga aylantirmoqchiman parol 1234\"",
                    parse_mode='Markdown'
                )
                
                data['stats']['total_exchanges'] += 1
                save_data(data)
                
            except Exception as e:
                logger.error(f"Adminga xabar yuborishda xato: {e}")
                # Xato bo'lsa, ballarni qaytarish
                add_user_points(user_id, min_points, "Xato tufayli qaytarildi")
                await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
        else:
            await query.edit_message_text("❌ Ballarni olib tashlashda xatolik yuz berdi!")
            
    except Exception as e:
        logger.error(f"exchange_points_handler da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# BONUSLAR BO'LIMI
async def show_bonuses(query):
    """Bonuslar sahifasi"""
    try:
        text = """
🎁 *BONUSLAR*

💰 *Ball olish usullari:*
• 🎁 *Yangi foydalanuvchi bonus:* 40 ball
• 📅 *Kunlik bonus:* Har kuni 15 ball
• 📤 *Referal bonus:* Har bir do'st uchun 5 ball

🏆 *Bukmeker kontorlarida ro'yxatdan o'ting va bonus oling!*

🎰 **1xBet:**
• Yangi foydalanuvchilar uchun 100% bonus
• INSAYDER PROMOKODINI kiriting va Birinchi depozitga 100% gacha bonus

🎯 **MelBet:**
• Ro'yxatdan o'ting va bonus oling
• AIFUT promokodini kiriting
"""

        keyboard = [
            [
                InlineKeyboardButton("🎰 1xBet Ro'yxatdan o'tish", url=BUKMAKER_LINKS['1xbet']),
                InlineKeyboardButton("🎯 MelBet Ro'yxatdan o'tish", url=BUKMAKER_LINKS['melbet'])
            ],
            [
                InlineKeyboardButton("🎯 Kupon Olish", callback_data="get_coupons"),
                InlineKeyboardButton("💰 PUL ISHLASH", callback_data="exchange_points")
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
        min_points = data['settings']['min_exchange_points']
        exchange_rate = data['settings']['exchange_rate']
        
        text = f"""
🏆 *MENING HISOBIM*

💰 **HISOBINGIZDA:** {points} ball
👥 **Referallar:** {referrals} ta
💵 **1 referal:** {data['settings']['referral_points']} ball
📅 **Kunlik bonus:** {data['settings']['daily_bonus']} ball

📊 **Almashish imkoniyatlari:**
• {min_points} ball = {exchange_rate} {data['settings']['currency']}
• {min_points * 2} ball = {exchange_rate * 2} {data['settings']['currency']}
• {min_points * 5} ball = {exchange_rate * 5} {data['settings']['currency']}

"""
        
        if points >= min_points:
            text += f"✅ **Almashish mumkin:** {points // min_points} marta\n\n"
        else:
            text += f"❌ **Almashish uchun:** {min_points - points} ball yetishmayapti\n\n"
        
        # Kunlik bonus holati
        today = datetime.now().strftime("%Y-%m-%d")
        if data['stats'].get('last_daily_bonus') == today:
            text += "📅 *Bugun kunlik bonus olgansiz!*\n\n"
        else:
            text += "📅 *Bugun kunlik bonus olish uchun /start ni bosing!*\n\n"
        
        points_history = user_data.get('points_history', [])
        if points_history:
            text += "📅 **So'nggi operatsiyalar:**\n"
            for history in points_history[-5:]:
                sign = "+" if history['points'] > 0 else ""
                text += f"• {sign}{history['points']} ball - {history['reason']}\n"
        
        keyboard = [
            [InlineKeyboardButton("💰 PUL ISHLASH", callback_data="exchange_points")],
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

# YORDAM BO'LIMI
async def show_help(query):
    """Yordam sahifasi"""
    try:
        text = """
ℹ️ *BOTDAN FOYDALANISH QO'LLANMASI*

⚽ *Kuponlar:*
• **Ball kuponlar** - 15 ball = 1 ta ekskluziv kupon

💰 *Ball Tizimi:*
• **Yangi foydalanuvchi bonus** - 40 ball
• **1 do'st taklif = 5 ball**
• **Kunlik bonus** - 15 ball
• **50 ball = 10,000 so'm** almashish
• **15 ball = 1 ta maxsus kupon**

🎯 *Qanday boshlash kerak:*
1. 📤 Do'stlaringizni taklif qiling
2. 💰 Ball to'plang
3. 🎯 Kuponlar oling
4. 💸 Ballarni pulga aylantiring

📞 *Qo'llab-quvvatlash:*
@baxtga_olga

🚀 *Har kuni yangi kuponlar bilan yutuqqa intiling!*
"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Kupon Olish", callback_data="get_coupons")],
            [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_help da xato: {e}")
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

Ball to'plang, kuponlar oling va yutuqlarga erishing! 🚀
"""

        keyboard = [
            [
                InlineKeyboardButton("🎯 KUPONLAR OLISH", callback_data="get_coupons"),
                InlineKeyboardButton("💰 PUL ISHLASH", callback_data="exchange_points")
            ],
            [
                InlineKeyboardButton("🎁 BONUSLAR", callback_data="bonuses"),
                InlineKeyboardButton("📊 MENING BALLIM", callback_data="my_points")
            ],
            [
                InlineKeyboardButton("📤 REFERAL HAVOLA", callback_data="get_referral_link"),
                InlineKeyboardButton("ℹ️ YORDAM", callback_data="help")
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

async def back_to_coupon_selection(query):
    """Kupon tanlash sahifasiga qaytish"""
    user_id = query.from_user.id
    await show_coupon_selection(query, user_id)

# ADMIN PANELI (qisqartirilgan versiya)
async def show_admin_panel(query):
    """Admin panelini ko'rsatish"""
    try:
        total_users = len(data['users'])
        total_points = sum(user.get('points', 0) for user in data['users'].values())
        
        text = f"""
👑 *ADMIN PANELI*

📊 **Bot Statistikasi:**
👥 Jami foydalanuvchilar: {total_users} ta
💰 Jami ballar: {total_points} ball
🎟️ Sotilgan kuponlar: {data['stats']['total_coupons_sold']} ta

🎯 **Admin Vazifalari:**
"""

        keyboard = [
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
            [InlineKeyboardButton("💰 Balans Boshqarish", callback_data="admin_manage_balance")],
            [InlineKeyboardButton("🎯 Kupon Qo'shish", callback_data="admin_add_coupon")],
            [InlineKeyboardButton("📢 Reklama Yuborish", callback_data="admin_broadcast")],
            [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"show_admin_panel da xato: {e}")
        await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# ... (qolgan admin funksiyalari)

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
        print("🎯 YANGI TIZIM:")
        print("   • 🎁 Yangi foydalanuvchi: 40 ball")
        print("   • 📅 Kunlik bonus: 15 ball")
        print("   • 🎯 Kupon narxi: 15 ball")
        print("   • 💰 Pul ishlash: 50 ball")
        print("   • 📨 So'rov @baxtga_olga ga yuboriladi")
        print("   • 🔑 Parol: 1234")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Main da xato: {e}")
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
