import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Bot tokeni
TOKEN = "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g"

# Admin ID (o'zingizning ID ingizni qo'ying)
ADMIN_ID = 7633561058  # O'z ID ingizni qo'ying

# Ma'lumotlarni saqlash fayli
DATA_FILE = "data.json"
FILES_DIR = "files"

# Loggerni sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fayllar katalogini yaratish
os.makedirs(FILES_DIR, exist_ok=True)

# Boshlang'ich ma'lumotlar
default_data = {
    "bookmakers": {
        "1xbet": {
            "name": "1xBet",
            "apk": "",
            "reg": "https://1xbet.com/registration",
            "desc": "Dunyoning eng yirik bukmekerlaridan biri",
            "active": True,
            "file_id": None
        },
        "melbet": {
            "name": "MelBet", 
            "apk": "",
            "reg": "https://melbet.com/registration",
            "desc": "Ishtonchli va tez to'lov qiladi",
            "active": True,
            "file_id": None
        },
        "dbbet": {
            "name": "DBBet",
            "apk": "",
            "reg": "https://dbbet.com/registration",
            "desc": "Yangi va rivojlanayotgan platforma",
            "active": True,
            "file_id": None
        }
    },
    "users": {},
    "settings": {
        "signal_url": "https://signal7.digital",
        "min_referrals": 5,
        "max_referrals": 20
    },
    "messages": {
        "welcome": "🎯 Apple of Fortune Botiga Xush Kelibsiz!",
        "signal_info": "📡 Signal olish uchun referal yigishingiz kerak!",
        "bonus_info": "🎁 Ajoyib bonuslar sizni kutmoqda!"
    }
}

# Ma'lumotlarni yuklash
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        save_data(default_data)
        return default_data
    except Exception as e:
        logger.error(f"Ma'lumotlarni yuklashda xato: {e}")
        return default_data

# Ma'lumotlarni saqlash
def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ma'lumotlarni saqlashda xato: {e}")
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
        data['messages']['welcome'],
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
            status = "📱" if bookmaker['file_id'] else "📄"
            keyboard.append([InlineKeyboardButton(
                f"{status} {bookmaker['name']}", 
                callback_data=bookmaker_id
            )])
    
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📊 *Daromad olishni boshlash uchun bukmekerni tanlang:*\n\n"
        "📱 - APK fayli mavjud\n"
        "📄 - Faqat havola",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_bookmaker_info(query, bookmaker_id):
    """Bukmeker ma'lumotlari"""
    if bookmaker_id not in data['bookmakers']:
        await query.message.reply_text("❌ Bu bukmeker mavjud emas!")
        return
    
    info = data['bookmakers'][bookmaker_id]
    
    if not info['active']:
        await query.message.reply_text("❌ Bu bukmeker hozircha mavjud emas!")
        return
    
    text = f"""
📱 *{info['name']}*

{info['desc']}

📝 *Ro'yxatdan o'tish:*
{info['reg']}"""

    # Agar APK fayli mavjud bo'lsa
    if info['file_id']:
        text += f"\n\n⬇️ *APK faylini yuklab olish:*"
        # Faylni yuborish
        try:
            await query.message.reply_document(
                document=info['file_id'],
                caption=text,
                parse_mode='Markdown'
            )
            return
        except Exception as e:
            logger.error(f"Fayl yuborishda xato: {e}")
            text += f"\n\n❌ Fayl yuklab olinmadi. Iltimos, keyinroq urinib ko'ring."
    elif info['apk']:
        text += f"\n\n⬇️ *APK yuklab olish:*\n{info['apk']}"
    else:
        text += f"\n\n❌ APK fayli hozircha mavjud emas."

    text += f"\n\n💡 *Eslatma:* Ro'yxatdan o'tgach, daromad olishni boshlashingiz mumkin!"
    
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

*Bukmekerlarni boshqarish:*"""

    keyboard = []
    
    for bookmaker_id, bookmaker in data['bookmakers'].items():
        status = "🟢" if bookmaker['active'] else "🔴"
        file_status = "📱" if bookmaker['file_id'] else "📄"
        keyboard.append([
            InlineKeyboardButton(
                f"{status}{file_status} {bookmaker['name']}", 
                callback_data=f"admin_edit_{bookmaker_id}"
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("➕ Yangi bukmeker", callback_data="admin_new")],
        [InlineKeyboardButton("💬 Xabarlarni boshqarish", callback_data="admin_messages")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="admin_settings")],
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
    
    elif action == "admin_messages":
        await show_message_management(query)
    
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
    
    elif action.startswith("admin_msg_"):
        message_type = action.replace("admin_msg_", "")
        await edit_message(query, message_type, context)

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
🔗 Ro'yxatdan o'tish: `{bookmaker['reg']}`
📝 Tavsif: `{bookmaker['desc']}`
🔘 Holati: {'🟢 Faol' if bookmaker['active'] else '🔴 Nofaol'}
📱 APK: {'Mavjud' if bookmaker['file_id'] else 'Mavjud emas'}

*O'zgartirish uchun:*
1. *Fayl yuboring* - APK faylini yangilash
2. *Matn yuboring* - format: `nomi|reg_havola|tavsif`

*Misol:*
`1xBet|https://1xbet.com/new-reg|Yangi tavsif`"""

    keyboard = [
        [InlineKeyboardButton("📎 APK faylini yangilash", callback_data=f"admin_file_{bookmaker_id}")],
        [InlineKeyboardButton("🔘 Holatni o'zgartirish", callback_data=f"admin_toggle_{bookmaker_id}")],
        [InlineKeyboardButton("🗑 O'chirish", callback_data=f"admin_delete_{bookmaker_id}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Contextga ma'lumot saqlaymiz
    context.user_data['waiting_for_edit'] = bookmaker_id
    context.user_data['waiting_type'] = 'edit_bookmaker'
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin xabarlarini qayta ishlash"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    # Fayl yuborilgan bo'lsa
    if update.message.document:
        await handle_admin_file(update, context)
        return
    
    if 'waiting_type' not in context.user_data:
        return
    
    message_text = update.message.text
    
    if context.user_data['waiting_type'] == 'edit_bookmaker':
        bookmaker_id = context.user_data['waiting_for_edit']
        await process_bookmaker_edit(update, context, bookmaker_id, message_text)
    
    elif context.user_data['waiting_type'] == 'new_bookmaker':
        await process_new_bookmaker(update, context, message_text)
    
    elif context.user_data['waiting_type'] == 'edit_message':
        message_type = context.user_data['editing_message']
        await save_message(update, context, message_type, message_text)

async def handle_admin_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin tomonidan yuborilgan faylni qayta ishlash"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return
    
    if 'waiting_type' not in context.user_data:
        return
    
    if context.user_data['waiting_type'] == 'edit_bookmaker':
        bookmaker_id = context.user_data['waiting_for_edit']
        await process_bookmaker_file(update, context, bookmaker_id)

async def process_bookmaker_file(update: Update, context: ContextTypes.DEFAULT_TYPE, bookmaker_id: str):
    """Bukmeker faylini qayta ishlash"""
    try:
        document = update.message.document
        
        # Fayl hajmini tekshirish (10MB dan oshmasligi kerak)
        if document.file_size > 10 * 1024 * 1024:
            await update.message.reply_text("❌ Fayl hajmi 10MB dan kichik bo'lishi kerak!")
            return
        
        # Fayl ID sini saqlash
        data['bookmakers'][bookmaker_id]['file_id'] = document.file_id
        data['bookmakers'][bookmaker_id]['apk'] = ""  # Havolani tozalash
        
        if save_data(data):
            bookmaker_name = data['bookmakers'][bookmaker_id]['name']
            await update.message.reply_text(f"✅ {bookmaker_name} uchun APK fayli yangilandi!")
        else:
            await update.message.reply_text("❌ Saqlashda xato!")
    
    except Exception as e:
        logger.error(f"Fayl qayta ishlashda xato: {e}")
        await update.message.reply_text("❌ Faylni qayta ishlashda xato!")
    
    # Contextni tozalash
    context.user_data.pop('waiting_type', None)
    context.user_data.pop('waiting_for_edit', None)
    
    await show_admin_panel_after_edit(update, context)

async def process_bookmaker_edit(update: Update, context: ContextTypes.DEFAULT_TYPE, bookmaker_id: str, message_text: str):
    """Bukmeker tahririni qayta ishlash"""
    try:
        parts = message_text.split('|')
        if len(parts) >= 3:
            name = parts[0].strip()
            reg = parts[1].strip()
            desc = parts[2].strip()
            
            # Ma'lumotlarni yangilash
            data['bookmakers'][bookmaker_id]['name'] = name
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
        if len(parts) >= 3:
            bookmaker_id = parts[0].strip().lower()
            name = parts[1].strip()
            reg = parts[2].strip()
            desc = parts[3].strip() if len(parts) > 3 else "Yangi bukmeker platformasi"
            
            # ID tekshirish
            if bookmaker_id in data['bookmakers']:
                await update.message.reply_text("❌ Bu ID allaqachon mavjud!")
                return
            
            # Yangi bukmeker qo'shish
            data['bookmakers'][bookmaker_id] = {
                'name': name,
                'apk': "",
                'reg': reg,
                'desc': desc,
                'active': True,
                'file_id': None
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

async def show_message_management(query):
    """Xabarlarni boshqarish"""
    text = """
💬 *Xabarlarni Boshqarish*

Quyidagi xabarlarni tahrirlashingiz mumkin:"""

    keyboard = [
        [InlineKeyboardButton("👋 Xush kelish xabari", callback_data="admin_msg_welcome")],
        [InlineKeyboardButton("📡 Signal xabari", callback_data="admin_msg_signal_info")],
        [InlineKeyboardButton("🎁 Bonus xabari", callback_data="admin_msg_bonus_info")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def edit_message(query, message_type, context: ContextTypes.DEFAULT_TYPE):
    """Xabarni tahrirlash"""
    current_message = data['messages'].get(message_type, "")
    
    text = f"""
✏️ *Xabarni Tahrirlash*

Joriy xabar:
`{current_message}`

Yangi xabarni yuboring:"""
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="admin_messages")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Contextga ma'lumot saqlaymiz
    context.user_data['waiting_type'] = 'edit_message'
    context.user_data['editing_message'] = message_type
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message_type: str, new_text: str):
    """Xabarni saqlash"""
    data['messages'][message_type] = new_text
    if save_data(data):
        await update.message.reply_text("✅ Xabar muvaffaqiyatli yangilandi!")
    else:
        await update.message.reply_text("❌ Saqlashda xato!")
    
    # Contextni tozalash
    context.user_data.pop('waiting_type', None)
    context.user_data.pop('editing_message', None)
    
    await show_message_management_after_edit(update)

async def show_message_management_after_edit(update: Update):
    """Xabar tahriridan keyin menyuni ko'rsatish"""
    text = "💬 *Xabarlarni Boshqarish* - Yangilandi!"
    
    keyboard = [
        [InlineKeyboardButton("👋 Xush kelish xabari", callback_data="admin_msg_welcome")],
        [InlineKeyboardButton("📡 Signal xabari", callback_data="admin_msg_signal_info")],
        [InlineKeyboardButton("🎁 Bonus xabari", callback_data="admin_msg_bonus_info")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_admin_panel_after_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tahrirdan keyin admin panelini ko'rsatish"""
    text = "👑 *Admin Panel* - Yangilandi!"
    
    keyboard = []
    for bookmaker_id, bookmaker in data['bookmakers'].items():
        status = "🟢" if bookmaker['active'] else "🔴"
        file_status = "📱" if bookmaker['file_id'] else "📄"
        keyboard.append([
            InlineKeyboardButton(
                f"{status}{file_status} {bookmaker['name']}", 
                callback_data=f"admin_edit_{bookmaker_id}"
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("➕ Yangi bukmeker", callback_data="admin_new")],
        [InlineKeyboardButton("💬 Xabarlarni boshqarish", callback_data="admin_messages")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="admin_settings")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Qolgan funksiyalar (toggle_bookmaker, delete_bookmaker, show_admin_settings, show_admin_stats)
# va boshqa kerakli funksiyalar oldingi kabi...

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

async def new_bookmaker(query, context: ContextTypes.DEFAULT_TYPE):
    """Yangi bukmeker qo'shish"""
    text = """
➕ *Yangi Bukmeker Qo'shish*

*Quyidagi formatda ma'lumot yuboring:*
`id|nomi|reg_havola|tavsif`

*Misol:*
`pinbet PinBet https://pinbet.com/reg Yangi bukmeker platformasi`

*Keyin APK faylini yuborishingiz mumkin.*"""

    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['waiting_type'] = 'new_bookmaker'
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Signal, referral va boshqa funksiyalar oldingi kabi...

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
{data['messages']['signal_info']}

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

async def show_bonus(query):
    """Bonuslar menyusi"""
    text = data['messages']['bonus_info']
    
    keyboard = [
        [InlineKeyboardButton("💰 Daromad olish", callback_data="earn")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_help(query):
    """Yordam menyusi"""
    text = "📚 *Qo'llanma* - Oldingi kabi..."
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]]
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
        data['messages']['welcome'],
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
            file_status = " (APK mavjud)" if bookmaker['file_id'] else " (havola)"
            text += f"\n• {bookmaker['name']} - 🟢 Faol{file_status}"
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
        app.add_handler(MessageHandler(filters.Document.ALL, handle_admin_message))
        
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        print("🤖 Bot ishlayapti...")
        print(f"👑 Admin ID: {ADMIN_ID}")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")

if __name__ == "__main__":
    main()
