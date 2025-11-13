import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot tokeni - o'z tokeningizni qo'ying
TOKEN = "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g"

# Foydalanuvchi ma'lumotlari (vaqtincha)
users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("💰 Daromad olish", callback_data="earn")],
        [InlineKeyboardButton("📡 Signal olish", callback_data="signal")],
        [InlineKeyboardButton("📚 Yordam", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Salom {user.first_name}! 👋\n"
        "Apple of Fortune botiga xush kelibsiz!\n\n"
        "Quyidagi tugmalardan foydalaning:",
        reply_markup=reply_markup
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
    
    elif query.data == "back":
        await start_callback(query)
    
    elif query.data in ["1xbet", "melbet", "dbbet"]:
        await show_bookmaker_info(query, query.data)

async def show_bookmakers(query):
    """Bukmekerlar ro'yxati"""
    keyboard = [
        [InlineKeyboardButton("1xBet", callback_data="1xbet")],
        [InlineKeyboardButton("MelBet", callback_data="melbet")],
        [InlineKeyboardButton("DBBet", callback_data="dbbet")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💰 Daromad olish uchun bukmekerni tanlang:",
        reply_markup=reply_markup
    )

async def show_bookmaker_info(query, bookmaker):
    """Bukmeker ma'lumotlari"""
    bookmaker_info = {
        "1xbet": {
            "name": "1xBet",
            "apk": "https://1xbet.com/download",
            "reg": "https://1xbet.com/registration"
        },
        "melbet": {
            "name": "MelBet", 
            "apk": "https://melbet.com/download",
            "reg": "https://melbet.com/registration"
        },
        "dbbet": {
            "name": "DBBet",
            "apk": "https://dbbet.com/download", 
            "reg": "https://dbbet.com/registration"
        }
    }
    
    info = bookmaker_info[bookmaker]
    text = f"""
📱 {info['name']}

📲 APK yuklab olish: {info['apk']}
📝 Ro'yxatdan o'tish: {info['reg']}

💡 Ro'yxatdan o'tgach, daromad olishni boshlashingiz mumkin!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="earn")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_signal_options(query, user_id):
    """Signal variantlari"""
    # Foydalanuvchi referallar soni
    ref_count = users.get(user_id, {}).get('referrals', 0)
    
    if ref_count >= 20:
        signal_text = "🚀 Signal NOW - Bosing va signal oling!"
        signal_button = [InlineKeyboardButton("📡 Signal NOW", url="https://signal7.digital")]
    elif ref_count >= 5:
        signal_text = f"🔒 Signal uchun {20 - ref_count} ta referal kerak"
        signal_button = [InlineKeyboardButton("📤 Referal olish", callback_data="get_ref")]
    else:
        signal_text = f"🔒 Signal uchun {5 - ref_count} ta referal kerak" 
        signal_button = [InlineKeyboardButton("📤 Referal olish", callback_data="get_ref")]
    
    text = f"""
📡 Signal olish

{signal_text}
Sizning referallaringiz: {ref_count} ta"""
    
    keyboard = []
    if ref_count >= 20:
        keyboard.append(signal_button)
    
    keyboard.extend([
        [InlineKeyboardButton("📤 Referal havola", callback_data="ref_link")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_help(query):
    """Yordam menyusi"""
    text = """
📚 Botdan foydalanish:

💰 Daromad olish - bukmekerlar orqali
📡 Signal olish - referal sistemasi orqali  
📤 Referal - do'stlaringizni taklif qiling

Har 20 ta referal uchun 1 ta signal!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def start_callback(query):
    """Callback uchun start"""
    user = query.from_user
    keyboard = [
        [InlineKeyboardButton("💰 Daromad olish", callback_data="earn")],
        [InlineKeyboardButton("📡 Signal olish", callback_data="signal")],
        [InlineKeyboardButton("📚 Yordam", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"Salom {user.first_name}! 👋\n"
        "Apple of Fortune botiga xush kelibsiz!\n\n"
        "Quyidagi tugmalardan foydalaning:",
        reply_markup=reply_markup
    )

def main():
    """Asosiy dastur"""
    # Botni yaratish
    app = Application.builder().token(TOKEN).build()
    
    # Handlerlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Botni ishga tushirish
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
