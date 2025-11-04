const TelegramBot = require("node-telegram-bot-api");

// 🔑 Bot tokeningizni yozing yoki Railway Environment Variables orqali qo‘shing
const token = process.env.BOT_TOKEN || "7454675594:AAFywGrnS-9Qo7zeLYOSdhKi1zxP04O1qhg";

// 👑 (Ixtiyoriy) Admin ID
const ADMIN_CHAT_ID = 7081746531;

const bot = new TelegramBot(token, { polling: true });

console.log("✅ MegaPari & 888Starz strategik bot ishga tushdi...");

// === /start komandasi ===
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const user = msg.from;

  // 🔔 Admin uchun yangi foydalanuvchi haqida bildirish
  if (ADMIN_CHAT_ID) {
    bot.sendMessage(
      ADMIN_CHAT_ID,
      `🧍‍♂️ <b>Yangi foydalanuvchi:</b>\n👤 ${user.first_name || "Noma’lum"}\n🆔 <code>${user.id}</code>\n🌐 @${
        user.username || "—"
      }`,
      { parse_mode: "HTML" }
    );
  }

  // 💬 Start xabari
  const message = `
💎 <b>MegaPari</b> va <b>888Starz</b> strategik botga xush kelibsiz!  

🎮 <b>O'yinlar o'ynab daromad qilish imkoniyati!</b>
• 🎯 Ishonchli platformalar  
• 💰 Samarali strategiyalar  
• 🚀 200% BONUS imkoniyati

🕹️ <b>Kerakli platformani tanlang:</b>
`;

  const options = {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          { text: "💰 MegaPari", callback_data: "megapari" },
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
    megapari: {
      name: "MegaPari",
      fileId: "AgAD4JEAAqqTSUg", // ✅ To‘g‘ridan-to‘g‘ri fayl ID
    },
    "888starz": {
      name: "888Starz",
      fileId: "AgADy5EAAqqTSUg", // ✅ To‘g‘ridan-to‘g‘ri fayl ID
    },
  };

  const platform = platforms[data];
  if (!platform) return;

  const caption = `
🎯 <b>${platform.name}</b> bukmekerni tanladingiz!  

💸 <b>AIFUT</b> promokodi orqali ro‘yxatdan o‘ting va  
🎁 <b>To‘liq ro‘yxatdan o‘tgan foydalanuvchilar uchun — 200% BONUS!</b>
`;

  try {
    // 📦 APK faylni to‘g‘ridan-to‘g‘ri yuborish
    await bot.sendDocument(chatId, platform.fileId, {
      caption,
      parse_mode: "HTML"
    });

    // 🎮 O'yinlar menyusi
    await bot.sendMessage(chatId, `
🎰 <b>Daromad qilish uchun o‘yinni tanlang:</b>
`, {
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [
            { text: "🍏 Apple of Fortune", url: "https://t.me/aifutbot" },
            { text: "✈️ Aviator", url: "https://t.me/aifutbot" }
          ],
          [
            { text: "⚽ Penalty", url: "https://t.me/aifutbot" },
            { text: "🚀 JetX", url: "https://t.me/aifutbot" }
          ],
          [
            { text: "💎 Cristal", url: "https://t.me/aifutbot" }
          ]
        ]
      }
    });
  } catch (error) {
    console.error("❌ Fayl yuborishda xato:", error);
    await bot.sendMessage(chatId, "⚠️ Xatolik yuz berdi. Keyinroq urinib ko‘ring.");
  }
});
