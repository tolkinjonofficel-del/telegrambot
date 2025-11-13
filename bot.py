import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Loggerni sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot tokeni - to'g'ridan-to'g'ri qo'ying (vaqtincha)
TOKEN = "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g"  # Bu yerga o'z tokeningizni qo'ying

# Token mavjudligini tekshirish
if TOKEN == "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g":
    print("❌ ILTIMOS: TOKEN ni o'zgartiring!")
    print("8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g")
    exit(1)

print(f"✅ Bot tokeni mavjud: {TOKEN[:10]}...")

# Bukmekerlar ma'lumotlari
bookmakers_data = {
    '1xbet': {
        'apk_link': 'https://1xbet.com/mobile/apk',
        'registration_link': 'https://1xbet.com/registration',
        'mavjud': True
    },
    'dbbet': {
        'apk_link': 'https://dbbet.com/mobile/apk', 
        'registration_link': 'https://dbbet.com/registration',
        'mavjud': True
    },
    'melbet': {
        'apk_link': 'https://melbet.com/mobile/apk',
        'registration_link': 'https://melbet.com/registration',
        'mavjud': True
    }
}

# Foydalanuvchi referallari
user_referrals = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start buyrug'i berilganda asosiy menyuni chiqarish"""
    welcome_text = """
🎯 *Apple of Fortune Botiga Xush Kelibsiz!*

🍎 Bu bot orqali siz:
• Ishonchli signal va strategiyalar olasiz
• Daromad olishni boshlashingiz mumkin
• Referal orqali qo'shimcha imkoniyatlarga ega bo'lasiz

Quyidagi tugmalardan birini tanlang:"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Daromad olishni boshlash", callback_data="daromad_boshlash")],
        [InlineKeyboardButton("📡 Signal olish", callback_data="signal_olish")],
        [InlineKeyboardButton("📚 Qo'llanma", callback_data="qollanma")],
        [InlineKeyboardButton("🎁 Bonus", callback_data="bonus")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tugma_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tugma bosilganda ishlovchi"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "daromad_boshlash":
        await bukmekerlar_royhati(query)
    
    elif query.data in ["1xbet", "dbbet", "melbet"]:
        await bukmeker_tafsilotlari(query, query.data)
    
    elif query.data == "signal_olish":
        await signal_variantlari(query, user_id)
    
    elif query.data == "signal_hozir":
        await signal_sozovi(query, user_id)
    
    elif query.data == "referal_yuborish":
        await referal_havola(query, user_id)
    
    elif query.data == "qollanma":
        await qollanma_yuborish(query)
    
    elif query.data == "bonus":
        await bonus_yuborish(query)
    
    elif query.data == "asosiy_menyu":
        await asosiy_menyuga_qaytish(query)

async def bukmekerlar_royhati(query):
    """Bukmekerlar ro'yxatini ko'rsatish"""
    text = "📊 Daromad olishni boshlash uchun bukmekerni tanlang:"
    
    keyboard = [
        [InlineKeyboardButton("1xBet", callback_data="1xbet")],
        [InlineKeyboardButton("DBBet", callback_data="dbbet")],
        [InlineKeyboardButton("MelBet", callback_data="melbet")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="asosiy_menyu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def bukmeker_tafsilotlari(query, bukmeker):
    """Tanlangan bukmeker uchun APK va ro'yxatdan o'tish havolalarini yuborish"""
    data = bookmakers_data.get(bukmeker)
    
    if not data:
        await query.edit_message_text("❌ Ma'lumot topilmadi.")
        return
    
    if not data['mavjud']:
        await query.edit_message_text("⏳ Uzur, hozircha fayllar ishlovda. Iltimos, keyinroq urinib ko'ring.")
        return
    
    bukmeker_nomlari = {
        '1xbet': '1xBet',
        'dbbet': 'DBBet', 
        'melbet': 'MelBet'
    }
    
    text = f"""
📱 *{bukmeker_nomlari[bukmeker]}*

⬇️ APK faylini yuklab olish:
{data['apk_link']}

📝 Ro'yxatdan o'tish:
{data['registration_link']}

💡 Eslatma: Ro'yxatdan o'tgach, daromad olishni boshlashingiz mumkin!"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="daromad_boshlash")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="asosiy_menyu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def signal_variantlari(query, user_id):
    """Signal variantlarini ko'rsatish"""
    referal_soni = user_referrals.get(user_id, 0)
    
    if referal_soni == 0:
        talab_qilinadigan = 1
        signal_mavjud = False
    elif referal_soni < 5:
        talab_qilinadigan = 5
        signal_mavjud = False
    elif referal_soni < 20:
        talab_qilinadigan = 20
        signal_mavjud = False
    else:
        talab_qilinadigan = 0
        signal_mavjud = True
    
    text = f"""
📡 *Ishonchli g'alaba qiling! Signalni hoziroq oling!*

Sizning referallaringiz: {referal_soni} ta"""
    
    keyboard = []
    
    if signal_mavjud:
        keyboard.append([InlineKeyboardButton("🚀 Signal NOW", callback_data="signal_hozir")])
    else:
        text += f"\n\n🔒 Signal olish uchun sizga {talab_qilinadigan - referal_soni} ta referal kerak!"
    
    keyboard.extend([
        [InlineKeyboardButton("📤 Referal yuborish", callback_data="referal_yuborish")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="asosiy_menyu")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def signal_sozovi(query, user_id):
    """Signal so'rovini qayta ishlash"""
    referal_soni = user_referrals.get(user_id, 0)
    
    if referal_soni >= 20:
        text = "🎯 Signal sahifasiga yo'naltirilmoqdasiz..."
        keyboard = [
            [InlineKeyboardButton("📡 Signal olish", url="https://www.signal7.digital")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="signal_olish")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await signal_variantlari(query, user_id)

async def referal_havola(query, user_id):
    """Foydalanuvchining referal havolasini yuborish"""
    bot_username = (await query.message._bot.get_me()).username
    referal_havola = f"https://t.me/{bot_username}?start=ref{user_id}"
    
    text = f"""
📤 *Referal havolangiz:*

`{referal_havola}`

👥 Do'stlaringizni taklif qiling va signal olish imkoniyatiga ega bo'ling!

📊 Sizning referallaringiz: {user_referrals.get(user_id, 0)} ta"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="signal_olish")],
        [InlineKeyboardButton("🏠 Bosh menyu", callback_data="asosiy_menyu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def qollanma_yuborish(query):
    """Foydalanuvchi qo'llanmasini yuborish"""
    text = """
📚 *Qo'llanma*

🎮 *Apple of Fortune o'yini qanday o'ynaladi:*
1. Bukmeker akkauntingizga kiring
2. Apple of Fortune o'yinini toping
3. Bizning signallarimiz asosida stavka qo'ying
4. G'alaba qozoning va daromad oling!

💡 *Maslahatlar:*
- Har doim risklarni boshqaring
- Kichik summadan boshlang
- Signallarni diqqat bilan kuzating"""
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="asosiy_menyu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def bonus_yuborish(query):
    """Bonus ma'lumotlarini yuborish"""
    text = """
🎁 *Bonuslar*

✨ *Ajoyib takliflar sizni kutmoqda:*

🏆 *Yangilangan bonuslar:*
- Yangi ro'yxatdan o'tganlar uchun +100% bonus
- Har bir do'stingiz uchun 50% bonus
- Haftalik cashback 10% gacha

📈 *Maxsus taklif:*
Har 5 ta muvaffaqiyatli signaldan keyin maxsus bonus!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="asosiy_menyu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def asosiy_menyuga_qaytish(query):
    """Asosiy menyuga qaytish"""
    welcome_text = """
🎯 *Apple of Fortune Botiga Xush Kelibsiz!*

🍎 Bu bot orqali siz:
• Ishonchli signal va strategiyalar olasiz
• Daromad olishni boshlashingiz mumkin
• Referal orqali qo'shimcha imkoniyatlarga ega bo'lasiz

Quyidagi tugmalardan birini tanlang:"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Daromad olishni boshlash", callback_data="daromad_boshlash")],
        [InlineKeyboardButton("📡 Signal olish", callback_data="signal_olish")],
        [InlineKeyboardButton("📚 Qo'llanma", callback_data="qollanma")],
        [InlineKeyboardButton("🎁 Bonus", callback_data="bonus")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        welcome_text, 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def referal_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Referal havolasi orqali kelgan foydalanuvchilarni qayta ishlash"""
    args = context.args
    if args and args[0].startswith('ref'):
        try:
            referal_bergan_id = int(args[0][3:])
            referal_olgan_id = update.message.from_user.id
            
            if referal_bergan_id in user_referrals:
                user_referrals[referal_bergan_id] += 1
            else:
                user_referrals[referal_bergan_id] = 1
            
            await update.message.reply_text(
                "✅ Siz do'stingiz orqali botga qo'shildingiz! "
                "Endi siz ham referal orqali signal olishingiz mumkin."
            )
        except ValueError:
            pass
    
    await start(update, context)

def main() -> None:
    """Botni ishga tushirish"""
    try:
        application = Application.builder().token(TOKEN).build()

        # Handlerlarni qo'shish
        application.add_handler(CommandHandler("start", referal_start))
        application.add_handler(CallbackQueryHandler(tugma_handler))

        print("🤖 Bot ishga tushmoqda...")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")
        print("Token noto'g'ri yoki mavjud emas")

if __name__ == '__main__':
    main()
