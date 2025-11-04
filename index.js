const TelegramBot = require("node-telegram-bot-api");

// 🔑 TOKEN — o'zingizning tokeningizni yozing yoki Railway'da Environment Variable sifatida kiriting
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
🧍‍♂️ <b>Yangi foydalanuvchi qo'shildi!</b>
👤 Ism: ${user.first_name || "Noma'lum"}
🆔 ID: <code>${user.id}</code>
🌐 Username: ${user.username ? "@" + user.username : "—"}
`;
  try {
    await bot.sendMessage(ADMIN_CHAT_ID, notifyAdmin, { parse_mode: "HTML" });
  } catch (error) {
    console.log("Adminga xabar yuborishda xato:", error);
  }

  // 💬 Yangi start xabari
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
            callback_data: "megapari" 
          }
        ],
        [
          { 
            text: "⭐ 888Starz", 
            callback_data: "888starz" 
          }
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
    "megapari": {
      name: "MegaPari",
      apk: "https://t.me/insayderAI/686",
      image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s"
    },
    "888starz": {
      name: "888Starz",
      apk: "https://t.me/insayderAI/682",
      image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s"
    }
  };

  const platform = platforms[data];
  if (!platform) {
    // Agar platforma emas, balki o'yin tanlangan bo'lsa
    await handleGameSelection(chatId, data);
    return;
  }

  const caption = `
✅ <b>Siz ${platform.name} bukmekerini tanladingiz</b>

🎁 <b>AIFUT promokod orqali ro'yxatdan o'ting</b>
💎 <b>To'liq ro'yxatdan o'tish uchun 200% bonusni qo'lga kiriting!</b>

📲 Pastdagi APK faylni yuklab oling va daromad olishni boshlang!
`;

  try {
    // 📸 Rasm + Xabar
    await bot.sendPhoto(chatId, platform.image, {
      caption,
      parse_mode: "HTML"
    });

    // 📦 APK fayl
    await bot.sendDocument(chatId, platform.apk, {
      caption: `📲 <b>${platform.name}</b> APK faylini yuklab oling va boshlang!`,
      parse_mode: "HTML"
    });

    // 🎮 O'yinlar menyusi
    await bot.sendMessage(
      chatId,
      `🎯 <b>Daromad qilish uchun o'yinlarni tanlang:</b>`,
      {
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
      }
    );
  } catch (error) {
    console.error("❌ Xato:", error);
    await bot.sendMessage(chatId, "⚠️ Xatolik yuz berdi. Keyinroq urinib ko'ring.");
  }
});

// === O'yin tanlanganda (agar callback_data orqali o'yin tanlansa) ===
async function handleGameSelection(chatId, game) {
  const gameMessages = {
    "apple": `
🍏 <b>Apple of Fortune</b>
🎯 Bu o'yinda strategiya bilan yuting!
💰 Daromad qilish uchun telegram kanalimizda strategiyalarni kuzatib boring.
    `,
    "aviator": `
✈️ <b>Aviator</b>
🚀 Eng mashhur va tez daromad olish o'yinlaridan biri!
📊 To'g'ri vaqtda chiqishni o'rganing.
    `,
    "penalty": `
⚽ <b>Penalty</b>
🎮 Sport o'yinlari sevuvchilar uchun!
🥅 Penaltilar seriyasida g'alaba qozoning.
    `,
    "jetx": `
🚀 <b>JetX</b>
💥 Risk va mukofot o'yini!
📈 Samolyot uchishidan oldin chiqib o'ling.
    `,
    "cristal": `
💎 <b>Cristal</b>
✨ Yangi va qizigarli o'yin!
🔮 Kristallarni bashorat qiling va yuting.
    `
  };

  const message = gameMessages[game] || "🎮 <b>Bu o'yin uchun strategiya tez orada qo'shiladi!</b>";
  await bot.sendMessage(chatId, message, { 
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          {
            text: "📱 Telegram Kanalimiz",
            url: "https://t.me/aifutbot"
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

// === Token mavjudligini tekshirish ===
if (!process.env.BOT_TOKEN && token === "BU_YERGA_TOKEN_YOZILADI") {
  console.error("❌ BOT_TOKEN environment variable o'rnatilmagan!");
  process.exit(1);
}

// === ADMIN_CHAT_ID tekshiruvi ===
if (isNaN(ADMIN_CHAT_ID)) {
  console.error("❌ ADMIN_CHAT_ID noto'g'ri formatda!");
  process.exit(1);
}
