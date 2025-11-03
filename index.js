const TelegramBot = require("node-telegram-bot-api");

// 🔑 BOT TOKEN — o'zingizning tokenni qo'ying yoki Railway orqali kiriting
const token = process.env.BOT_TOKEN || "8320792971:AAG6APrNu2wJgYSJreRPYkGjpt3o5JEeWYM";
const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategiya bot ishga tushdi...");


// === /start komandasi ===
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;

  const message = `
✨ <b>Xush kelibsiz! O'yin strategiyalari botiga!</b> ✨

🎮 <b>Bot imkoniyatlari:</b>
• 🎯 Ishonchli platformalar  
• 💰 Samarali strategiyalar  
• 🚀 Tez daromad olish  
• 📊 Professional ko'rsatkichlar  

💎 <b>Pul ko'paytirish uchun kerakli platformani tanlang:</b>
`;

  const options = {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          { text: "💎 1Xbet", callback_data: "1xbet" },
          { text: "🏆 DBbet", callback_data: "dbbet" }
        ],
        [
          { text: "🔥 Melbet", callback_data: "melbet" },
          { text: "⚡ Winwin", callback_data: "winwin" }
        ],
        [
          { text: "⭐ 888Starz", callback_data: "888starz" },
          { text: "💰 Megapari", callback_data: "megapari" }
        ],
        [
          { text: "🎯 Lyukypari", callback_data: "lyukypari" },
          { text: "👑 Goldpari", callback_data: "goldpari" }
        ]
      ]
    }
  };

  bot.sendMessage(chatId, message, options);
});


// === Callback (platforma tanlanganda) ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  const platformNames = {
    "1xbet": "1Xbet",
    "dbbet": "DBbet",
    "melbet": "Melbet",
    "winwin": "Winwin",
    "888starz": "888Starz",
    "megapari": "Megapari",
    "lyukypari": "Lyukypari",
    "goldpari": "Goldpari"
  };

  const platformName = platformNames[data];
  const imageUrl = "blob:https://web.telegram.org/e8083033-ed72-4096-b3d6-b29a7e393f74";
  const apkUrl = "https://t.me/upaymeuz/3542";

  const caption = `
🎯 <b>${platformName}</b> o'yin platformasini tanladingiz!

💸 <b>Strategik game bilan doimo daromad qiling!</b>

📲 Rasmda ko‘rsatilganday promokodni yozing va ro‘yxatdan o‘ting.  
✅ To‘liq ro‘yxatdan o‘tib 200% bonusga ega bo‘ling!

⬇️ <b>${platformName}</b> APK faylini yuklab oling yoki ushbu havola orqali ro‘yxatdan o‘ting:
👉 <a href="${apkUrl}">${apkUrl}</a>
`;

  try {
    await bot.sendPhoto(chatId, imageUrl, {
      caption,
      parse_mode: "HTML"
    });
  } catch (error) {
    console.error("❌ Rasmni yuborishda xato:", error);
    await bot.sendMessage(chatId, caption, { parse_mode: "HTML" });
  }
});
