import os
import json
import logging
import random
import asyncio
import sys
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

# Environment variables dan token va admin ID ni olish
TOKEN = os.getenv("7871992128:AAF7RGJDLKPr34jUJFXuE7mpeZaMc6812ec", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable topilmadi!")
    print("⚠️  Iltimos, Render dashboard dan BOT_TOKEN qo'shing")
    sys.exit(1)

if not ADMIN_ID:
    print("⚠️  WARNING: ADMIN_ID topilmadi, default 0 ishlatiladi")

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout  # Render uchun stdout ga log yozish
)
logger = logging.getLogger(__name__)

# Qolgan kod o'zgarmaydi...
# (Yuqoridagi to'liq kodni shu yerga joylashtiring)
# Faqat tepadagi environment variables qismini o'zgartiring

async def main():
    """Asosiy funksiya"""
    try:
        print("=" * 50)
        print("🚀 FUTBOL KUPONLARI BOTI ISHGA TUSHMODA...")
        print("=" * 50)
        print(f"🤖 Admin ID: {ADMIN_ID}")
        
        # Application yaratish
        application = Application.builder().token(TOKEN).build()
        
        # Handlerlar
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Admin handler
        admin_filter = filters.User(ADMIN_ID) if ADMIN_ID else filters.User()
        application.add_handler(MessageHandler(
            filters.TEXT & admin_filter & ~filters.COMMAND, 
            handle_admin_message
        ))
        
        # Oddiy foydalanuvchi handler
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~admin_filter,
            handle_regular_message
        ))
        
        # Bot ma'lumotlarini olish
        bot = await application.bot.get_me()
        print(f"✅ Bot username: @{bot.username}")
        print(f"✅ Bot ismi: {bot.first_name}")
        print("=" * 50)
        print("✅ Bot ishlayapti. Yangi xabarlarni kutmoqda...")
        print("=" * 50)
        
        # Polling ni boshlash
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"Main da xato: {e}")
        print(f"❌ Xato: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
