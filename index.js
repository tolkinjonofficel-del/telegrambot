const TelegramBot = require("node-telegram-bot-api");

// 🔑 Bot token (BotFather’dan)
const token = process.env.BOT_TOKEN || "7454675594:AAFM2PQr8FX5KpbK_3k5z3kDYBtkFrBhJwo";
// 👑 Admin ID (sizning Telegram ID'ingiz)
const ADMIN_CHAT_ID = 7081746531;

const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategik bot ishga tushdi...");

// === START komandasi ===
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  const user = msg.from;

  // 🔔 Admin uchun bildirish
  const notifyAdmin = `
🧍‍♂️ <b>Yangi foydalanuvchi qo‘shildi!</b>
👤 Ism: ${user.first_name || "Noma’lum"}
🆔 ID: <code>${user.id}</code>
🌐 Username: ${user.username ? "@" + user.username : "—"}
📱 Til: ${user.language_code ? user.language_code.toUpperCase() : "—"}
`;
  bot.sendMessage(ADMIN_CHAT_ID, notifyAdmin, { parse_mode: "HTML" });

  // 💬 Foydalanuvchiga start xabari
  const startMessage = `
✨ <b>Xush kelibsiz! Strategik o'yinlar botiga!</b> ✨  

🎮 <b>Bot imkoniyatlari:</b>
• 🎯 Ishonchli platformalar  
• 💰 Samarali strategiyalar  
• 🚀 Har kuni daromad  
• 📊 Professional tahlil  

💎 <b>Pul ko‘paytirish uchun kerakli platformani tanlang:</b>
`;

  const buttons = {
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
    },
    parse_mode: "HTML"
  };

  bot.sendMessage(chatId, startMessage, buttons);
});

// === PLATFORMANI TANLAGANDA ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  const platforms = {
    "1xbet": { name: "1Xbet", apk: "https://t.me/insayderAI/681" },
    "dbbet": { name: "DBbet", apk: "https://t.me/insayderAI/683" },
    "melbet": { name: "Melbet", apk: "https://t.me/insayderAI/687" },
    "winwin": { name: "Winwin", apk: "https://t.me/insayderAI/688" },
    "888starz": { name: "888Starz", apk: "https://t.me/insayderAI/682" },
    "megapari": { name: "Megapari", apk: "https://t.me/insayderAI/686" },
    "lyukypari": { name: "Lyukypari", apk: "https://t.me/insayderAI/685" },
    "goldpari": { name: "Goldpari", apk: "https://t.me/insayderAI/684" }
  };

  const imageUrl =
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s";

  const platform = platforms[data];
  if (!platform) return;

  const caption = `
🎯 <b>${platform.name}</b> platformasi tanlandi!  

💸 <b>Strategik game bilan doimo daromad qiling!</b>  
Rasmda ko‘rsatilganday <b>AIFUT</b> promokodini kiriting va ro‘yxatdan o‘ting.  

💥 To‘liq ro‘yxatdan o‘tgan foydalanuvchilar uchun — <b>200% BONUS!</b> 🎁  
`;

  try {
    // 📸 Rasm
    await bot.sendPhoto(chatId, imageUrl, {
      caption,
      parse_mode: "HTML"
    });

    // 📦 APK fayl — Telegram fayl sifatida ko‘rinadi
    await bot.sendDocument(chatId, platform.apk, {
      caption: `📥 <b>${platform.name}</b> APK faylini yuklab oling va o‘rnatib ro‘yxatdan o‘ting.`,
      parse_mode: "HTML"
    });

    // 🎰 O‘yinlar menyusi
    await bot.sendMessage(
      chatId,
      `
🎰 <b>Daromad olish uchun o'yinni tanlang:</b>  
Har bir o'yin — strategik yondashuv bilan g‘alabaga olib keladi 💪  
`,
      {
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
            [{ text: "💎 Cristal", url: "https://t.me/AiFUTbot" }]
          ]
        }
      }
    );
  } catch (error) {
    console.error("❌ Xato:", error);
    bot.sendMessage(chatId, "⚠️ Xatolik yuz berdi, keyinroq urinib ko‘ring.");
  }
});
