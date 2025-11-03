const TelegramBot = require("node-telegram-bot-api");
const fs = require("fs");

// Railway uchun token
const token = process.env.BOT_TOKEN || "8320792971:AAG6APrNu2wJgYSJreRPYkGjpt3o5JEeWYM";
const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategiya bot ishga tushdi...");


// === 1️⃣ /start komandasi ===
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;

  const message = `
✨ <b>Xush kelibsiz! O'yin strategiyalari botiga! ✨</b>

🎮 <b>Bot imkoniyatlari:</b>
• 🎯 Ishonchli platformalar  
• 💰 Samarali strategiyalar  
• 🚀 Tez daromad olish  
• 📊 Professional ko'rsatkichlar  

💎 Pul ko'paytirish uchun kerakli platformani tanlang:
`;

  const options = {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          { text: "💎 1xBet", callback_data: "1xbet" },
          { text: "🔥 Melbet", callback_data: "melbet" }
        ],
        [
          { text: "⚡ WinWin", callback_data: "winwin" },
          { text: "🏆 DBbet", callback_data: "dbbet" }
        ],
        [
          { text: "💰 MegaPari", callback_data: "megapari" },
          { text: "⭐ 888Starz", callback_data: "888starz" }
        ],
        [
          { text: "🎯 LuckyPati", callback_data: "luckypati" },
          { text: "👑 GoldPari", callback_data: "goldpari" }
        ]
      ]
    }
  };

  bot.sendMessage(chatId, message, options);
});


// === 2️⃣ Platforma tanlanganda ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const platform = query.data;

  const platformNames = {
    "1xbet": "1xBet",
    "melbet": "MelBet",
    "winwin": "WinWin",
    "dbbet": "DBbet",
    "megapari": "MegaPari",
    "888starz": "888Starz",
    "luckypati": "LuckyPati",
    "goldpari": "GoldPari"
  };

  const platformName = platformNames[platform];

  // Har bir platforma uchun rasm va APK fayl
  const imagePath = `./images/${platform}.jpg`;
  const apkPath = `./apks/${platform}.apk`;

  let caption = `
*🎰 ${platformName} platformasi tanlandi!* ✅

Royhatdan o'tish uchun:
📱 Android: APK faylni yuklab oling
📱 iPhone: Havola tez orada joylanadi  

Botni faollashtirish uchun <b>"AIFUT"</b> promokodini yozing va uni ro'yhatdan o'tishda kiriting! 👆✅
`;

  if (fs.existsSync(imagePath)) {
    await bot.sendPhoto(chatId, imagePath, { caption, parse_mode: "HTML" });
  } else {
    await bot.sendMessage(chatId, caption, { parse_mode: "HTML" });
  }

  if (fs.existsSync(apkPath)) {
    await bot.sendDocument(chatId, apkPath, {
      caption: `📱 ${platformName} uchun Android APK fayl`
    });
  } else {
    await bot.sendMessage(chatId, "⚠️ APK fayl hali joylanmagan.");
  }

  // O'yinlar tanlash
  await bot.sendMessage(chatId, `
💰 <b>Daromad olish uchun qaysi o'yinni o'ynashni tanlaysiz?</b>

📊 <b>${platformName} haqida:</b>
• 🎯 Ishonchlilik: 98%
• ⚡ Tezkorlik: A+
• 💰 Bonus: 150% gacha
• 📱 Qulaylik: Mobil optimallashtirilgan  

❗️ AIFUT promokodini ro'yhatdan o'tishda kiriting — shunda aniq signallar olasiz.
`, {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          { text: "🍏 Apple of Fortune", url: "https://t.me/AiFUTbot" },
          { text: "✈️ Aviator", url: "https://t.me/AiFUTbot" }
        ],
        [
          { text: "⚽ Penalty", url: "https://t.me/AiFUTbot" },
          { text: "🚀 JetX", url: "https://t.me/AiFUTbot" }
        ]
      ]
    }
  });
});
