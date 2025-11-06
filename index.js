const TelegramBot = require("node-telegram-bot-api");
const token = process.env.BOT_TOKEN || "7454675594:AAGXaG5eRBClVwj9PjSyqcK5B_VV1FqWvLQ"; // 👈 o'zingizning tokeningizni kiriting

const bot = new TelegramBot(token, { polling: true });

// Vaqtinchalik bazani yaratamiz (RAM ichida)
const users = {}; // { userId: { referrals: Set([...]), invitedBy: userId } }

console.log("✅ Sport kupon bot ishga tushdi...");

// === START komandasi ===
bot.onText(/\/start(?: (.+))?/, async (msg, match) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const referrerId = match[1]; // /start <ref_id>

  // === Referral tizimi ===
  if (referrerId && referrerId !== String(userId)) {
    if (!users[userId]) users[userId] = { referrals: new Set(), invitedBy: referrerId };
    if (!users[referrerId]) users[referrerId] = { referrals: new Set() };

    // Yangi foydalanuvchini ro‘yxatga olish
    const referrer = users[referrerId];
    if (!referrer.referrals.has(userId)) {
      referrer.referrals.add(userId);

      const total = referrer.referrals.size;
      const remaining = Math.max(10 - total, 0);

      // Taklifchi foydalanuvchiga xabar yuborish
      if (total < 10) {
        await bot.sendMessage(
          referrerId,
          `👤 <b>1 ta yangi do‘st qo‘shildi!</b>\nSizda hozirda <b>${total}</b> ta taklif mavjud.\nYana <b>${remaining}</b> ta do‘st taklif qilsangiz, sizga kupon kodi yuboriladi 🎯`,
          { parse_mode: "HTML" }
        );
      }

      // Agar 10 ta do‘st to‘plansa
      if (total === 10) {
        await bot.sendMessage(
          referrerId,
          "🎉 Tabriklaymiz! Siz 10 ta do‘stni taklif qildingiz!\n kupon kodi
1Xbet:
Melbet:
WinWin:
DBbet: <b>XVGZD</b>",
          { parse_mode: "HTML" }
        );
      }
    }
  }

  // === Boshlang‘ich xabar ===
  const startMessage = `
⚽️ <b>Ushbu bot yordamida har kuni bepul kuponlar oling!</b>

💡 <b>Ishonchli kuponlar</b> har kuni sizlar uchun AI yordamida tayyorlanadi.  
📋 Pastdagi tugmani bosing va ishonchli kupon oling 👇
`;

  await bot.sendMessage(chatId, startMessage, {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [[{ text: "📋 Kupon olish", callback_data: "get_coupon" }]],
    },
  });
});

// === Callback bosilganda ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  // === Kupon olish ===
  if (data === "get_coupon") {
    const caption = `
🎯 <b>100% ishonchli kupon!</b>  
Kuponni olish uchun quyidagi bukmekerdan birini tanlang 👇
`;

    const imageUrl =
      "https://ai-ageency.ru/wp-content/uploads/2025/09/low-price.webp";

    await bot.sendPhoto(chatId, imageUrl, {
      caption,
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [
            { text: "🔵 1xBet", callback_data: "bm_1xbet" },
            { text: "🟠 Melbet", callback_data: "bm_melbet" },
          ],
          [
            { text: "🟢 Winwin", callback_data: "bm_winwin" },
            { text: "🔴 DBbet", callback_data: "bm_dbbet" },
          ],
        ],
      },
    });
    return;
  }

  // === Bukmeker tanlanganda ===
  if (data.startsWith("bm_")) {
    const bookmaker = data.replace("bm_", "").toUpperCase();

    const botInfo = await bot.getMe();
    const referralLink = `https://t.me/${botInfo.username}?start=${chatId}`;

    const text = `
🏦 <b>${bookmaker}</b> bukmekerni tanladingiz!  

💸 Kupon kodini olish uchun <b>10 ta do‘stni</b> botga taklif qiling.  
📨 Taklif tugmasini bosing va yuboring 10 ta odam qoshilganidan song avtomatik ravishda kupon kodi yuboriladi👇
`;

    // Share havolasi (Telegram “Do‘stga ulashish” oynasi uchun)
    const shareText = encodeURIComponent(
      `Do‘stim, sen ham biz bilan g‘alaba qil! ⚽️\n100% ishonchli kuponlarni shu botdan ol! 🔥\n\n👉 ${referralLink}`
    );
    const shareUrl = `https://t.me/share/url?url=${referralLink}&text=${shareText}`;

    await bot.sendMessage(chatId, text, {
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [[{ text: "📨 Taklif qilish", url: shareUrl }]],
      },
    });

    // Foydalanuvchining havolasini saqlaymiz
    users[chatId] = { ...users[chatId], referralLink };
    return;
  }
});
