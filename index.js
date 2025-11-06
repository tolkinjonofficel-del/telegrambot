const TelegramBot = require("node-telegram-bot-api");
const token = process.env.BOT_TOKEN || "7454675594:AAFywGrnS-9Qo7zeLYOSdhKi1zxP04O1qhg"; // 👈 Tokeningizni qo‘ying

const bot = new TelegramBot(token, { polling: true });

// Oddiy vaqtinchalik bazani yaratamiz (RAM ichida)
const users = {}; // { userId: { referrals: Set([...]), invitedBy: userId } }

console.log("✅ Sport kupon bot ishga tushdi...");

// === START komandasi ===
bot.onText(/\/start(?: (.+))?/, async (msg, match) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const referrerId = match[1]; // /start <referral_id>

  // Referral tizimi
  if (referrerId && referrerId !== String(userId)) {
    if (!users[userId]) users[userId] = { referrals: new Set(), invitedBy: referrerId };
    if (!users[referrerId]) users[referrerId] = { referrals: new Set() };
    users[referrerId].referrals.add(userId);

    // Agar taklif qilgan foydalanuvchi 10 ta odamga yetgan bo‘lsa — kupon kodi yuboriladi
    if (users[referrerId].referrals.size >= 10) {
      await bot.sendMessage(referrerId, "🎉 Siz 10 ta do‘st taklif qildingiz!\nKupon kodingiz: <b>XVGZD</b>", {
        parse_mode: "HTML",
      });
    }
  }

  // Start xabar
  const startMessage = `
⚽️ <b>Ushbu bot yordamida har kuni bepul kuponlar oling!</b>

💡 <b>Ishonchli kuponlar</b> har kuni sizlar uchun AI yordamida tayyorlanadi.  
📋 Pastdagi tugmani bosing va ishonchli kupon oling 👇
`;

  const options = {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [[{ text: "📋 Kupon olish", callback_data: "get_coupon" }]],
    },
  };

  await bot.sendMessage(chatId, startMessage, options);
});

// === Kupon olish bosilganda ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  if (data === "get_coupon") {
    const caption = `
🎯 <b>99.99% ishonchli kupon!</b>  
Kuponni olish uchun quyidagi bukmekerdan birini tanlang 👇
`;

    const imageUrl =
      "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSx42j_KVKzgj4x0mWs2PAcVMAEQAwakFY_Sg&s";

    await bot.sendPhoto(chatId, imageUrl, {
      caption,
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [
            { text: "💎 1xBet", callback_data: "bm_1xbet" },
            { text: "🔥 Melbet", callback_data: "bm_melbet" },
          ],
          [
            { text: "⚡ Winwin", callback_data: "bm_winwin" },
            { text: "🏆 DBbet", callback_data: "bm_dbbet" },
          ],
        ],
      },
    });
    return;
  }

  // === Bukmeker tanlanganda ===
  if (data.startsWith("bm_")) {
    const bookmaker = data.replace("bm_", "").toUpperCase();

    const text = `
🏦 <b>${bookmaker}</b> bukmekerni tanladingiz!  

💸 Kupon kodini olish uchun <b>10 ta do‘stni</b> botga taklif qiling.  
📨 Taklif tugmasini bosing va do‘stlaringizga yuboring 👇
`;

    await bot.sendMessage(chatId, text, {
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: "📨 Do‘stni taklif qilish",
              switch_inline_query: "", // inline share (Telegram menyusi ochiladi)
            },
          ],
        ],
      },
    });

    // Shuningdek, foydalanuvchiga referral havolani yuboramiz
    const referralLink = `https://t.me/${(await bot.getMe()).username}?start=${chatId}`;
    await bot.sendMessage(
      chatId,
      `🔗 Sizning taklif havolangiz:\n<code>${referralLink}</code>\n\nDo‘stingiz botga qo‘shilganda avtomatik hisoblanadi.`,
      { parse_mode: "HTML" }
    );
    return;
  }
});
