import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

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
    except FileNotFoundError:
        # Fayl mavjud emas, boshlang'ich ma'lumotlarni yaratamiz
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data
    except Exception as e:
        print(f"Ma'lumotlarni yuklashda xato: {e}")
        return default_data

# Ma'lumotlarni saqlash
def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ma'lumotlarni saqlashda xato: {e}")
        return False

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
        [InlineKeyboardButton("➕ Yangi bukmeker", callback_data="admin_new")],
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
        await edit_bookmaker(query, bookmaker_id, context)
    
    elif action == "admin_new":
        await new_bookmaker(query, context)
    
    elif action == "admin_settings":
        await show_admin_settings(query)
    
    elif action == "admin_stats":
        await show_admin_stats(query)
    
    elif action.startswith("admin_toggle_"):
        bookmaker_id = action.replace("admin_toggle_", "")
        await toggle_bookmaker(query, bookmaker_id)
    
    elif action.startswith("admin_delete_"):
        bookmaker_id = action.replace("admin_delete_", "")
        await delete_bookmaker(query, bookmaker_id)

async def edit_bookmaker(query, bookmaker_id, context: ContextTypes.DEFAULT_TYPE):
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

*O'zgartirish uchun quyidagi formatda xabar yuboring:*
`nomi|apk_havola|reg_havola|tavsif`

*Misol:*
`1xBet|https://1xbet.com/new.apk|https://1xbet.com/new-reg|Yangi tavsif`"""

    keyboard = [
        [InlineKeyboardButton("🔘 Holatni o'zgartirish", callback_data=f"admin_toggle_{bookmaker_id}")],
        [InlineKeyboardButton("🗑 O'chirish", callback_data=f"admin_delete_{bookmaker_id}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Contextga ma'lumot saqlaymiz
    context.user_data['waiting_for_edit'] = bookmaker_id
    context.user_data['waiting_type'] = 'edit_bookmaker'
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def new_bookmaker(query, context: ContextTypes.DEFAULT_TYPE):
    """Yangi bukmeker qo'shish"""
    text = """
➕ *Yangi Bukmeker Qo'shish*

*Quyidagi formatda ma'lumot yuboring:*
`id|nomi|apk_havola|reg_havola|tavsif`

*Misol:*
`pinbet PinBet https://pinbet.com/apk https://pinbet.com/reg Yangi bukmeker platformasi`

*Eslatma:* ID faqat harf va raqamlardan iborat bo'lsin (masalan: pinbet)"""

    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Contextga ma'lumot saqlaymiz
    context.user_data['waiting_type'] = 'new_bookmaker'
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def toggle_bookmaker(query, bookmaker_id):
    """Bukmeker holatini o'zgartirish"""
    if bookmaker_id in data['bookmakers']:
        data['bookmakers'][bookmaker_id]['active'] = not data['bookmakers'][bookmaker_id]['active']
        if save_data(data):
            status = "faol" if data['bookmakers'][bookmaker_id]['active'] else "nofaol"
            await query.message.reply_text(f"✅ {data['bookmakers'][bookmaker_id]['name']} {status} holatga o'zgartirildi!")
        else:
            await query.message.reply_text("❌ Saqlashda xato!")
    
    await show_admin_panel(query)

async def delete_bookmaker(query, bookmaker_id):
    """Bukmekerni o'chirish"""
    if bookmaker_id in data['bookmakers']:
        bookmaker_name = data['bookmakers'][bookmaker_id]['name']
        del data['bookmakers'][bookmaker_id]
        if save_data(data):
            await query.message.reply_text(f"✅ {bookmaker_name} o'chirildi!")
        else:
            await query.message.reply_text("❌ Saqlashda xato!")
    
    await show_admin_panel(query)

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin xabarlarini qayta ishlash"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    if 'waiting_type' not in context.user_data:
        return
    
    message_text = update.message.text
    
    if context.user_data['waiting_type'] == 'edit_bookmaker':
        bookmaker_id = context.user_data['waiting_for_edit']
        await process_bookmaker_edit(update, context, bookmaker_id, message_text)
    
    elif context.user_data['waiting_type'] == 'new_bookmaker':
        await process_new_bookmaker(update, context, message_text)

async def process_bookmaker_edit(update: Update, context: ContextTypes.DEFAULT_TYPE, bookmaker_id: str, message_text: str):
    """Bukmeker tahririni qayta ishlash"""
    try:
        parts = message_text.split('|')
        if len(parts) >= 4:
            name = parts[0].strip()
            apk = parts[1].strip()
            reg = parts[2].strip()
            desc = parts[3].strip()
            
            # Ma'lumotlarni yangilash
            data['bookmakers'][bookmaker_id]['name'] = name
            data['bookmakers'][bookmaker_id]['apk'] = apk
            data['bookmakers'][bookmaker_id]['reg'] = reg
            data['bookmakers'][bookmaker_id]['desc'] = desc
            
            if save_data(data):
                await update.message.reply_text(f"✅ {name} muvaffaqiyatli yangilandi!")
            else:
                await update.message.reply_text("❌ Saqlashda xato!")
        else:
            await update.message.reply_text("❌ Noto'g'ri format! Iltimos, to'g'ri formatda yuboring.")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")
    
    # Contextni tozalash
    context.user_data.pop('waiting_type', None)
    context.user_data.pop('waiting_for_edit', None)
    
    await show_admin_panel_after_edit(update, context)

async def process_new_bookmaker(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
    """Yangi bukmeker qo'shish"""
    try:
        parts = message_text.split('|')
        if len(parts) >= 4:
            bookmaker_id = parts[0].strip().lower()
            name = parts[1].strip()
            apk = parts[2].strip()
            reg = parts[3].strip()
            desc = parts[4].strip() if len(parts) > 4 else "Yangi bukmeker platformasi"
            
            # ID tekshirish
            if bookmaker_id in data['bookmakers']:
                await update.message.reply_text("❌ Bu ID allaqachon mavjud!")
                return
            
            # Yangi bukmeker qo'shish
            data['bookmakers'][bookmaker_id] = {
                'name': name,
                'apk': apk,
                'reg': reg,
                'desc': desc,
                'active': True
            }
            
            if save_data(data):
                await update.message.reply_text(f"✅ {name} muvaffaqiyatli qo'shildi!")
            else:
                await update.message.reply_text("❌ Saqlashda xato!")
        else:
            await update.message.reply_text("❌ Noto'g'ri format! Iltimos, to'g'ri formatda yuboring.")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")
    
    # Contextni tozalash
    context.user_data.pop('waiting_type', None)
    
    await show_admin_panel_after_edit(update, context)

async def show_admin_panel_after_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tahrirdan keyin admin panelini ko'rsatish"""
    # Bu funksiya callback emas, shuning uchun oddiy xabar yuboramiz
    user_id = update.effective_user.id
    if is_admin(user_id):
        text = "👑 *Admin Panel* - Yangilandi!\n\nQuyidagi bukmekerlarni boshqarish:"
        
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
            [InlineKeyboardButton("➕ Yangi bukmeker", callback_data="admin_new")],
            [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="admin_settings")],
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Qolgan funksiyalar (show_signal_options, show_referral_link, show_help, show_bonus, start_callback)
# Oldingi koddagidek qoladi, faqat data ni global o'zgaruvchidan olish kerak

async def show_signal_options(query, user_id):
    """Signal variantlari"""
    user_data = data['users'].get(str(user_id), {'referrals': 0})
    ref_count = user_data['referrals']
    min_ref = data['settings']['min_referrals']
    max_ref = data['settings']['max_referrals']
    
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

📊 *Sizning referallaringiz:* {ref_count} ta"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="signal")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_help(query):
    """Yordam menyusi"""
    text = "📚 *Qo'llanma* - Oldingi kabi..."
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_bonus(query):
    """Bonuslar menyusi"""
    text = "🎁 *Bonuslar* - Oldingi kabi..."
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
    
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎯 Salom {user.first_name}!\n🍎 *Apple of Fortune Botiga Xush Kelibsiz!*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

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
        if save_data(data):
            await update.message.reply_text("✅ Signal URL yangilandi!")
        else:
            await update.message.reply_text("❌ Saqlashda xato!")
    
    elif context.args[0] == "min_ref" and len(context.args) > 1:
        try:
            data['settings']['min_referrals'] = int(context.args[1])
            if save_data(data):
                await update.message.reply_text("✅ Minimal referal yangilandi!")
            else:
                await update.message.reply_text("❌ Saqlashda xato!")
        except:
            await update.message.reply_text("❌ Noto'g'ri son!")
    
    elif context.args[0] == "max_ref" and len(context.args) > 1:
        try:
            data['settings']['max_referrals'] = int(context.args[1])
            if save_data(data):
                await update.message.reply_text("✅ Maksimal referal yangilandi!")
            else:
                await update.message.reply_text("❌ Saqlashda xato!")
        except:
            await update.message.reply_text("❌ Noto'g'ri son!")

def main():
    """Asosiy dastur"""
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handlerlar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("settings", admin_settings))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
        
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        print("🤖 Bot ishlayapti...")
        print(f"👑 Admin ID: {ADMIN_ID}")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
