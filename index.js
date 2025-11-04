const TelegramBot = require("node-telegram-bot-api");

// 🔑 TOKEN
const token = process.env.BOT_TOKEN || "7454675594:AAEP9585-lWBDOKg1Z1-g6w6OSGTRV4FY_0";

// 👑 ADMIN ID
const ADMIN_CHAT_ID = 7081746531;

const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategik o'yinlar bot ishga tushdi...");

// === /start komandasi ===
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const user = msg.from;

  // Adminga xabar yuborish
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

  // Start xabari
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

// === Callback query handler ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  // Callback query ni javoblash
  await bot.answerCallbackQuery(query.id);

  // Platforma tanlangan bo'lsa
  if (data.startsWith("platform_")) {
    await handlePlatformSelection(chatId, data);
  }
  // O'yin tanlangan bo'lsa
  else if (data.startsWith("game_")) {
    await handleGameSelection(chatId, data);
  }
});

// === Platforma tanlash ===
async function handlePlatformSelection(chatId, platformData) {
  const platforms = {
    "platform_megapari": {
      name: "MegaPari",
      apk: "https://t.me/insayderAI/686",
      image: "https://img.freepik.com/free-vector/gradient-abstract-purple-background_23-2149120770.jpg"
    },
    "platform_888starz": {
      name: "888Starz",
      apk: "https://t.me/insayderAI/682", 
      image: "https://img.freepik.com/free-vector/gradient-blue-abstract-background_23-2149120775.jpg"
    }
  };

  const platform = platforms[platformData];
  if (!platform) return;

  const caption = `
✅ <b>Siz ${platform.name} bukmekerini tanladingiz</b>

🎁 <b>AIFUT promokod orqali ro'yxatdan o'ting</b>
💎 <b>To'liq ro'yxatdan o'tish uchun 200% bonusni qo'lga kiriting!</b>

📲 Pastdagi APK faylni yuklab oling va daromad olishni boshlang!
`;

  try {
    // Rasm yuborish
    await bot.sendPhoto(chatId, platform.image, {
      caption,
      parse_mode: "HTML"
    });

    // APK fayl yuborish
    await bot.sendDocument(chatId, platform.apk, {
      caption: `📲 <b>${platform.name} APK fayli</b>\nYuklab oling va o'ynashni boshlang!`,
      parse_mode: "HTML"
    });

    // O'yinlar menyusini ko'rsatish
    await showGamesMenu(chatId);

  } catch (error) {
    console.error("❌ Xato:", error);
    await bot.sendMessage(chatId, "⚠️ Xatolik yuz berdi. Keyinroq urinib ko'ring.");
  }
}

// === O'yinlar menyusi ===
async function showGamesMenu(chatId) {
  const message = `
🎯 <b>Daromad qilish uchun o'yinlarni tanlang:</b>

Quyidagi o'yinlardan birini tanlab, daromad olishni boshlang!
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

🎯 Bu o'yinda strategiya bilan yuting!
💰 Daromad qilish uchun telegram kanalimizda strategiyalarni kuzatib boring.

📊 <b>O'yin qoidalari:</b>
• Olma aylanasida g'olib bo'ling
• Strategik harakatlar bilan yuting
• Bonuslardan foydalaning
`,

    "game_aviator": `
✈️ <b>Aviator</b>

🚀 Eng mashhur va tez daromad olish o'yinlaridan biri!
📊 To'g'ri vaqtda chiqishni o'rganing.

📈 <b>Maslahat:</b>
• Koeffitsient oshgan sari risk oshadi
• Vaqtida chiqib o'ling
• Kichik summadan boshlang
`,

    "game_penalty": `
⚽ <b>Penalty</b>

🎮 Sport o'yinlari sevuvchilar uchun!
🥅 Penaltilar seriyasida g'alaba qozoning.

🏆 <b>Strategiya:</b>
• Darvozabon harakatlarini kuzating
• Turli burchaklarni sinab ko'ring
• Zarbalaringizni diversifikatsiya qiling
`,

    "game_jetx": `
🚀 <b>JetX</b>

💥 Risk va mukofot o'yini!
📈 Samolyot uchishidan oldin chiqib o'ling.

⚠️ <b>Eslatma:</b>
• Samolyot har qachon ham parvoz qilishi mumkin
• Koeffitsient oshgan sari risk oshadi
• O'z limitlaringizni belgilang
`,

    "game_cristal": `
💎 <b>Cristal</b>

✨ Yangi va qizigarli o'yin!
🔮 Kristallarni bashorat qiling va yuting.

🎲 <b>Qoidalar:</b>
• Kristallar kombinatsiyasini taxmin qiling
• Turli darajadagi mukofotlar
• Strategik yondashuv muhim
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
            text: "🔙 Asosiy menyu",
            callback_data: "main_menu"
          }
        ]
      ]
    }
  });
}

// === Asosiy menyuga qaytish ===
bot.on("callback_query", async (query) => {
  if (query.data === "main_menu") {
    const chatId = query.message.chat.id;
    
    // Asosiy menyuni qayta yuborish
    const message = `
🎮 <b>MegaPari va 888Starz strategik bot o'yinlari</b>

💰 <b>O'ynab daromad qilish ishonchli platformalar</b>
📝 Ro'yxatdan o'tib <b>200% bonus</b>ga ega bo'ling

👇 <b>Platformani tanlang:</b>
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
});

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

// Token tekshiruvi
if (!process.env.BOT_TOKEN && token === "BU_YERGA_TOKEN_YOZILADI") {
  console.error("❌ BOT_TOKEN environment variable o'rnatilmagan!");
  process.exit(1);
}
