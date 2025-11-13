import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot tokeni
TOKEN = "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g"

# Admin ID (o'zingizning ID ingizni qo'ying)
ADMIN_ID = 7633561058  # O'z ID ingizni qo'ying

# Ma'lumotlarni saqlash fayli
DATA_FILE = "data.json"

# Boshlang'ich ma'lumotlar
default_data = {
    "bookmakers": {
        "1xbet": {
            "name": "1xBet",
            "apk": "https://1xbet.com/download",
            "reg": "https://1xbet.com/registration",
            "desc": "Dunyoning eng yirik bukmekerlaridan biri",
            "active": True
        },
        "melbet": {
            "name": "MelBet", 
            "apk": "https://melbet.com/download",
            "reg": "https://melbet.com/registration",
            "desc": "Ishtonchli va tez to'lov qiladi",
            "active": True
        },
        "dbbet": {
            "name": "DBBet",
            "apk": "https://dbbet.com/download", 
            "reg": "https://dbbet.com/registration",
            "desc": "Yangi va rivojlanayotgan platforma",
            "active": True
        }
    },
    "users": {},
    "settings": {
        "signal_url": "https://signal7.digital",
        "min_referrals": 5,
        "max_referrals": 20
    }
}

# Ma'lumotlarni yuklash
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_data

# Ma'lumotlarni saqlash
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Ma'lumotlarni yuklab olish
data = load_data()

def is_admin(user_id):
    """Admin tekshirish"""
    return user_id == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user = update.effective_user
    user_id = user.id
    
    # Yangi foydalanuvchini qo'shish
    if str(user_id) not in data['users']:
        data['users'][str(user_id)] = {
            'name': user.first_name,
            'referrals': 0,
            'username': user.username
        }
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
        [InlineKeyboardButton("💰 Daromad olishni boshlash", callback_data="earn")],
        [InlineKeyboardButton("📡 Signal olish", callback_data="signal")],
        [InlineKeyboardButton("📚 Qo'llanma", callback_data="help")],
        [InlineKeyboardButton("🎁 Bonus", callback_data="bonus")]
    ]
    
    # Admin paneli
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎯 Salom {user.first_name}!\n\n"
        "🍎 *Apple of Fortune Botiga Xush Kelibsiz!*\n\n"
        "📈 Bizning bot orqali siz:\n"
        "• 💰 Daromad olishingiz mumkin\n"
        "• 📡 Ishonchli signal olasiz\n"
        "• 👥 Referal orqali qo'shimcha foyda olasiz",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalarni boshqarish"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "earn":
        await show_bookmakers(query)
    
    elif query.data == "signal":
        await show_signal_options(query, user_id)
    
    elif query.data == "help":
        await show_help(query)
    
    elif query.data == "bonus":
        await show_bonus(query)
    
    elif query.data == "back":
        await start_callback(query)
    
    elif query.data == "ref_link":
        await show_referral_link(query, user_id)
    
    elif query.data == "admin":
        if is_admin(user_id):
            await show_admin_panel(query)
        else:
            await query.message.reply_text("❌ Siz admin emassiz!")
    
    elif query.data.startswith("admin_"):
        if is_admin(user_id):
            await handle_admin_actions(query, context)
        else:
            await query.message.reply_text("❌ Siz admin emassiz!")
    
    elif query.data in ["1xbet", "melbet", "dbbet"]:
        await show_bookmaker_info(query, query.data)

async def show_bookmakers(query):
    """Bukmekerlar ro'yxati"""
    keyboard = []
    for bookmaker_id, bookmaker in data['bookmakers'].items():
        if bookmaker['active']:
            keyboard.append([InlineKeyboardButton(bookmaker['name'], callback_data=bookmaker_id)])
    
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📊 *Daromad olishni boshlash uchun bukmekerni tanlang:*\n\n"
        "Har bir bukmeker uchun:\n"
        "• 📱 APK fayl\n" 
        "• 📝 Ro'yxatdan o'tish havolasi",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_bookmaker_info(query, bookmaker):
    """Bukmeker ma'lumotlari"""
    if bookmaker not in data['bookmakers']:
        await query.message.reply_text("❌ Bu bukmeker mavjud emas!")
        return
    
    info = data['bookmakers'][bookmaker]
    
    if not info['active']:
        await query.message.reply_text("❌ Bu bukmeker hozircha mavjud emas!")
        return
    
    text = f"""
📱 *{info['name']}*

{info['desc']}

⬇️ *APK yuklab olish:*
{info['apk']}

📝 *Ro'yxatdan o'tish:*
{info['reg']}

💡 *Eslatma:* Ro'yxatdan o'tgach, daromad olishni boshlashingiz mumkin!"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="earn")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_signal_options(query, user_id):
    """Signal variantlari"""
    user_data = data['users'].get(str(user_id), {'referrals': 0})
    ref_count = user_data['referrals']
    min_ref = data['settings']['min_referrals']
    max_ref = data['settings']['max_referrals']
    
    # Referal talablari
    if ref_count >= max_ref:
        status = "🟢 TAYYOR"
        signal_text = "Signal olish uchun bosing!"
        required = 0
    elif ref_count >= min_ref:
        status = "🟡 KUTILMOQDA"
        required = max_ref - ref_count
        signal_text = f"Yana {required} ta referal kerak"
    else:
        status = "🔴 YOPIQ"
        required = min_ref - ref_count
        signal_text = f"{required} ta referal kerak"
    
    text = f"""
📡 *Signal Olish*

🎯 Status: {status}
👥 Sizning referallaringiz: {ref_count} ta
📋 Talab: {signal_text}

💡 *Qoida:*
• {min_ref} ta referal - signal ko'rish mumkin
• {max_ref} ta referal - to'liq signal olish mumkin"""
    
    keyboard = []
    
    if ref_count >= max_ref:
        keyboard.append([InlineKeyboardButton("🚀 SIGNAL NOW", url=data['settings']['signal_url'])])
    
    keyboard.extend([
        [InlineKeyboardButton("📤 Referal havolam", callback_data="ref_link")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_referral_link(query, user_id):
    """Referal havolasini ko'rsatish"""
    bot_username = (await query.message._bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
    
    user_data = data['users'].get(str(user_id), {'referrals': 0})
    ref_count = user_data['referrals']
    
    text = f"""
📤 *Referal Havolangiz*

`{ref_link}`

👥 *Qanday ishlatish:*
1. Ushbu havolani do'stlaringizga yuboring
2. Har bir yangi foydalanuvchi +1 referal
3. {data['settings']['max_referrals']} ta referal = To'liq signal access

📊 *Sizning referallaringiz:* {ref_count} ta

💡 *Maslahat:* Havolani koproq odamga yuboring, tezroq signal oling!"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="signal")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_admin_panel(query):
    """Admin paneli"""
    text = """
👑 *Admin Panel*

Quyidagi bukmekerlarni boshqarish:"""

    keyboard = []
    
    for bookmaker_id, bookmaker in data['bookmakers'].items():
        status = "🟢" if bookmaker['active'] else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {bookmaker['name']}", 
                callback_data=f"admin_edit_{bookmaker_id}"
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="admin_settings")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_admin_actions(query, context: ContextTypes.DEFAULT_TYPE):
    """Admin harakatlari"""
    action = query.data
    
    if action.startswith("admin_edit_"):
        bookmaker_id = action.replace("admin_edit_", "")
        await edit_bookmaker(query, bookmaker_id)
    
    elif action == "admin_settings":
        await show_admin_settings(query)
    
    elif action == "admin_stats":
        await show_admin_stats(query)
    
    elif action.startswith("admin_save_"):
        bookmaker_id = action.replace("admin_save_", "")
        await save_bookmaker_changes(query, context, bookmaker_id)
    
    elif action.startswith("admin_toggle_"):
        bookmaker_id = action.replace("admin_toggle_", "")
        await toggle_bookmaker(query, bookmaker_id)

async def edit_bookmaker(query, bookmaker_id):
    """Bukmekerni tahrirlash"""
    if bookmaker_id not in data['bookmakers']:
        await query.message.reply_text("❌ Bu bukmeker mavjud emas!")
        return
    
    bookmaker = data['bookmakers'][bookmaker_id]
    
    text = f"""
✏️ *Tahrirlash: {bookmaker['name']}*

🆔 ID: `{bookmaker_id}`
📛 Nomi: `{bookmaker['name']}`
📱 APK: `{bookmaker['apk']}`
🔗 Ro'yxatdan o'tish: `{bookmaker['reg']}`
📝 Tavsif: `{bookmaker['desc']}`
🔘 Holati: {'🟢 Faol' if bookmaker['active'] else '🔴 Nofaol'}

Yangi ma'lumotlarni quyidagi formatda yuboring:
`nomi|apk_havola|reg_havola|tavsif`

Misol:
`1xBet|https://1xbet.com/apk|https://1xbet.com/reg|Dunyoning eng yirik bukmekeri`"""

    keyboard = [
        [InlineKeyboardButton("🔘 Holatni o'zgartirish", callback_data=f"admin_toggle_{bookmaker_id}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Contextga ma'lumot saqlaymiz
    context.user_data['editing_bookmaker'] = bookmaker_id
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def toggle_bookmaker(query, bookmaker_id):
    """Bukmeker holatini o'zgartirish"""
    if bookmaker_id in data['bookmakers']:
        data['bookmakers'][bookmaker_id]['active'] = not data['bookmakers'][bookmaker_id]['active']
        save_data(data)
        
        status = "faol" if data['bookmakers'][bookmaker_id]['active'] else "nofaol"
        await query.message.reply_text(f"✅ {data['bookmakers'][bookmaker_id]['name']} {status} holatga o'zgartirildi!")
    
    await show_admin_panel(query)

async def save_bookmaker_changes(query, context: ContextTypes.DEFAULT_TYPE, bookmaker_id):
    """O'zgarishlarni saqlash"""
    # Bu yerda foydalanuvchi kiritgan ma'lumotlarni qabul qilamiz
    await query.message.reply_text("Iltimos, yangi ma'lumotlarni yuboring...")

async def show_admin_settings(query):
    """Admin sozlamalari"""
    settings = data['settings']
    
    text = f"""
⚙️ *Sozlamalar*

🔗 Signal URL: `{settings['signal_url']}`
👥 Minimal referal: `{settings['min_referrals']}`
👥 Maksimal referal: `{settings['max_referrals']}`

Sozlamalarni o'zgartirish uchun /settings buyrug'idan foydalaning."""

    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_admin_stats(query):
    """Statistika"""
    total_users = len(data['users'])
    total_referrals = sum(user['referrals'] for user in data['users'].values())
    
    text = f"""
📊 *Statistika*

👥 Jami foydalanuvchilar: `{total_users}`
📤 Jami referallar: `{total_referrals}`

📈 Faol bukmekerlar:"""
    
    for bookmaker_id, bookmaker in data['bookmakers'].items():
        if bookmaker['active']:
            text += f"\n• {bookmaker['name']} - 🟢 Faol"
        else:
            text += f"\n• {bookmaker['name']} - 🔴 Nofaol"

    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Admin buyruqlari
async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sozlamalarni o'zgartirish"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Sozlamalarni o'zgartirish:\n\n"
            "Signal URL ni o'zgartirish:\n"
            "/settings signal_url yangi_url\n\n"
            "Minimal referal:\n"
            "/settings min_ref son\n\n"
            "Maksimal referal:\n"
            "/settings max_ref son"
        )
        return
    
    if context.args[0] == "signal_url" and len(context.args) > 1:
        data['settings']['signal_url'] = context.args[1]
        save_data(data)
        await update.message.reply_text("✅ Signal URL yangilandi!")
    
    elif context.args[0] == "min_ref" and len(context.args) > 1:
        try:
            data['settings']['min_referrals'] = int(context.args[1])
            save_data(data)
            await update.message.reply_text("✅ Minimal referal yangilandi!")
        except:
            await update.message.reply_text("❌ Noto'g'ri son!")
    
    elif context.args[0] == "max_ref" and len(context.args) > 1:
        try:
            data['settings']['max_referrals'] = int(context.args[1])
            save_data(data)
            await update.message.reply_text("✅ Maksimal referal yangilandi!")
        except:
            await update.message.reply_text("❌ Noto'g'ri son!")

async def edit_bukmeker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bukmekerni tahrirlash"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    if not context.args or len(context.args) < 5:
        await update.message.reply_text(
            "Bukmekerni tahrirlash:\n\n"
            "Format: /edit bukmeker_id nomi apk_havola reg_havola tavsif\n\n"
            "Misol:\n"
            "/edit 1xbet 1xBet https://1xbet.com/apk https://1xbet.com/reg 'Dunyoning eng yirik bukmekeri'"
        )
        return
    
    bookmaker_id = context.args[0]
    if bookmaker_id not in data['bookmakers']:
        await update.message.reply_text("❌ Bu bukmeker mavjud emas!")
        return
    
    # Yangi ma'lumotlarni saqlash
    data['bookmakers'][bookmaker_id]['name'] = context.args[1]
    data['bookmakers'][bookmaker_id]['apk'] = context.args[2]
    data['bookmakers'][bookmaker_id]['reg'] = context.args[3]
    data['bookmakers'][bookmaker_id]['desc'] = ' '.join(context.args[4:])
    
    save_data(data)
    await update.message.reply_text("✅ Bukmeker ma'lumotlari yangilandi!")

# Qolgan funksiyalar (show_help, show_bonus, start_callback) oldingi kabi...

async def show_help(query):
    """Yordam menyusi"""
    text = """
📚 *Botdan Foydalanish Qo'llanmasi*

🎮 *Apple of Fortune O'yini:*
Bu popular slot o'yini bo'lib, yuqori daromad keltiradi.

💰 *Daromad olish:*
1. Bukmekerni tanlang (1xBet, MelBet, DBBet)
2. APK yuklab oling
3. Ro'yxatdan o'ting
4. O'ynashni boshlang

📡 *Signal olish:*
• 5 ta referal - cheklangan signal
• 20 ta referal - to'liq signal

👥 *Referal tizimi:*
Har bir do'stingiz sizga +1 referal keltiradi

🎁 *Bonuslar:*
Har hafta yangi bonuslar va takliflar!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_bonus(query):
    """Bonuslar menyusi"""
    text = """
🎁 *Bonuslar va Takliflar*

✨ *Hozirgi Aksiyalar:*

🏆 *Yangi o'yinchilar uchun:*
• +100% depozit bonus
• 10 ta bepul spin
• 5000 so'm start bonus

📈 *Doimiy bonuslar:*
• Har bir do'st taklifi uchun 50% bonus
• Haftalik cashback 15% gacha
• Oylik turnir 1,000,000 so'm g'olibiga

🔥 *Maxsus taklif:*
Har 5 ta muvaffaqiyatli signaldan keyin maxsus bonus!

💡 *Eslatma:* Bonuslardan foydalanish uchun bukmekerlar orqali ro'yxatdan o'ting!"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Daromad olish", callback_data="earn")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def start_callback(query):
    """Callback uchun start"""
    user = query.from_user
    user_id = user.id
    
    keyboard = [
        [InlineKeyboardButton("💰 Daromad olishni boshlash", callback_data="earn")],
        [InlineKeyboardButton("📡 Signal olish", callback_data="signal")],
        [InlineKeyboardButton("📚 Qo'llanma", callback_data="help")],
        [InlineKeyboardButton("🎁 Bonus", callback_data="bonus")]
    ]
    
    # Admin paneli
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎯 Salom {user.first_name}!\n\n"
        "🍎 *Apple of Fortune Botiga Xush Kelibsiz!*\n\n"
        "📈 Bizning bot orqali siz:\n"
        "• 💰 Daromad olishingiz mumkin\n"
        "• 📡 Ishonchli signal olasiz\n"
        "• 👥 Referal orqali qo'shimcha foyda olasiz",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def main():
    """Asosiy dastur"""
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handlerlar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("settings", admin_settings))
        app.add_handler(CommandHandler("edit", edit_bukmeker))
        app.add_handler(CallbackQueryHandler(button_handler))
        
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        print("🤖 Bot ishlayapti...")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
