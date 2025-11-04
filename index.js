const TelegramBot = require("node-telegram-bot-api");

// 🔑 TOKEN — o‘zingizning tokeningizni yozing yoki Railway’da Environment Variable sifatida kiriting
const token = process.env.BOT_TOKEN || "7454675594:AAFM2PQr8FX5KpbK_3k5z3kDYBtkFrBhJwo";

// 👑 ADMIN ID — sizning Telegram ID'ingiz (ixtiyoriy)
const ADMIN_CHAT_ID = 7081746531;

const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategik o'yinlar bot ishga tushdi...");

// === /start komandasi ===
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const user = msg.from;

  // 🔔 Yangi foydalanuvchi haqida admin uchun xabar (ixtiyoriy)
  const notifyAdmin = `
🧍‍♂️ <b>Yangi foydalanuvchi qo‘shildi!</b>
👤 Ism: ${user.first_name || "Noma’lum"}
🆔 ID: <code>${user.id}</code>
🌐 Username: ${user.username ? "@" + user.username : "—"}
`;
  bot.sendMessage(ADMIN_CHAT_ID, notifyAdmin, { parse_mode: "HTML" });

  // 💬 Start xabari
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
          { text: "🔥 Melbet", callback_data: "melbet" }
        ],
        [
          { text: "💰 Megapari", callback_data: "megapari" },
          { text: "🏆 DBbet", callback_data: "dbbet" }
        ],
        [
          { text: "⭐ 888Starz", callback_data: "888starz" }
        ]
      ]
    }
  };

  await bot.sendMessage(chatId, message, options);
});

// === Platforma tanlanganda ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  const platforms = {
    "1xbet": {
      name: "1Xbet",
      apk: "https://t.me/insayderAI/681",
      image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s"
    },
    "melbet": {
      name: "Melbet",
      apk: "https://t.me/insayderAI/687",
      image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s"
    },
    "megapari": {
      name: "Megapari",
      apk: "https://t.me/insayderAI/686",
      image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s"
    },
    "dbbet": {
      name: "DBbet",
      apk: "https://t.me/insayderAI/683",
      image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s"
    },
    "888starz": {
      name: "888Starz",
      apk: "https://t.me/insayderAI/682",
      image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s"
    }
  };

  const platform = platforms[data];
  if (!platform) return;

  const caption = `
🎯 <b>${platform.name}</b> platformasi tanlandi!  

💸 <b>Strategik game bilan doimo daromad qiling!</b>  
Ro‘yxatdan o‘tishda <b>AIFUT</b> promokodini kiriting va ro‘yxatdan o‘ting.  

💥 <b>To‘liq ro‘yxatdan o‘tgan foydalanuvchilar uchun — 200% BONUS!</b> 🎁
`;

  try {
    // 📸 Rasm + Xabar
    await bot.sendPhoto(chatId, platform.image, {
      caption,
      parse_mode: "HTML"
    });

    // 📦 APK fayl
    await bot.sendDocument(chatId, platform.apk, {
      caption: `📲 <b>${platform.name}</b> APK faylini yuklab oling va daromad olishni boshlang!`,
      parse_mode: "HTML"
    });

    // 🎮 O'yinlar menyusi
    await bot.sendMessage(
      chatId,
      `🎰 <b>Daromad olish uchun qaysi o‘yinni tanlaysiz?</b>`,
      {
        parse_mode: "HTML",
        reply_markup: {
          inline_keyboard: [
            [
              {
                text: "🍏 Apple of Fortune",
                url: "https://aplleoffortunesignal-bukmekeriotherss.netlify.app/"
              },
              {
                text: "✈️ Aviator",
                url: "https://aviatorxxxxxsignalll.netlify.app/"
              }
            ],
            [
              { text: "💥 Crash", callback_data: "crash" },
              { text: "⚽ Penalty", callback_data: "penalty" }
            ],
            [
              { text: "🐸 Swamp Lamp", callback_data: "swamp" }
            ]
          ]
        }
      }
    );
  } catch (error) {
    console.error("❌ Xato:", error);
    bot.sendMessage(chatId, "⚠️ Xatolik yuz berdi. Keyinroq urinib ko‘ring.");
  }
});

// === O'yin tanlanganda ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const game = query.data;

  if (game === "crash") {
    await bot.sendMessage(
      chatId,
      `⚠️ <b>Crash</b> — Aviatorning minilashgan versiyasi.  
🧠 Yangi o‘yinchilarga dastlab omad beradi, keyin ko‘p hollarda yo‘qotishga olib keladi.  
💡 Maslahat: bu o‘yinni kamroq o‘ynang.`,
      { parse_mode: "HTML" }
    );
  } else if (game === "penalty") {
    await bot.sendMessage(
      chatId,
      `⚽ <b>Penalty</b> — tez orada ushbu o‘yin uchun maxsus strategiya joylanadi.`,
      { parse_mode: "HTML" }
    );
  } else if (game === "swamp") {
    await bot.sendMessage(
      chatId,
      `🐸 <b>Swamp Lamp</b> — yangi “Apple of Fortune” o‘yinining modern versiyasi.  
🌿 Yangi bosqichlarda vizual effektlari yaxshilangan.  
🕹️ Tez orada bu o‘yinga ham signal beriladi.`,
      { parse_mode: "HTML" }
    );
  }
});by B 
