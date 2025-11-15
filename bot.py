import os
import json
import logging
import random
import string
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

def calculate_user_stats():
    """Foydalanuvchi statistikasini hisoblash"""
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
            except:
                pass
    
    data['stats']['today_users'] = today_count
    data['stats']['week_users'] = week_count
    data['stats']['month_users'] = month_count
    save_data(data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
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
            except:
                pass

    # Chiroyli va 3 qatorli tugmalar
    keyboard = [
        # 1-qator: Asosiy kuponlar
        [
            InlineKeyboardButton("⚽ Bugungi Kuponlar", callback_data="today_coupons"),
            InlineKeyboardButton("💎 100% kupon", callback_data="premium_coupons")
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
    elif query.data == "admin_user_stats":
        await show_user_statistics(query)
    elif query.data == "admin_broadcast":
        await start_broadcast(query, context)
    elif query.data == "admin_user_list":
        await show_user_list(query)
    elif query.data.startswith("user_detail_"):
        user_detail_id = query.data.replace("user_detail_", "")
        await show_user_detail(query, user_detail_id)
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

# ... (send_today_coupons, handle_premium_coupons, send_premium_coupons, show_bet_platform, back_to_coupons funksiyalari o'zgarmaydi)

async def show_admin_panel(query):
    """Yangi va mukammal admin paneli"""
    today_status = "🟢 Faol" if data['coupons']['today']['active'] else "🔴 Nofaol"
    premium_status = "🟢 Faol" if data['coupons']['premium']['active'] else "🔴 Nofaol"
    today_count = len(data['coupons']['today']['matches'])
    premium_count = len(data['coupons']['premium']['matches'])
    
    # Statistikani yangilash
    calculate_user_stats()
    
    text = f"""
👑 *MUKAMMAL ADMIN PANELI*

📊 **UMUMIY STATISTIKA:**
👥 Jami foydalanuvchilar: {data['stats']['total_users']} ta
💎 Premium foydalanuvchilar: {sum(1 for user in data['users'].values() if user.get('premium', False))} ta
📈 Bugun qo'shilgan: {data['stats']['today_users']} ta
📈 So'nggi 7 kun: {data['stats']['week_users']} ta
📈 So'nggi 30 kun: {data['stats']['month_users']} ta

⚽ **KUPONLAR HOLATI:**
📅 Bugungi kuponlar: {today_status} ({today_count} ta o'yin)
💎 Premium kuponlar: {premium_status} ({premium_count} ta o'yin)

🎯 **ADMIN IMKONIYATLARI:**
"""
    
    keyboard = [
        [InlineKeyboardButton("📊 Foydalanuvchi Statistika", callback_data="admin_user_stats")],
        [InlineKeyboardButton("👥 Foydalanuvchilar Ro'yxati", callback_data="admin_user_list")],
        [InlineKeyboardButton("📢 Xabar Yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton("➕ Kupon Qo'shish", callback_data="admin_add_coupon")],
        [InlineKeyboardButton("🔑 Kodlarni Tahrirlash", callback_data="admin_edit_codes")],
        [InlineKeyboardButton("🔄 Faol/O'chirish", callback_data="admin_toggle_coupons")],
        [InlineKeyboardButton("🗑️ Kuponlarni Tozalash", callback_data="admin_clear_coupons")],
        [InlineKeyboardButton("💳 To'lov Sozlamalari", callback_data="admin_payment_settings")],
        [InlineKeyboardButton("🔙 Bosh Menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_user_statistics(query):
    """Batafsil foydalanuvchi statistikasi"""
    calculate_user_stats()
    
    total_users = data['stats']['total_users']
    premium_users = sum(1 for user in data['users'].values() if user.get('premium', False))
    regular_users = total_users - premium_users
    
    # Referal statistikasi
    users_with_referrals = sum(1 for user in data['users'].values() if user.get('referrals', 0) > 0)
    total_referrals = sum(user.get('referrals', 0) for user in data['users'].values())
    
    # Faol foydalanuvchilar (so'nggi 7 kun)
    week_ago = datetime.now() - timedelta(days=7)
    active_users = 0
    for user_data in data['users'].values():
        if 'last_active' in user_data:
            try:
                last_active = datetime.fromisoformat(user_data['last_active'])
                if last_active >= week_ago:
                    active_users += 1
            except:
                pass
    
    text = f"""
📊 *BATAFSIL FOYDALANUVCHI STATISTIKASI*

👥 **UMUMIY KO'RSATKICHLAR:**
• Jami foydalanuvchilar: {total_users} ta
• Premium foydalanuvchilar: {premium_users} ta
• Oddiy foydalanuvchilar: {regular_users} ta
• Faol foydalanuvchilar (7 kun): {active_users} ta

📈 **DAVRIY QO'SHILISHLAR:**
• Bugun: {data['stats']['today_users']} ta
• So'nggi 7 kun: {data['stats']['week_users']} ta  
• So'nggi 30 kun: {data['stats']['month_users']} ta

🔗 **REFERAL TIZIMI:**
• Referal olgan foydalanuvchilar: {users_with_referrals} ta
• Jami referallar: {total_referrals} ta
• O'rtacha referal: {total_referrals/max(users_with_referrals, 1):.1f} ta

💎 **PREMIUM STATISTIKA:**
• Premium ulushi: {(premium_users/max(total_users, 1)*100):.1f}%
• Faollik darajasi: {(active_users/max(total_users, 1)*100):.1f}%
"""
    
    keyboard = [
        [InlineKeyboardButton("👥 Batafsil Ro'yxat", callback_data="admin_user_list")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_user_list(query):
    """Foydalanuvchilar ro'yxati"""
    users = data['users']
    
    if not users:
        text = "📭 *Hozircha foydalanuvchilar mavjud emas*"
    else:
        text = f"👥 *FOYDALANUVCHILAR RO'YXATI:* {len(users)} ta\n\n"
        
        # Foydalanuvchilarni faollik bo'yicha saralash
        sorted_users = sorted(users.items(), 
                            key=lambda x: x[1].get('last_active', ''), 
                            reverse=True)
        
        for i, (user_id, user_data) in enumerate(list(sorted_users)[:20], 1):  # Faqat 20 tasini ko'rsatish
            user_name = user_data.get('name', 'Noma\'lum')
            username = f"@{user_data.get('username', '')}" if user_data.get('username') else "Yo'q"
            premium = "💎" if user_data.get('premium', False) else "⚪"
            referrals = user_data.get('referrals', 0)
            
            text += f"{i}. {premium} {user_name}\n"
            text += f"   👤 {username} | ID: `{user_id}`\n"
            text += f"   👥 Referallar: {referrals} ta\n\n"
    
    keyboard = [
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_user_stats")],
        [InlineKeyboardButton("📢 Xabar Yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_user_detail(query, user_id):
    """Foydalanuvchi haqida batafsil ma'lumot"""
    user_data = data['users'].get(user_id)
    
    if not user_data:
        await query.answer("❌ Foydalanuvchi topilmadi!")
        return
    
    user_name = user_data.get('name', 'Noma\'lum')
    username = f"@{user_data.get('username', '')}" if user_data.get('username') else "Yo'q"
    premium = "Ha 💎" if user_data.get('premium', False) else "Yo'q ⚪"
    referrals = user_data.get('referrals', 0)
    join_date = user_data.get('joined_date', 'Noma\'lum')
    last_active = user_data.get('last_active', 'Noma\'lum')
    
    text = f"""
👤 *FOYDALANUVCHI MA'LUMOTLARI*

🏷️ **Ism:** {user_name}
📱 **Username:** {username}
🆔 **ID:** `{user_id}`
💎 **Premium:** {premium}
👥 **Referallar:** {referrals} ta
📅 **Qo'shilgan sana:** {join_date[:10]}
🕐 **So'nggi faollik:** {last_active[:16]}
"""
    
    keyboard = [
        [InlineKeyboardButton("👥 Barcha Foydalanuvchilar", callback_data="admin_user_list")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def start_broadcast(query, context: ContextTypes.DEFAULT_TYPE):
    """Xabar yuborishni boshlash"""
    context.user_data['broadcasting'] = True
    
    text = """
📢 *XABAR YUBORISH*

Endi barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring:

📝 *Xabar formati:*
• Matn
• Rasm + Matn
• Tugmalar bilan xabar

⚠️ *Eslatma:* Xabar barcha foydalanuvchilarga yuboriladi!
"""
    
    keyboard = [
        [InlineKeyboardButton("❌ Bekor Qilish", callback_data="admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xabar yuborishni qayta ishlash"""
    user_id = update.effective_user.id
    if not is_admin(user_id) or not context.user_data.get('broadcasting'):
        return
    
    message = update.message
    users = data['users']
    total_users = len(users)
    successful = 0
    failed = 0
    
    # Xabarni yuborish jarayoni
    broadcast_text = f"📢 *Admin xabarı:*\n\n{message.text if message.text else ''}"
    
    for user_id_str in users.keys():
        try:
            if message.text:
                await context.bot.send_message(
                    chat_id=int(user_id_str),
                    text=broadcast_text,
                    parse_mode='Markdown'
                )
            elif message.photo:
                await context.bot.send_photo(
                    chat_id=int(user_id_str),
                    photo=message.photo[-1].file_id,
                    caption=broadcast_text,
                    parse_mode='Markdown'
                )
            successful += 1
        except Exception as e:
            logger.error(f"Xabar yuborishda xato {user_id_str}: {e}")
            failed += 1
        
        # Kichik kutish vaqti
        await asyncio.sleep(0.1)
    
    # Natijani ko'rsatish
    result_text = f"""
✅ *XABAR YUBORISH NATIJASI*

📊 **Statistika:**
• Jami foydalanuvchilar: {total_users} ta
• Muvaffaqiyatli: {successful} ta
• Xatolik: {failed} ta
• Muvaffaqiyat darajasi: {(successful/max(total_users, 1)*100):.1f}%

📝 Yuborilgan xabar: {message.text[:100] + '...' if message.text and len(message.text) > 100 else message.text}
"""
    
    await update.message.reply_text(result_text, parse_mode='Markdown')
    context.user_data.pop('broadcasting', None)

# ... (qolgan funksiyalar o'zgarmaydi, faqat admin paneli yangilandi)

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    # Xabar yuborish rejimi
    if context.user_data.get('broadcasting'):
        await handle_broadcast_message(update, context)
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

def main():
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handlerlar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
        app.add_handler(MessageHandler(filters.PHOTO, handle_admin_message))
        
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        print("🤖 Bot ishlayapti...")
        print(f"👑 Admin ID: {ADMIN_ID}")
        print("🎰 Bukmeker tugmalari qo'shildi: 1xBet, MelBet, DB Bet")
        print("📊 Mukammal admin paneli qo'shildi!")
        print("📢 Xabar yuborish tizimi faollashtirildi!")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    import asyncio
    main()
