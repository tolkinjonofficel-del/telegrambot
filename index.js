const TelegramBot = require("node-telegram-bot-api");

// BOT TOKEN va ADMIN ID ni o'zgartiring
const token = process.env.BOT_TOKEN || "7454675594:AAFImURbtBJchKqfNa8LJZ4a7-xiLd_b4Kc";
const ADMIN_CHAT_ID = 7081746531; // o'zingizni ID bilan almashtiring (yoki null)

const bot = new TelegramBot(token, { polling: true });
console.log("✅ Strategik bot ishga tushdi... (xato-fallback bilan)");

/* ---------- /start ---------- */
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const user = msg.from;

  // Adminga bildirish (agar ADMIN_CHAT_ID to'g'ri bo'lsa)
  if (ADMIN_CHAT_ID) {
    const notify = `
🧍‍♂️ <b>Yangi foydalanuvchi qo‘shildi</b>
👤 ${user.first_name || "—"} ${user.last_name || ""} (${user.username ? "@" + user.username : "—"})
🆔 <code>${user.id}</code>
`;
    bot.sendMessage(ADMIN_CHAT_ID, notify, { parse_mode: "HTML" }).catch(() => {});
  }

  const text = `
💎 <b>MegaPari va 888Starz strategik botga xush kelibsiz!</b>

🎮 <b>O'yinlar o'ynab daromad qilish imkoniyati</b>
• 🎯 Ishonchli platformalar
• 💰 Samarali strategiyalar
• 🚀 Ro'yxatdan o‘tib 200% BONUS olishingiz mumkin

🕹️ <b>Kerakli platformani tanlang:</b>
`;

  const opts = {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [{ text: "💰 MegaPari", callback_data: "plat_megapari" }, { text: "⭐ 888Starz", callback_data: "plat_888starz" }]
      ]
    }
  };

  await bot.sendMessage(chatId, text, opts);
});

/* ---------- Ma'lumotlar ---------- */
const PLATFORMS = {
  plat_megapari: {
    id: "megapari",
    name: "MegaPari",
    image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s",
    apk: "https://t.me/insayderAI/686" // t.me message link (fallback qo'llaniladi)
  },
  plat_888starz: {
    id: "888starz",
    name: "888Starz",
    image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s",
    apk: "https://t.me/insayderAI/682"
  }
};

/* O'yinlar (url'lar test uchun t.me/aifutbot ga olib boradi yoki berilgan saytlar) */
const GAME_LINKS = {
  apple: "https://aplleoffortunesignal-bukmekeriotherss.netlify.app/",
  aviator: "https://aviatorxxxxxsignalll.netlify.app/",
  // crash: internal text
  // penalty: internal text
  cristal: "https://t.me/aifutbot"
};

/* ---------- Bitta callback handler: platforma va o'yinlarni boshqaradi ---------- */
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  // Tezkor javob: tugma bosildi (spinner yo'qoladi)
  try {
    await bot.answerCallbackQuery(query.id);
  } catch (e) {
    // Agar answerCallbackQuery xato bersa — davom etamiz
  }

  // ---------- Platforma tanlandi ----------
  if (PLATFORMS[data]) {
    const p = PLATFORMS[data];
    const caption = `
🎯 <b>${p.name}</b> bukmekerni tanladingiz!

💸 <b>AIFUT</b> promokodi orqali ro‘yhatdan o‘ting va
🎁 <b>To‘liq ro‘yxatdan o‘tgan foydalanuvchilar uchun — 200% BONUS!</b>
`;

    // 1) Rasmni yuboramiz
    try {
      await bot.sendPhoto(chatId, p.image, { caption, parse_mode: "HTML" });
    } catch (err) {
      // rasm yuborishda xato bo'lsa oddiy xabar beramiz
      await bot.sendMessage(chatId, caption, { parse_mode: "HTML" });
    }

    // 2) APK yuborish: birinchi urinish sendDocument bilan, agar xato bo'lsa fallback link tugmasi bilan yuboramiz
    try {
      // sendDocument bilan t.me message-link ko'pincha ishlamaydi va xatoga olib keladi
      // shu sababli biz uni sinab ko'ramiz va catch da fallback yuboramiz
      await bot.sendDocument(chatId, p.apk, {
        caption: `📦 ${p.name} APK — yuklab oling va o‘rnatib ro‘yxatdan o‘ting.`,
        parse_mode: "HTML"
      });
    } catch (err) {
      console.warn("sendDocument xato, fallback link yuborilmoqda:", err && err.message);
      // Fallback: havola bilan tugma ko'rinishida yuborish
      await bot.sendMessage(
        chatId,
        `📦 <b>${p.name} APK yuklab olish</b>\nAgar fayl avtomatik yuborilmasa, quyidagi tugma orqali yuklab oling:`,
        {
          parse_mode: "HTML",
          reply_markup: {
            inline_keyboard: [[{ text: "📥 APK yuklab olish", url: p.apk }]]
          }
        }
      );
    }

    // 3) O'yinlar menyusini yuborish (shaффоф tugmalar: URL yoki ichki xabar)
    const gamesMsg = `🎰 <b>Daromad qilish uchun qaysi o‘yinni tanlaysiz?</b>\nKerakli o‘yinni tanlang:`;
    await bot.sendMessage(chatId, gamesMsg, {
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [{ text: "🍏 Apple of Fortune", callback_data: "game_apple" }, { text: "✈️ Aviator", callback_data: "game_aviator" }],
          [{ text: "💥 Crash", callback_data: "game_crash" }, { text: "⚽ Penalty", callback_data: "game_penalty" }],
          [{ text: "💎 Cristal", callback_data: "game_cristal" }]
        ]
      }
    });

    return;
  }

  // ---------- O'yinlar bilan ishlash ----------
  if (data && data.startsWith("game_")) {
    const gameKey = data.replace("game_", "");

    if (gameKey === "apple") {
      // tashqi sayt ochiladigan havola (URL tugma bilan)
      await bot.sendMessage(chatId, `🍏 Apple of Fortune — havola ochildi.`, {
        reply_markup: { inline_keyboard: [[{ text: "Ochish", url: GAME_LINKS.apple }]] }
      });
      return;
    }

    if (gameKey === "aviator") {
      await bot.sendMessage(chatId, `✈️ Aviator — havola ochildi.`, {
        reply_markup: { inline_keyboard: [[{ text: "Ochish", url: GAME_LINKS.aviator }]] }
      });
      return;
    }

    if (gameKey === "crash") {
      await bot.sendMessage(
        chatId,
        `💥 <b>Crash</b> — Aviatorning mini-versiyasi. Yangi o‘yinchilarga dastlab omad beradi, ammo undan keyin yo‘qotish ehtimoli bor. Tavsiya: kamroq o‘ynang.`,
        { parse_mode: "HTML" }
      );
      return;
    }

    if (gameKey === "penalty") {
      await bot.sendMessage(chatId, `⚽ <b>Penalty</b> — tez orada ushbu o‘yinga maxsus strategiya qo‘shiladi.`, {
        parse_mode: "HTML"
      });
      return;
    }

    if (gameKey === "cristal") {
      await bot.sendMessage(chatId, `💎 Cristal — test kanali: https://t.me/aifutbot`, { parse_mode: "HTML" });
      return;
    }
  }

  // Agar boshqa noma'lum callback bo'lsa — xabar beramiz
  await bot.sendMessage(chatId, "⚠️ Noma'lum tugma bosildi. Iltimos qayta urinib ko‘ring.");
});

/* ---------- Error logging ---------- */
bot.on("polling_error", (error) => {
  console.error("Polling error:", error);
});
