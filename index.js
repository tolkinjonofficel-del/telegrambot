const TelegramBot = require("node-telegram-bot-api");

// 🔑 Bot tokeni
const token = "7454675594:AAFywGrnS-9Qo7zeLYOSdhKi1zxP04O1qhg";

// 👑 Admin ID
const ADMIN_CHAT_ID = 7081746531;

const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategik o'yinlar bot ishga tushdi...");

// APK fayllarning file_id lari
const apkFiles = {
  megapari: "AgAD4JEAAqqTSUg",
  starz: "AgADy5EAAqqTSUg"
};

// === /start komandasi ===
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const user = msg.from;

  // 🔔 Yangi foydalanuvchi haqida admin uchun xabar
  try {
    const notifyAdmin = `
🧍‍♂️ <b>Yangi foydalanuvchi qo'shildi!</b>
👤 Ism: ${user.first_name || "Noma'lum"}
🆔 ID: <code>${user.id}</code>
🌐 Username: ${user.username ? "@" + user.username : "—"}
`;
    await bot.sendMessage(ADMIN_CHAT_ID, notifyAdmin, { parse_mode: "HTML" });
  } catch (error) {
    console.log("Adminga xabar yuborishda xato:", error);
  }

  // 💬 Start xabari
  const message = `
🎮 <b>MegaPari va 888Starz strategik bot o'yinlari</b>

💰 <b>O'ynab daromad qilish ishonchli platformalar</b>
📝 Ro'yxatdan o'tib <b>200% bonus</b>ga ega bo'ling
🚀 O'yin o'ynab daromad qilishni boshlang!

👇 <b>Kerakli joyda o'yna - o'z tanlovingni qil:</b>
`;

  const options = {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          { 
            text: "🎯 MegaPari", 
            callback_data: "platform_megapari" 
          }
        ],
        [
          { 
            text: "⭐ 888Starz", 
            callback_data: "platform_888starz" 
          }
        ]
      ]
    }
  };

  await bot.sendMessage(chatId, message, options);
});

// === Barcha callback query'lar uchun handler ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  // Callback query ni javoblash
  await bot.answerCallbackQuery(query.id);

  try {
    // Platforma tanlangan bo'lsa
    if (data.startsWith("platform_")) {
      await handlePlatformSelection(chatId, data);
    }
    // O'yin tanlangan bo'lsa
    else if (data.startsWith("game_")) {
      await handleGameSelection(chatId, data);
    }
    // Asosiy menyuga qaytish
    else if (data === "main_menu") {
      await showMainMenu(chatId);
    }
  } catch (error) {
    console.error("❌ Callback queryda xato:", error);
    await bot.sendMessage(chatId, "⚠️ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.");
  }
});

// === Platforma tanlash ===
async function handlePlatformSelection(chatId, platformData) {
  const platforms = {
    "platform_megapari": {
      name: "MegaPari",
      fileId: apkFiles.megapari,
      fileName: "megapari.apk"
    },
    "platform_888starz": {
      name: "888Starz", 
      fileId: apkFiles.starz,
      fileName: "888starz.apk"
    }
  };

  const platform = platforms[platformData];
  if (!platform) return;

  // Platforma haqida ma'lumot
  const platformInfo = `
✅ <b>Siz ${platform.name} bukmekerini tanladingiz</b>

🎁 <b>AIFUT promokod orqali ro'yxatdan o'ting</b>
💎 <b>To'liq ro'yxatdan o'tish uchun 200% bonusni qo'lga kiriting!</b>

📲 Quyidagi APK faylni yuklab oling va daromad olishni boshlang!
`;

  await bot.sendMessage(chatId, platformInfo, { parse_mode: "HTML" });

  // APK faylni yuborish
  try {
    await bot.sendDocument(chatId, platform.fileId, {
      caption: `📲 <b>${platform.name} APK fayli</b>\n\n📍 Fayl nomi: ${platform.fileName}\n📦 Hajmi: ${platformData === "platform_megapari" ? "76.33 MB" : "68.22 MB"}\n\nYuklab oling va o'ynashni boshlang! 🚀`,
      parse_mode: "HTML"
    });

    // O'yinlar menyusini ko'rsatish
    await showGamesMenu(chatId);

  } catch (error) {
    console.error(`❌ ${platform.name} APK yuborishda xato:`, error);
    
    // Agar file_id ishlamasa, URL orqali yuborish
    const backupUrls = {
      "platform_megapari": "https://t.me/insayderAI/686",
      "platform_888starz": "https://t.me/insayderAI/682"
    };
    
    await bot.sendDocument(chatId, backupUrls[platformData], {
      caption: `📲 <b>${platform.name} APK fayli</b>\n\nZaxira usul bilan yuklab oling!`,
      parse_mode: "HTML"
    });
    
    await showGamesMenu(chatId);
  }
}

// === O'yinlar menyusi ===
async function showGamesMenu(chatId) {
  const message = `
🎯 <b>Daromad qilish uchun o'yinlarni tanlang:</b>

Quyidagi o'yinlardan birini tanlab, strategiya bilan yutib, daromad olishni boshlang!

✨ <b>Har bir o'yin uchun maxsus strategiyalar mavjud!</b>
`;

  await bot.sendMessage(chatId, message, {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          {
            text: "🍏 Apple of Fortune",
            url: "https://t.me/aifutbot"
          },
          {
            text: "✈️ Aviator", 
            url: "https://t.me/aifutbot"
          }
        ],
        [
          {
            text: "⚽ Penalty",
            url: "https://t.me/aifutbot"
          },
          {
            text: "🚀 JetX",
            url: "https://t.me/aifutbot"
          }
        ],
        [
          {
            text: "💎 Cristal",
            url: "https://t.me/aifutbot"
          }
        ],
        [
          {
            text: "🔙 Asosiy menyu",
            callback_data: "main_menu"
          }
        ]
      ]
    }
  });
}

// === O'yin tanlash ===
async function handleGameSelection(chatId, gameData) {
  const gameMessages = {
    "game_apple": `
🍏 <b>Apple of Fortune</b>

🎯 <b>Strategik o'yin - aqlli yuting!</b>

📊 <b>O'yin qoidalari:</b>
• Olma aylanasida to'g'ri joyni tanlang
• Har bir aylana yangi imkoniyat
• Bonus va multiplikatorlardan foydalaning

💡 <b>Maslahat:</b>
• Kichik summadan boshlang
• Strategiyani o'rganing
• Limitlaringizni belgilang
`,

    "game_aviator": `
✈️ <b>Aviator</b>

🚀 <b>Tez daromad olishning eng mashhur usuli!</b>

📈 <b>O'yin mexanikasi:</b>
• Samolyot uchadi va koeffitsient oshadi
• To'g'ri vaqtda chiqib o'ling
• Riskni boshqaring

⚠️ <b>Eslatma:</b>
• Har qachon ham samolyot "uchib ketishi" mumkin
• Sabrli bo'ling
• Emotsiyalarga berilmang
`,

    "game_penalty": `
⚽ <b>Penalty</b>

🎮 <b>Sport sevuvchilar uchun mukammal o'yin!</b>

🥅 <b>O'yin strategiyasi:</b>
• Darvozabon harakatlarini tahmin qiling
• Turli burchaklarni sinab ko'ring
• Zarbalaringizni diversifikatsiya qiling

🏆 <b>G'alaba kaliti:</b>
• Patternlarni kuzating
• Vaqtni to'g'ri boshqaring
• Sport bilimlaridan foydalaning
`,

    "game_jetx": `
🚀 <b>JetX</b>

💥 <b>Risk va mukofot o'yini!</b>

📊 <b>O'yin tamoyili:</b>
• Samolyot parvoz qiladi
• Koeffitsient oshib boradi
• Vaqtida chiqib o'ling

🎯 <b>Strategiya:</b>
• Kichik koeffitsientlarda chiqib o'ying
• Bankrot bo'lishdan qoching
• O'yin statistikasini o'rganing
`,

    "game_cristal": `
💎 <b>Cristal</b>

✨ <b>Yangi va qizigarli o'yin!</b>

🔮 <b>O'yin usuli:</b>
• Kristallar kombinatsiyasini taxmin qiling
• Turli darajadagi mukofotlar
• Strategik yondashuv muhim

💎 <b>Maxsus taktika:</b>
• Patternlarni o'rganing
• Kristallar ketma-ketligini tahlil qiling
• Turli stavka usullarini sinab ko'ring
`
  };

  const message = gameMessages[gameData] || `
🎮 <b>O'yin ma'lumotlari</b>

Tez orada ushbu o'yin uchun batafsil ma'lumotlar qo'shiladi.

📱 Hozircha telegram kanalimizda yangiliklarni kuzatib boring:
`;

  await bot.sendMessage(chatId, message, { 
    parse_mode: 'HTML',
    reply_markup: {
      inline_keyboard: [
        [
          {
            text: "📱 Telegram Kanalimiz",
            url: "https://t.me/aifutbot"
          }
        ],
        [
          {
            text: "🎮 Boshqa o'yinlar",
            callback_data: "platform_" + (gameData.includes("apple") ? "megapari" : "888starz")
          },
          {
            text: "🔙 Asosiy menyu", 
            callback_data: "main_menu"
          }
        ]
      ]
    }
  });
}

// === Asosiy menyuni ko'rsatish ===
async function showMainMenu(chatId) {
  const message = `
🎮 <b>MegaPari va 888Starz strategik bot o'yinlari</b>

💰 <b>O'ynab daromad qilish ishonchli platformalar</b>
📝 Ro'yxatdan o'tib <b>200% bonus</b>ga ega bo'ling
🚀 O'yin o'ynab daromad qilishni boshlang!

👇 <b>Platformani tanlang va boshlang:</b>
`;

  await bot.sendMessage(chatId, message, {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          { 
            text: "🎯 MegaPari", 
            callback_data: "platform_megapari" 
          }
        ],
        [
          { 
            text: "⭐ 888Starz", 
            callback_data: "platform_888starz" 
          }
        ]
      ]
    }
  });
}

// === Xatoliklar boshqaruvi ===
bot.on("polling_error", (error) => {
  console.error("❌ Polling error:", error);
});

process.on("uncaughtException", (error) => {
  console.error("❌ Uncaught Exception:", error);
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("❌ Unhandled Rejection at:", promise, "reason:", reason);
});

// === Bot ishga tushganligi haqida xabar ===
console.log("🤖 Bot muvaffaqiyatli ishga tushdi!");
console.log("📱 APK fayllar tayyor:");
console.log("   - MegaPari: megapari.apk (76.33 MB)");
console.log("   - 888Starz: 888starz.apk (68.22 MB)");
