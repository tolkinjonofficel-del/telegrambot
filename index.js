const TelegramBot = require("node-telegram-bot-api");

// 🧩 Bot tokeningiz (BotFather’dan olingan tokenni qo‘ying)
const token = process.env.BOT_TOKEN || "8320792971:AAG6APrNu2wJgYSJreRPYkGjpt3o5JEeWYM";
const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategik o'yinlar boti ishga tushdi...");

// === /start komandasi ===
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;

  const message = `
✨ <b>Xush kelibsiz! Strategik o'yinlar botiga!</b> ✨  

🎮 <b>Bot imkoniyatlari:</b>
• 🎯 Ishonchli o'yin platformalar  
• 💰 Sinovdan o'tgan strategiyalar  
• 🚀 Har kuni barqaror daromad  
• 📊 Professional yondashuv va foyda tahlili  

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


// === Platforma tanlanganda ===
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
  const imageUrl = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s";
  const apkUrl = "https://t.me/upaymeuz/3542";

  const caption = `
🎯 <b>${platformName}</b> o'yin platformasini tanladingiz!  

💸 <b>Strategik game bilan doimo daromad qiling!</b>  
Rasmda ko‘rsatilganday promokodni kiriting va ro‘yxatdan o‘ting.  

💥 To‘liq ro‘yxatdan o‘tgan foydalanuvchilar uchun — <b>200% bonus!</b> 🎁  

📲 Quyidagi havoladan <b>${platformName}</b> APK faylini yuklab oling:  
<a href="${apkUrl}">📦 ${platformName} APK faylini yuklab olish</a>
`;

  try {
    // Rasm bilan birga xabar yuborish
    await bot.sendPhoto(chatId, imageUrl, {
      caption,
      parse_mode: "HTML"
    });

    // Shu bilan birga APK fayl ham yuboriladi (rasm ostida)
    await bot.sendDocument(chatId, apkUrl, {
      caption: `📥 ${platformName} uchun APK fayl`,
      parse_mode: "HTML"
    });

    // Keyingi bosqich — o'yinlar ro'yxati
    await bot.sendMessage(chatId, `
🎰 <b>Daromad olish uchun o'yinni tanlang:</b>  
Har bir o'yin sizga strategiya asosida aniq natija va g‘alaba olib keladi 💪  
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
          ],
          [
            { text: "🐸 Swamp Lamp", url: "https://t.me/AiFUTbot" },
            { text: "🧞‍♂️ Aladin Chirogi", url: "https://t.me/AiFUTbot" }
          ],
          [
            { text: "💎 Cristal", url: "https://t.me/AiFUTbot" }
          ]
        ]
      }
    });
  } catch (error) {
    console.error("❌ Rasm yoki faylni yuborishda xato:", error);
    await bot.sendMessage(chatId, caption, { parse_mode: "HTML" });
  }
});
