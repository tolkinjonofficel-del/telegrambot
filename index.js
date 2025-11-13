const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();
const PORT = 3000;

// 🔐 TOKENLAR - O'ZINGIZGA TEGISHLI TOKENLARNI QO'YING
const TOKEN = "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g"; // @BotFather dan olingan token
const ADMIN_CHAT_ID = "7633561058"; // @userinfobot dan olingan ID

// Express server for Railway/Render
app.get('/', (req, res) => {
  res.json({ status: 'OK', message: 'Fortune Apple Bot is running!' });
});

app.listen(PORT, () => {
  console.log(`🚀 Server started on port ${PORT}`);
});

// Telegram Bot
if (!TOKEN || TOKEN === "8172087830:AAGe0W_fB-Xknd1wPsG8ElpBP6jL5XOmi-g") {
  console.log('❌ BOT_TOKEN ni o\'zgartiring! @BotFather dan token oling.');
  process.exit(1);
}

const bot = new TelegramBot(TOKEN, { polling: true });

console.log('🤖 Fortune Apple Bot ishga tushdi...');

// Bot info tekshirish
bot.getMe().then((botInfo) => {
  console.log(`✅ Bot ishga tushdi: @${botInfo.username}`);
  
  // Admin ga xabar yuborish
  if (ADMIN_CHAT_ID && ADMIN_CHAT_ID !== "678901234") {
    bot.sendMessage(ADMIN_CHAT_ID, '🤖 Bot ishga tushdi! Fortune Apple Bot faollashdi.');
  }
}).catch(err => {
  console.log('❌ Bot tokeni noto\'g\'ri! Token ni tekshiring.');
});

// User data storage
const userData = new Map();

// Start command
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  const firstName = msg.from.first_name;
  
  const welcomeText = `🍎 *Fortune Apple - Ishonchli Signal va Strategiya* 🍎\n\n*Xush kelibsiz, ${firstName}!* ✨\n\nBu bot orqali siz:\n✅ Ishonchli betting signallar\n✅ G'alaba strategiyalari\n✅ Bonus va imtiyozlar\n✅ Daromad olish imkoniyatiga ega bo'lasiz!\n\n*Quyidagi tugmalardan birini tanlang:*`;

  const keyboard = {
    reply_markup: {
      keyboard: [
        [{ text: "💰 Daromad olishni boshlash" }],
        [{ text: "📡 Signal olish" }],
        [{ text: "📚 Qo'llanma" }, { text: "🎁 Bonus" }],
        [{ text: "👥 Referal yuborish" }]
      ],
      resize_keyboard: true,
      one_time_keyboard: false
    }
  };

  bot.sendMessage(chatId, welcomeText, { 
    parse_mode: 'Markdown',
    ...keyboard
  });
});

// Daromad olishni boshlash
bot.onText(/💰 Daromad olishni boshlash/, (msg) => {
  const chatId = msg.chat.id;
  
  const text = `🎯 *Daromad olishni boshlash uchun bukmekerni tanlang:*\n\nHar bir bukmeker uchun siz:\n📱 APK fayl\n🔗 Ro'yxatdan o'tish havolasi\n🎁 Maxsus bonus olasiz!`;

  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        [{ text: "1xBet 📱", callback_data: "bukmeker_1xbet" }],
        [{ text: "DBBet 🎯", callback_data: "bukmeker_dbbet" }],
        [{ text: "MelBet ⚡", callback_data: "bukmeker_melbet" }],
        [{ text: "🔙 Orqaga", callback_data: "back_to_main" }]
      ]
    }
  };

  bot.sendMessage(chatId, text, { 
    parse_mode: 'Markdown',
    ...keyboard
  });
});

// Signal olish
bot.onText(/📡 Signal olish/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  const user = userData.get(userId) || { referrals: 0 };
  const requiredReferrals = getRequiredReferrals(user.referrals);

  const text = `🎯 *Ishonchli g'alaba qiling! Signalni hozir oling!*\n\n📊 Sizning statistikangiz:\n👥 Referallar: ${user.referrals}/${requiredReferrals}\n\n${
    user.referrals >= requiredReferrals 
      ? "✅ Signal olish uchun tayyorsiz!"
      : `❌ Signal olish uchun ${requiredReferrals - user.referrals} ta referal kerak!`
  }`;

  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        user.referrals >= requiredReferrals 
          ? [{ text: "🚀 SIGNAL NOW", url: "https://www.signal7.digital" }]
          : [{ text: `📊 ${requiredReferrals - user.referrals} ta referal kerak`, callback_data: "need_referrals" }],
        [{ text: "👥 Referal yuborish", callback_data: "share_referral" }],
        [{ text: "🔙 Orqaga", callback_data: "back_to_main" }]
      ]
    }
  };

  bot.sendMessage(chatId, text, { 
    parse_mode: 'Markdown',
    ...keyboard
  });
});

// Qo'llanma
bot.onText(/📚 Qo'llanma/, (msg) => {
  const chatId = msg.chat.id;
  
  const text = `📖 *Fortune Apple Bot Qo'llanmasi*\n\n1. *Daromad olish* - Bukmeker tanlang va ro'yxatdan o'ting\n2. *Signal olish* - Referallar to'plang va signallarni oling\n3. *Bonus* - Bonuslardan foydalaning\n\n*Qoidalar:*\n- Har bir yangi foydalanuvchi 1 ta signal olish imkoniyati\n- Keyingi signal uchun 5 ta referal\n- Undan keyin 20 ta referal`;

  bot.sendMessage(chatId, text, { parse_mode: 'Markdown' });
});

// Bonus
bot.onText(/🎁 Bonus/, (msg) => {
  const chatId = msg.chat.id;
  
  const text = `🎁 *Maxsus Bonuslar*\n\n✨ *Yangilar uchun:*\n- 1xBet: 100% deposit bonus\n- DBBet: 50% birinchi bonus\n- MelBet: 200% welcome bonus\n\n🎯 *Faol foydalanuvchilar:*\n- Har 10 ta referal uchun maxsus bonus\n- Haftalik sovrinlar\n- Exclusive signallar`;

  bot.sendMessage(chatId, text, { parse_mode: 'Markdown' });
});

// Referal yuborish
bot.onText(/👥 Referal yuborish/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  const referralLink = `https://t.me/${(await bot.getMe()).username}?start=ref_${userId}`;
  
  const text = `👥 *Referal Do'stlaringizni Taklif Qiling!*\n\n🔗 Sizning referal havolangiz:\n\`${referralLink}\`\n\n📊 *Taklif qilish uchun:*\n1. Havolani do'stlaringizga yuboring\n2. Har bir ro'yxatdan o'tgan do'stingiz sizga 1 ball beradi\n3. Ballar to'plab signallar oling!\n\n🎁 *Bonus:* Har 5 ta referal uchun maxsus bonus!`;

  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        [{ text: "📤 Havolani ulashish", url: `https://t.me/share/url?url=${encodeURIComponent(referralLink)}&text=Fortune Apple Bot - Ishonchli signallar!` }],
        [{ text: "🔙 Orqaga", callback_data: "back_to_main" }]
      ]
    }
  };

  bot.sendMessage(chatId, text, { 
    parse_mode: 'Markdown',
    ...keyboard
  });
});

// Callback query handler
bot.on('callback_query', (callbackQuery) => {
  const msg = callbackQuery.message;
  const chatId = msg.chat.id;
  const data = callbackQuery.data;

  if (data.startsWith('bukmeker_')) {
    handleBukmekerSelection(chatId, data);
  } else if (data === 'back_to_main') {
    bot.sendMessage(chatId, "🏠 Asosiy menyu:", {
      reply_markup: {
        keyboard: [
          [{ text: "💰 Daromad olishni boshlash" }],
          [{ text: "📡 Signal olish" }],
          [{ text: "📚 Qo'llanma" }, { text: "🎁 Bonus" }],
          [{ text: "👥 Referal yuborish" }]
        ],
        resize_keyboard: true
      }
    });
  } else if (data === 'share_referral') {
    const userId = callbackQuery.from.id;
    bot.getMe().then((botInfo) => {
      const referralLink = `https://t.me/${botInfo.username}?start=ref_${userId}`;
      bot.sendMessage(chatId, `🔗 Referal havolangiz:\n\`${referralLink}\``, {
        parse_mode: 'Markdown'
      });
    });
  }

  bot.answerCallbackQuery(callbackQuery.id);
});

// Bukmeker selection handler
function handleBukmekerSelection(chatId, bukmekerType) {
  const bukmekers = {
    'bukmeker_1xbet': {
      name: '1xBet',
      apk: 'https://1xbet.com/app.apk',
      register: 'https://1xbet.com/register',
      bonus: '100% deposit bonus'
    },
    'bukmeker_dbbet': {
      name: 'DBBet', 
      apk: 'https://dbbet.com/app.apk',
      register: 'https://dbbet.com/register',
      bonus: '50% first deposit bonus'
    },
    'bukmeker_melbet': {
      name: 'MelBet',
      apk: 'https://melbet.com/app.apk',
      register: 'https://melbet.com/register',
      bonus: '200% welcome bonus'
    }
  };

  const bukmeker = bukmekers[bukmekerType];
  
  const text = `🎯 *${bukmeker.name}* - Bukmeker\n\n📱 *APK Yuklab Olish:*\n${bukmeker.apk}\n\n🔗 *Ro'yxatdan O'tish:*\n${bukmeker.register}\n\n🎁 *Bonus:* ${bukmeker.bonus}\n\n⚠️ *Admin ga yuborildi! Tez orada siz bilan bog'lanamiz!*`;

  // Admin ga xabar yuborish
  if (ADMIN_CHAT_ID && ADMIN_CHAT_ID !== "7633561058") {
    bot.sendMessage(ADMIN_CHAT_ID, `📥 Yangi bukmeker so'rovi:\n\n👤 User ID: ${chatId}\n🏢 Bukmeker: ${bukmeker.name}\n📱 APK: ${bukmeker.apk}\n🔗 Register: ${bukmeker.register}`);
  }

  bot.sendMessage(chatId, text, { parse_mode: 'Markdown' });
}

// Referal requirement calculator
function getRequiredReferrals(currentReferrals) {
  if (currentReferrals === 0) return 1;    // Birinchi marta 1 ta
  if (currentReferrals === 1) return 5;    // Keyin 5 ta
  return 20;                               // Undan keyin 20 ta
}

// Referal tracking
bot.onText(/\/start ref_(\d+)/, (msg, match) => {
  const chatId = msg.chat.id;
  const referrerId = match[1];
  const newUserId = msg.from.id;

  if (referrerId !== newUserId.toString()) {
    let referrer = userData.get(parseInt(referrerId)) || { referrals: 0 };
    referrer.referrals += 1;
    userData.set(parseInt(referrerId), referrer);

    // Referrer ga xabar
    bot.sendMessage(referrerId, `🎉 Tabriklaymiz! Yangi referal qo'shildi!\n\n📊 Jami referallar: ${referrer.referrals}`);
  }

  // Start xabarini yuborish
  bot.sendMessage(chatId, `🍎 *Fortune Apple Bot* ga xush kelibsiz!\n\nSizni taklif qilgan foydalanuvchi uchun rahmat! 🎁`, {
    parse_mode: 'Markdown',
    reply_markup: {
      keyboard: [
        [{ text: "💰 Daromad olishni boshlash" }],
        [{ text: "📡 Signal olish" }],
        [{ text: "📚 Qo'llanma" }, { text: "🎁 Bonus" }]
      ],
      resize_keyboard: true
    }
  });
});

console.log('✅ Bot kodlari tayyor! Token va ID lar kod ichida.');
