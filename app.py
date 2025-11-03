import os
import logging
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot ishlayapti!"

# Bot tokenini environment dan olamiz
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# APK fayllar manzillari
APK_FILES = {
    "1xbet": "https://example.com/1xbet.apk",
    "winwin": "https://example.com/winwin.apk", 
    "melbet": "https://example.com/melbet.apk",
    "megapari": "https://example.com/megapari.apk",
    "dbbet": "https://example.com/dbbet.apk",
    "888starz": "https://example.com/888starz.apk",
    "lyukypari": "https://example.com/lyukypari.apk"
}

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("1xBet", callback_data="1xbet"),
            InlineKeyboardButton("WinWin", callback_data="winwin"),
            InlineKeyboardButton("Melbet", callback_data="melbet")
        ],
        [
            InlineKeyboardButton("Megapari", callback_data="megapari"),
            InlineKeyboardButton("DBBet", callback_data="dbbet"),
            InlineKeyboardButton("888Starz", callback_data="888starz")
        ],
        [
            InlineKeyboardButton("Lyukypari", callback_data="lyukypari")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    start_text = """
Assalomu alaykum! 🤝

Sport tikishlari bo'yicha eng sara bukmekerlik kompaniyalarini tanlang va g'alabalarga yo'l oching! 

🎯 Bizning bot orqali siz:
• Eng yangi va daromadli o'yinlarga ega bo'lasiz
• G'alaba qozonish uchun strategiyalar va aniq signallar olasiz
• Ishonchli bukmekerlik kompaniyalarini bitta platformada topasiz

Quyidagi shaffof tugmalardan kerakli bukmekerni tanlang va boshlang!
    """
    
    await update.message.reply_text(start_text, reply_markup=reply_markup)

# Tugmalar bosilganda
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    bukmeker = query.data
    bukmeker_names = {
        "1xbet": "1xBet",
        "winwin": "WinWin", 
        "melbet": "Melbet",
        "megapari": "Megapari",
        "dbbet": "DBBet",
        "888starz": "888Starz",
        "lyukypari": "Lyukypari"
    }
    
    apk_url = APK_FILES.get(bukmeker)
    bukmeker_name = bukmeker_names.get(bukmeker, bukmeker)
    
    if apk_url:
        response_text = f"""
Siz «{bukmeker_name}» ni tanladingiz! ✅

AIFUT platformasida ro'yxatdan o'ting va zafar qozoning! 🏆

APK fayl yuklanmoqda... ⬇️
        """
        
        await query.edit_message_text(response_text)
        
        # APK faylini yuborish
        try:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=apk_url,
                filename=f"{bukmeker_name}.apk",
                caption=f"📱 {bukmeker_name} ilovasi\n\nIlovani o'rnatib, hisob oching va g'alabani boshlang! 🎯"
            )
        except Exception as e:
            logging.error(f"APK yuborishda xatolik: {e}")
            await query.message.reply_text("❌ APK fayl yuklashda xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
    else:
        await query.edit_message_text("❌ Uzr, bu bukmeker uchun APK fayl hozircha mavjud emas.")

# Xatolik handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Xatolik yuz berdi: {context.error}")

def run_bot():
    """Botni ishga tushirish"""
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN topilmadi! Environment variable ni tekshiring.")
        return
    
    # Logging sozlash
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Bot application yaratish
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    # Botni ishga tushirish
    print("🤖 Bot Render da ishga tushdi...")
    application.run_polling()

if __name__ == "__main__":
    # Flask ni background da ishga tushiramiz
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Botni ishga tushiramiz
    run_bot()
