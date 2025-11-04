const TelegramBot = require("node-telegram-bot-api");

// 🔑 Tokeningizni kiriting yoki Railway Environment Variable orqali qo‘ying
const token = process.env.BOT_TOKEN || "7454675594:AAF3KjpNdhhMWk4QbI8uHuwk5uPjqTPFBUo";

// 👑 Ixtiyoriy: sizning admin ID’ingiz (agar yangi foydalanuvchilar haqida xabar olmoqchi bo‘lsangiz)
const ADMIN_CHAT_ID = 7081746531;

const bot = new TelegramBot(token, { polling: true });

console.log("✅ MegaPari va 888Starz strategik bot ishga tushdi...");

// === /start komandasi ===
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const user = msg.from;

  // 🔔 Ixtiyoriy: Admin uchun yangi foydalanuvchi haqida xabar
  const notifyAdmin = `
🧍‍♂️ <b>Yangi foydalanuvchi qo‘shildi!</b>
👤 Ism: ${user.first_name || "Noma’lum"}
🆔 ID: <code>${user.id}</code>
🌐 Username: ${user.username ? "@" + user.username : "—"}
`;
  if (ADMIN_CHAT_ID) bot.sendMessage(ADMIN_CHAT_ID, notifyAdmin, { parse_mode: "HTML" });

  // 🎯 Start xabari
  const message = `
💎 <b>MegaPari</b> va <b>888Starz</b> strategik botga xush kelibsiz!  

🎮 <b>O‘yinlar o‘ynab daromad qilish imkoniyati!</b>  
• 🎯 Ishonchli platformalar  
• 💰 Samarali strategiyalar  
• 🚀 Har kuni 200% BONUS imkoniyati  

💥 Ro‘yxatdan o‘ting va <b>AIFUT</b> promokodi bilan daromadni boshlang!  
🕹️ <b>Kerakli joyda o‘yna, o‘z tanlovingni qil!</b>
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

// === Tugma bosilganda ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  const platforms = {
    "megapari": {
      name: "MegaPari",
      apk: "https://t.me/insayderAI/686"
    },
    "888starz": {
      name: "888Starz",
      apk: "https://t.me/insayderAI/682"
    }
  };

  const platform = platforms[data];
  if (!platform) return;

  const caption = `
🎯 <b>${platform.name}</b> bukmekerni tanladingiz!  

💸 <b>AIFUT</b> promokodi orqali ro‘yxatdan o‘ting va  
🎁 <b>To‘liq ro‘yxatdan o‘tganingiz uchun — 200% BONUSni qo‘lga kiriting!</b>
`;

  try {
    // 📦 APK fayl (fayl sifatida)
    await bot.sendDocument(chatId, platform.apk, {
      caption,
      parse_mode: "HTML"
    });

    // 🎮 O‘yinlar menyusi
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
    console.error("❌ Xato:", error);
    await bot.sendMessage(chatId, "⚠️ Xatolik yuz berdi, keyinroq urinib ko‘ring.");
  }
});
