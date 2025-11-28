import os
import json
import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta
import requests

# Bot tokeni
TOKEN = "8114630640:AAHqHzsEyL7s7yckyLXfOHltm8m8cYh4F2Q"
ADMIN_ID = 7081746531
DATA_FILE = "data.json"
API_URL = "http://localhost:5000/api"  # Flask API manzili

# ... (avvalgi import va sozlashlar o'zgarmaydi)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"Start command from user {user_id} ({user.first_name})")
        
        global data
        data = load_data()
        
        # Kunlik bonusni tekshirish
        await give_daily_bonus()
        
        # Yangi foydalanuvchi bo'lsa 30 ball berish
        is_new_user = False
        if str(user_id) not in data['users']:
            data['users'][str(user_id)] = {
                'name': user.first_name,
                'username': user.username,
                'referrals': 0,
                'referral_points': 0,
                'points': data['settings']['welcome_points'],
                'joined_date': datetime.now().strftime("%Y-%m-%d"),
                'last_active': datetime.now().timestamp(),
                'points_history': [{
                    'points': data['settings']['welcome_points'],
                    'reason': "Yangi foydalanuvchi bonus",
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'type': 'add'
                }]
            }
            data['stats']['total_users'] += 1
            data['stats']['total_points_given'] += data['settings']['welcome_points']
            save_data(data)
            is_new_user = True
            logger.info(f"Yangi foydalanuvchi qo'shildi: {user_id} - 30 ball berildi")
        else:
            data['users'][str(user_id)]['last_active'] = datetime.now().timestamp()
            save_data(data)
        
        # Referal tizimi - VEB INTEGRATSIYA
        if context.args:
            ref_id = context.args[0]
            logger.info(f"Referal argument: {ref_id}")
            if ref_id.startswith('ref'):
                try:
                    referrer_id = int(ref_id[3:])
                    
                    # API orqali referal qo'shish
                    response = requests.post(f"{API_URL}/user/{referrer_id}/add_referral")
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result['success']:
                            # Muvaffaqiyatli xabar
                            try:
                                await context.bot.send_message(
                                    chat_id=referrer_id,
                                    text=f"🎉 *Tabriklaymiz!*\n\n"
                                         f"📤 Sizning referal havolangiz orqali yangi foydalanuvchi qo'shildi!\n"
                                         f"👤 Yangi foydalanuvchi: {user.first_name}\n"
                                         f"💰 Sizga {result['points_added']} ball qo'shildi!\n"
                                         f"🎯 Jami ball: {result['new_points']}\n"
                                         f"👥 Jami referallar: {result['total_referrals']} ta",
                                    parse_mode='Markdown'
                                )
                            except Exception as e:
                                logger.error(f"Referal bildirishnoma yuborishda xato: {e}")
                except Exception as e:
                    logger.error(f"Referal qayd etishda xato: {e}")

        # API dan foydalanuvchi ma'lumotlarini olish
        user_response = requests.get(f"{API_URL}/user/{user_id}")
        if user_response.status_code == 200:
            user_data = user_response.json()['user']
        else:
            user_data = data['users'].get(str(user_id), {})

        welcome_text = f"""
🎉 *SALOM {user.first_name}!* 🏆

⚽ *FUTBOL BAHOLARI BOTIGA XUSH KELIBSIZ!*

💰 *BALL TIZIMI:*
• 🎁 *Yangi foydalanuvchi bonus:* 30 ball
• 📤 1 do'st taklif = *5 ball*
• 📅 *Kunlik bonus:* 10 ball
• 🎯 15 ball = *1 ta VIP kupon*

📊 *SIZNING HOLATINGIZ:*
👥 Referallar: {user_data.get('referrals', 0)} ta
💰 HISOBINGIZDA: {user_data.get('points', 0)} ball
💎 Referal ballar: {user_data.get('referral_points', 0)} ball
"""

        if is_new_user:
            welcome_text += f"\n🎁 *Sizga yangi foydalanuvchi bonus sifatida 30 ball berildi!*"

        welcome_text += f"\n\n🌐 *Veb sayt:* futbol-baholari.uz"
        welcome_text += f"\n🚀 *HOZIRROQ BOSHLANG!*\nBall to'plang va kuponlar oling! 🎯"

        keyboard = [
            [
                InlineKeyboardButton("🎯 VIP KUPONLAR", callback_data="get_coupons"),
                InlineKeyboardButton("🎁 BONUSLAR", callback_data="bonuses")
            ],
            [
                InlineKeyboardButton("📊 MENING BALLIM", callback_data="my_points"),
                InlineKeyboardButton("📤 REFERAL HAVOLA", callback_data="get_referral_link")
            ],
            [
                InlineKeyboardButton("🌐 VEB SAYT", url="http://futbol-baholari.uz"),
                InlineKeyboardButton("📱 STATISTIKA", callback_data="stats")
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

# Yangilangan veb interfeys HTML kodi
