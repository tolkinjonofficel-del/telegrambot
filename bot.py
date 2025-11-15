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
            "active": True,
            "coupon_code": ""
        }
    },
    "settings": {
        "min_referrals": 10,
        "premium_price": 100,
        "currency": "so'm",
        "payment_details": "💳 To'lov qilish uchun:\n\nClick: 1234 5678 9012 3456\nPayme: +998901234567\n\nTo'lov qilgach, chek skrinshotini @admin ga yuboring."
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
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

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

    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons")],
        [InlineKeyboardButton("🎯 Premium Kuponlar", callback_data="premium_coupons")],
        [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]
    
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚽ Salom {user.first_name}!\n\n"
        "📊 Futbol Kuponlari Botiga Xush Kelibsiz!\n\n"
        "10 ta referal yoki 100 so'm to'lov bilan Premium kuponlarga ega bo'ling!",
        reply_markup=reply_markup
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
    elif query.data == "help":
        await show_help(query)
    elif query.data == "admin":
        if is_admin(user_id):
            await show_admin_panel(query)
    elif query.data == "back":
        await back_to_main(query)
    elif query.data == "admin_add_coupon":
        await start_adding_coupon(query, context)
    elif query.data == "admin_toggle_coupons":
        await toggle_coupons_active(query)
    elif query.data == "admin_clear_coupons":
        await clear_coupons(query)

async def send_today_coupons(query):
    today_coupons = data['coupons']['today']
    
    if not today_coupons['active'] or not today_coupons['matches']:
        await query.edit_message_text("❌ Bugun uchun kuponlar mavjud emas.")
        return
    
    coupon_text = f"⚽ {today_coupons['description']}\n"
    coupon_text += f"📅 Sana: {today_coupons['date']}\n"
    coupon_text += f"🆔 Kupon Kodi: {today_coupons.get('coupon_code', '')}\n\n"
    
    for i, match in enumerate(today_coupons['matches'], 1):
        coupon_text += f"{i}. {match['time']} - {match['league']}\n"
        coupon_text += f"🏆 {match['teams']}\n"
        coupon_text += f"🎯 {match['prediction']} ({match['odds']})\n"
        coupon_text += f"💎 {match['confidence']}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(coupon_text, reply_markup=reply_markup)

async def handle_premium_coupons(query, user_id):
    if is_premium(user_id):
        await send_premium_coupons(query)
    else:
        await show_premium_offer(query, user_id)

async def send_premium_coupons(query):
    premium_text = """🎯 PREMIUM KUPONLAR

⚽ Champions League
🏆 Real Madrid vs Bayern Munich
🎯 1X & Over 2.5 (3.50)
💎 95%

⚽ Premier League  
🏆 Man City vs Arsenal
🎯 BTTS - Ha (1.80)
💎 88%

🆔 Kupon Kodi: PREMIUM123"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(premium_text, reply_markup=reply_markup)

async def show_premium_offer(query, user_id):
    referrals_count = get_user_referrals(user_id)
    required_refs = data['settings']['min_referrals']
    
    text = f"""🎯 PREMIUM KUPONLAR

Sizda: {referrals_count}/{required_refs} referal

10 ta referal yoki 100 so'm to'lov bilan Premium oching!"""
    
    keyboard = []
    if referrals_count >= required_refs:
        keyboard.append([InlineKeyboardButton("🎁 Bepul Premium", callback_data="get_free_premium")])
    else:
        keyboard.append([InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")])
    
    keyboard.append([InlineKeyboardButton("💳 Premium Sotib Olish", callback_data="buy_premium")])
    keyboard.append([InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_referral_link(query, user_id):
    bot_username = (await query.message._bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
    referrals_count = get_user_referrals(user_id)
    
    text = f"""📤 Referal Havolangiz

{ref_link}

Sizning referallaringiz: {referrals_count} ta"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_help(query):
    text = """ℹ️ Yordam

⚽ Bugungi Kuponlar - bepul
🎯 Premium Kuponlar - 10 referal yoki 100 so'm
📤 Referal Havola - do'stlaringizni taklif qiling"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# ADMIN FUNCTIONS
async def show_admin_panel(query):
    status = "🟢 Faol" if data['coupons']['today']['active'] else "🔴 Nofaol"
    matches_count = len(data['coupons']['today']['matches'])
    
    text = f"""👑 Admin Panel

Kuponlar: {status}
Kuponlar soni: {matches_count} ta
Foydalanuvchilar: {data['stats']['total_users']}"""
    
    keyboard = [
        [InlineKeyboardButton("➕ Kupon Qo'shish", callback_data="admin_add_coupon")],
        [InlineKeyboardButton("🔄 Faol/O'chir", callback_data="admin_toggle_coupons")],
        [InlineKeyboardButton("🗑️ Kuponlarni Tozalash", callback_data="admin_clear_coupons")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def start_adding_coupon(query, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['adding_coupon'] = True
    await query.edit_message_text(
        "Kupon qo'shish uchun formatda yuboring:\n\n"
        "sana|vaqt|liga|jamoalar|bashorat|koeffitsient|ishonch\n\n"
        "Misol: 2024-01-20|20:00|Premier League|Man City vs Arsenal|1X|1.50|85%"
    )

async def toggle_coupons_active(query):
    data['coupons']['today']['active'] = not data['coupons']['today']['active']
    save_data(data)
    status = "faol" if data['coupons']['today']['active'] else "nofaol"
    await query.message.reply_text(f"Kuponlar {status} holatga o'zgartirildi!")
    await show_admin_panel(query)

async def clear_coupons(query):
    data['coupons']['today']['matches'] = []
    data['coupons']['today']['coupon_code'] = generate_coupon_code()
    save_data(data)
    await query.message.reply_text("Barcha kuponlar o'chirildi!")
    await show_admin_panel(query)

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    if context.user_data.get('adding_coupon'):
        await process_coupon_addition(update, context)

async def process_coupon_addition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_text = update.message.text
        parts = message_text.split('|')
        
        if len(parts) < 7:
            await update.message.reply_text("❌ Noto'g'ri format!")
            return
        
        date, time, league, teams, prediction, odds, confidence = parts[:7]
        
        new_match = {
            'time': time.strip(),
            'league': league.strip(),
            'teams': teams.strip(),
            'prediction': prediction.strip(),
            'odds': odds.strip(),
            'confidence': confidence.strip()
        }
        
        # Birinchi kupon qo'shilganda kod yaratish
        if not data['coupons']['today']['matches']:
            data['coupons']['today']['coupon_code'] = generate_coupon_code()
        
        data['coupons']['today']['matches'].append(new_match)
        data['coupons']['today']['date'] = date.strip()
        save_data(data)
        
        coupon_code = data['coupons']['today'].get('coupon_code', '')
        
        await update.message.reply_text(
            f"✅ Kupon qo'shildi!\n"
            f"Kod: {coupon_code}\n"
            f"Jami: {len(data['coupons']['today']['matches'])} ta"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")
    
    context.user_data.pop('adding_coupon', None)

async def back_to_main(query):
    user = query.from_user
    user_id = user.id
    
    keyboard = [
        [InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons")],
        [InlineKeyboardButton("🎯 Premium Kuponlar", callback_data="premium_coupons")],
        [InlineKeyboardButton("📤 Referal Havola", callback_data="get_referral_link")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")]
    ]
    
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚽ Salom {user.first_name}!",
        reply_markup=reply_markup
    )

def main():
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handlerlar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
        
        print("✅ Bot ishga tushdi!")
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
