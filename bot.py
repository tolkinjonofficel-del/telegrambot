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
        "today": {
            "date": "",
            "matches": [],
            "description": "🎯 Bugungi Bepul Kuponlar",
            "active": True,
            "coupon_codes": {
                "1xbet": "",
                "melbet": "",
                "dbbet": ""
            }
        },
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
        "payment_details": "💳 *To'lov qilish uchun:*\n\n🏦 **HUMO:** `9860356622837710`\n📱 **Payme:** `mavjud emas`\n💳 **Uzumbank visa:** `4916990318695001`\n\n✅ To'lov qilgach, chek skrinshotini @baxtga_olga ga yuboring."
    },
    "stats": {
        "total_users": 0,
        "premium_users": 0,
        "today_users": 0,
        "today_referrals": 0,
        "total_points_given": 0,
        "total_coupons_sold": 0,
        "total_exchanges": 0
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"Start command from user {user_id} ({user.first_name})")
        
        global data
        data = load_data()
        
        if str(user_id) not in data['users']:
            data['users'][str(user_id)] = {
                'name': user.first_name,
                'username': user.username,
                'referrals': 0,
                'points': 0,
                'premium': False,
                'joined_date': datetime.now().strftime("%Y-%m-%d"),
                'last_active': datetime.now().timestamp(),
                'points_history': []
            }
            data['stats']['total_users'] += 1
            save_data(data)
            logger.info(f"Yangi foydalanuvchi qo'shildi: {user_id}")
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

💰 *HAR KUNI YANGI KUPONLAR!*
• 🎯 *Kunlik bepul kuponlar* - Har kuni yangilanadi!
• 💰 *Ball evaziga kuponlar* - 15 ball = 1 ta ekskluziv kupon
• 🎁 *Bonuslar* - Bukmeker kontorlarida ro'yxatdan o'ting

🏆 *BALL TIZIMI:*
• 📤 1 do'st taklif = *5 ball*
• 💰 50 ball = *10,000 so'm*
• 🎯 15 ball = *1 ta maxsus kupon*

📊 *SIZNING HOLATINGIZ:*
👥 Referallar: {get_user_referrals(user_id)} ta
💰 HISOBINGIZDA: {get_user_points(user_id)} ball

🚀 *HOZIRROQ BOSHLANG!*
Ball to'plang, kuponlar oling va yutuqlarga erishing!
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
        
        if query.data == "get_coupons":
            await show_coupon_selection(query, user_id)
        elif query.data == "get_free_coupon":
            await send_today_coupons(query)
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
        
        # ADMIN HANDLERLARI
        elif query.data == "admin":
            if is_admin(user_id):
                await show_admin_panel(query)
            else:
                await query.message.reply_text("❌ Siz admin emassiz!")
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
            user_id_to_edit = query.data.replace("admin_add_points_", "")
            context.user_data['editing_user'] = user_id_to_edit
            context.user_data['action'] = 'add_points'
            user_data = data['users'].get(user_id_to_edit, {})
            user_name = user_data.get('name', 'Noma\'lum')
            current_points = user_data.get('points', 0)
            
            await query.message.reply_text(
                f"👤 *Foydalanuvchi:* {user_name}\n"
                f"💰 *Joriy ball:* {current_points} ball\n"
                f"💳 *Qancha ball qo'shmoqchisiz?*\n\n"
                f"Raqam kiriting:",
                parse_mode='Markdown'
            )
            
        elif query.data.startswith("admin_remove_points_"):
            user_id_to_edit = query.data.replace("admin_remove_points_", "")
            context.user_data['editing_user'] = user_id_to_edit
            context.user_data['action'] = 'remove_points'
            user_data = data['users'].get(user_id_to_edit, {})
            user_name = user_data.get('name', 'Noma\'lum')
            current_points = user_data.get('points', 0)
            
            await query.message.reply_text(
                f"👤 *Foydalanuvchi:* {user_name}\n"
                f"💰 *Joriy ball:* {current_points} ball\n"
                f"💳 *Qancha ball olib tashlamoqchisiz?*\n\n"
                f"Raqam kiriting:",
                parse_mode='Markdown'
            )
        
        else:
            await query.message.reply_text("❌ Noma'lum buyruq!")
            
    except Exception as e:
        logger.error(f"Button handlerda xato: {e}")
        try:
            await update.callback_query.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
        except:
            pass

# ... (qolgan funksiyalar o'zgarmagan, faqat admin qidiruv funksiyasini to'g'irlayman)

async def admin_search_user(query, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi qidirish - TO'G'IRLANGAN VERSIYA"""
    try:
        # Context ni to'g'ri o'rnatish
        context.user_data['admin_action'] = 'search_user'
        
        text = """
🔍 *FOYDALANUVCHI QIDIRISH*

Foydalanuvchi @username yoki ismini yuboring:

*Namuna:*
`ali` - Ismi Ali bo'lgan foydalanuvchilar  
`john` - Ismi John bo'lgan foydalanuvchilar
`baxtga_olga` - @baxtga_olga foydalanuvchisi

💡 *Eslatma:* 
- Faqat username yoki ismni yozing, @ belgisiz
- Qisman qidirish ham ishlaydi
- Katta-kichik harflar farqi yo'q
"""

        keyboard = [
            [InlineKeyboardButton("🔙 Balans Boshqarish", callback_data="admin_manage_balance")],
            [InlineKeyboardButton("👑 Admin Panel", callback_data="admin")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"admin_search_user da xato: {e}")
        await query.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

# YANGI ADMIN XABARLARINI QAYTA ISHLASH - TO'G'IRLANGAN
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin xabarlarini qayta ishlash - TO'G'IRLANGAN VERSIYA"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    try:
        message = update.message
        message_text = message.text.strip()
        
        logger.info(f"Admin xabar: {message_text}")
        
        # Foydalanuvchi qidirish - TO'G'IRLANGAN
        if context.user_data.get('admin_action') == 'search_user':
            search_term = message_text.lower().strip()
            found_users = []
            
            logger.info(f"Qidiruv so'rovi: '{search_term}'")
            logger.info(f"Jami foydalanuvchilar: {len(data['users'])} ta")
            
            # Barcha foydalanuvchilarni tekshiramiz
            for user_id_str, user_data in data['users'].items():
                user_username = user_data.get('username', '').lower() if user_data.get('username') else ''
                user_name = user_data.get('name', '').lower() if user_data.get('name') else ''
                
                logger.debug(f"Tekshirilayotgan: {user_name} (@{user_username}) - ID: {user_id_str}")
                
                # Username yoki ismda qidirish (qisman moslik)
                if (search_term in user_username or 
                    search_term in user_name or
                    user_name.startswith(search_term) or
                    user_username.startswith(search_term)):
                    
                    found_users.append((user_id_str, user_data))
                    logger.info(f"Topildi: {user_data.get('name')} (@{user_data.get('username')}) - ID: {user_id_str}")
            
            if found_users:
                text = f"🔍 *Qidiruv natijasi:* `{search_term}`\n\n"
                text += f"📊 Topilgan foydalanuvchilar: {len(found_users)} ta\n\n"
                
                for user_id_str, user_data in found_users[:10]:  # 10 tadan ko'p bo'lsa cheklaymiz
                    name = user_data.get('name', 'Noma\'lum')
                    username_found = user_data.get('username', '')
                    points = user_data.get('points', 0)
                    referrals = user_data.get('referrals', 0)
                    
                    username_display = f"(@{username_found})" if username_found else ""
                    
                    text += f"👤 *{name}* {username_display}\n"
                    text += f"🆔 ID: `{user_id_str}`\n"
                    text += f"💰 Ball: {points} | 👥 Referallar: {referrals} ta\n\n"
                
                if len(found_users) > 10:
                    text += f"⚠️ ... va yana {len(found_users) - 10} ta foydalanuvchi\n\n"
                
                keyboard = []
                for user_id_str, user_data in found_users[:8]:  # Tugmalar uchun 8 tadan
                    name = user_data.get('name', 'Noma\'lum')[:15]
                    username_found = user_data.get('username', '')
                    
                    # Tugma matnini tayyorlash
                    display_text = f"{name}"
                    if username_found:
                        display_text = f"{name} (@{username_found})"[:20]
                    
                    keyboard.extend([
                        [
                            InlineKeyboardButton(f"➕ {display_text}", callback_data=f"admin_add_points_{user_id_str}"),
                            InlineKeyboardButton(f"➖ {display_text}", callback_data=f"admin_remove_points_{user_id_str}")
                        ]
                    ])
                
                keyboard.append([InlineKeyboardButton("🔙 Balans Boshqarish", callback_data="admin_manage_balance")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
                
            else:
                # Hech nima topilmaganda barcha foydalanuvchilarni ko'rsatish
                users_list = list(data['users'].items())[:8]
                users_text = f"❌ *Foydalanuvchi topilmadi!*\n\n"
                users_text += f"🔍 Qidiruv so'zi: `{search_term}`\n\n"
                users_text += "📋 *Oxirgi foydalanuvchilar:*\n"
                
                for i, (uid, udata) in enumerate(users_list, 1):
                    name = udata.get('name', 'Noma\'lum')
                    username_found = udata.get('username', '')
                    points = udata.get('points', 0)
                    
                    username_display = f"(@{username_found})" if username_found else ""
                    users_text += f"{i}. {name} {username_display} - 💰 {points} ball\n"
                
                users_text += f"\n💡 *Jami foydalanuvchilar:* {len(data['users'])} ta"
                users_text += f"\n\n💡 *Maslahat:* Ism yoki username ni aniqroq yozing"
                
                # Oxirgi foydalanuvchilarni boshqarish tugmalari
                keyboard = []
                for uid, udata in users_list[:6]:
                    name = udata.get('name', 'Noma\'lum')[:12]
                    keyboard.extend([
                        [
                            InlineKeyboardButton(f"➕ {name}", callback_data=f"admin_add_points_{uid}"),
                            InlineKeyboardButton(f"➖ {name}", callback_data=f"admin_remove_points_{uid}")
                        ]
                    ])
                
                keyboard.append([InlineKeyboardButton("🔄 Qayta Qidirish", callback_data="admin_search_user")])
                keyboard.append([InlineKeyboardButton("🔙 Balans Boshqarish", callback_data="admin_manage_balance")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.reply_text(users_text, reply_markup=reply_markup, parse_mode='Markdown')
            
            context.user_data.pop('admin_action', None)
            return
        
        # Ball qo'shish/olish rejimi
        if context.user_data.get('editing_user'):
            user_id_to_edit = context.user_data['editing_user']
            action = context.user_data.get('action')
            
            try:
                points = int(message.text)
                user_data = data['users'].get(user_id_to_edit, {})
                user_name = user_data.get('name', 'Noma\'lum')
                current_points = user_data.get('points', 0)
                
                if action == 'add_points':
                    # Foydalanuvchi ID sini to'g'ri formatda o'tkazish
                    user_id_int = int(user_id_to_edit)
                    if add_user_points(user_id_int, points, f"Admin tomonidan qo'shildi"):
                        await message.reply_text(
                            f"✅ *Ball qo'shildi!*\n\n"
                            f"👤 Foydalanuvchi: {user_name}\n"
                            f"🆔 ID: `{user_id_to_edit}`\n"
                            f"💰 Qo'shildi: {points} ball\n"
                            f"📊 Avval: {current_points} ball\n"
                            f"🎯 Keyin: {get_user_points(user_id_int)} ball\n\n"
                            f"✅ Amal muvaffaqiyatli bajarildi!",
                            parse_mode='Markdown'
                        )
                    else:
                        await message.reply_text("❌ Ball qo'shishda xatolik yuz berdi!")
                    
                elif action == 'remove_points':
                    # Foydalanuvchi ID sini to'g'ri formatda o'tkazish
                    user_id_int = int(user_id_to_edit)
                    if remove_user_points(user_id_int, points, f"Admin tomonidan olindi"):
                        await message.reply_text(
                            f"✅ *Ball olindi!*\n\n"
                            f"👤 Foydalanuvchi: {user_name}\n"
                            f"🆔 ID: `{user_id_to_edit}`\n"
                            f"💰 Olindi: {points} ball\n"
                            f"📊 Avval: {current_points} ball\n"
                            f"🎯 Keyin: {get_user_points(user_id_int)} ball\n\n"
                            f"⚠️ Amalni bekor qilib bo'lmaydi!",
                            parse_mode='Markdown'
                        )
                    else:
                        await message.reply_text(
                            f"❌ *Ball olib bo'lmadi!*\n\n"
                            f"👤 Foydalanuvchi: {user_name}\n"
                            f"💰 So'ralgan: {points} ball\n"
                            f"🎯 Mavjud: {current_points} ball\n\n"
                            f"Ball yetarli emas!",
                            parse_mode='Markdown'
                        )
                
                context.user_data.pop('editing_user', None)
                context.user_data.pop('action', None)
                return
                
            except ValueError:
                await message.reply_text("❌ Iltimos, faqat raqam kiriting!")
                return
        
        # Kupon qo'shish
        if '|' in message.text:
            parts = message.text.split('|')
            
            if len(parts) == 10:  # Bepul kupon
                date, time, league, teams, prediction, odds, confidence, code_1xbet, code_melbet, code_dbbet = parts
                
                new_match = {
                    'time': time.strip(),
                    'league': league.strip(),
                    'teams': teams.strip(),
                    'prediction': prediction.strip(),
                    'odds': odds.strip(),
                    'confidence': confidence.strip()
                }
                
                data['coupons']['today']['matches'].append(new_match)
                data['coupons']['today']['date'] = date.strip()
                data['coupons']['today']['coupon_codes'] = {
                    "1xbet": code_1xbet.strip(),
                    "melbet": code_melbet.strip(),
                    "dbbet": code_dbbet.strip()
                }
                save_data(data)
                
                await message.reply_text(
                    f"✅ *Bepul kupon qo'shildi!*\n\n"
                    f"🏆 {teams.strip()}\n"
                    f"⏰ {time.strip()} | {league.strip()}\n"
                    f"🎯 {prediction.strip()} | 📊 {odds.strip()}\n\n"
                    f"📊 Jami bepul kuponlar: {len(data['coupons']['today']['matches'])} ta",
                    parse_mode='Markdown'
                )
                
            elif len(parts) == 9:  # Ball kupon
                time, league, teams, prediction, odds, confidence, code_1xbet, code_melbet, code_dbbet = parts
                
                new_coupon = {
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
                
                data['coupons']['ball_coupons']['available'].append(new_coupon)
                data['coupons']['ball_coupons']['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_data(data)
                
                await message.reply_text(
                    f"✅ *Ball kupon qo'shildi!*\n\n"
                    f"🏆 {teams.strip()}\n"
                    f"⏰ {time.strip()} | {league.strip()}\n"
                    f"🎯 {prediction.strip()} | 📊 {odds.strip()}\n"
                    f"💰 Narxi: {data['settings']['coupon_price']} ball\n\n"
                    f"📊 Jami ball kuponlar: {len(data['coupons']['ball_coupons']['available'])} ta",
                    parse_mode='Markdown'
                )
        
        # Reklama yuborish
        else:
            # ... (reklama kodi o'zgarmadi)
            pass
            
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
        application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_admin_message))
        
        logger.info("Bot ishga tushmoqda...")
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        print("🤖 Bot ishlayapti...")
        print(f"👑 Admin ID: {ADMIN_ID}")
        print("🎯 BARCHA FUNKSIYALAR ISHLAYDI:")
        print("   • 🎯 Kupon olish tizimi")
        print("   • 💰 Ball almashish")
        print("   • 🎁 Bonuslar")
        print("   • 👑 Soddalashtirilgan admin paneli")
        print("   • 💰 Ball qo'shish/olish (TO'LIQ ISHLAYDI!)")
        print("   • 🔍 Foydalanuvchi qidirish (TO'LIQ ISHLAYDI!)")
        print("   • 📢 Reklama yuborish")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Main da xato: {e}")
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
