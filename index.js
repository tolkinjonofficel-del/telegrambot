const TelegramBot = require("node-telegram-bot-api");

// 🔑 BOT TOKEN
const token = process.env.BOT_TOKEN || "8320792971:AAG6APrNu2wJgYSJreRPYkGjpt3o5JEeWYM";
// 👑 ADMIN CHAT ID — o'zingizning Telegram ID'ingizni yozing
const ADMIN_CHAT_ID = 7081746531;

const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategik o'yinlar boti ishga tushdi...");


// === /start komandasi ===
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  const user = msg.from;

  // --- 🔔 Admin uchun xabar ---
  const notifyAdmin = `
🧍‍♂️ <b>Yangi foydalanuvchi qo‘shildi!</b>

👤 <b>Ism:</b> ${user.first_name || "Noma’lum"}
🆔 <b>ID:</b> <code>${user.id}</code>
🌐 <b>Username:</b> ${user.username ? "@" + user.username : "—"}
📱 <b>Til:</b> ${user.language_code ? user.language_code.toUpperCase() : "—"}
`;
  bot.sendMessage(ADMIN_CHAT_ID, notifyAdmin, { parse_mode: "HTML" });

  // --- 🎮 Foydalanuvchi uchun start xabari ---
  const message = `
✨ <b>Xush kelibsiz! Strategik o'yinlar botiga!</b> ✨  

🎮 <b>Bot imkoniyatlari:</b>
• 🎯 Ishonchli platformalar  
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

  const apkLinks = {
    "1xbet": "https://t.me/insayderAI/681",
    "winwin": "https://t.me/insayderAI/688",
    "goldpari": "https://t.me/insayderAI/684",
    "lyukypari": "https://t.me/insayderAI/685",
    "melbet": "https://t.me/insayderAI/687",
    "megapari": "https://t.me/insayderAI/686",
    "888starz": "https://t.me/insayderAI/682",
    "dbbet": "https://t.me/insayderAI/683"
  };

  const platformName = platformNames[data];
  const apkUrl = apkLinks[data];
  const imageUrl = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s";

  const caption = `
🎯 <b>${platformName}</b> o'yin platformasini tanladingiz!  

💸 <b>Strategik game bilan doimo daromad qiling!</b>  
Rasmda ko‘rsatilganday <b>AIFUT</b> promokodini kiriting va ro‘yxatdan o‘ting.  

💥 To‘liq ro‘yxatdan o‘tgan foydalanuvchilar uchun — <b>200% BONUS!</b> 🎁  

📲 Quyidagi havoladan <b>${platformName}</b> APK faylini yuklab oling:
<a href="${apkUrl}">📦 ${platformName} APK faylini yuklab olish</a>
`;

  try {
    // 📸 Rasm bilan xabar
    await bot.sendPhoto(chatId, imageUrl, {
      caption,
      parse_mode: "HTML"
    });

    // 📦 Fayl havolasi (fayl sifatida ko‘rinadi)
    await bot.sendDocument(chatId, apkUrl, {
      caption: `📥 ${platformName} uchun APK fayl`,
      parse_mode: "HTML"
    });

    // 🎮 O'yinlar ro'yxati
    await bot.sendMessage(chatId, `
🎰 <b>Daromad olish uchun o'yinni tanlang:</b>  
Har bir o'yin — strategiya asosida aniq natija va foyda olib keladi 💪  
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
    console.error("❌ Xato:", error);
    await bot.sendMessage(chatId, caption, { parse_mode: "HTML" });
  }
});
