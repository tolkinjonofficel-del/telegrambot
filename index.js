const TelegramBot = require("node-telegram-bot-api");
const token = process.env.BOT_TOKEN || "7454675594:AAFywGrnS-9Qo7zeLYOSdhKi1zxP04O1qhg"; // 👈 Tokeningizni qo‘ying

const bot = new TelegramBot(token, { polling: true });

// Oddiy vaqtinchalik ma’lumotlar bazasi
const users = {}; // { userId: { referrals: Set([...]), invitedBy: userId } }

console.log("✅ Sport kupon bot ishga tushdi...");

// === START komandasi ===
bot.onText(/\/start(?: (.+))?/, async (msg, match) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const referrerId = match[1]; // /start <referral_id>

  // Referral tizimi ishlashi
  if (referrerId && referrerId !== String(userId)) {
    if (!users[userId]) users[userId] = { referrals: new Set(), invitedBy: referrerId };
    if (!users[referrerId]) users[referrerId] = { referrals: new Set() };
    users[referrerId].referrals.add(userId);

    // Agar taklif qilgan foydalanuvchi 10 ta do‘stga yetgan bo‘lsa
    if (users[referrerId].referrals.size >= 10) {
      await bot.sendMessage(
        referrerId,
        "🎉 Siz 10 ta do‘st taklif qildingiz!\nKupon kodingiz: <b>XVGZD</b>",
        { parse_mode: "HTML" }
      );
    }
  }

  // Start xabari
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

// === Callback bosilganda ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  // Kupon olish
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

  // Bukmeker tanlanganda
  if (data.startsWith("bm_")) {
    const bookmaker = data.replace("bm_", "").toUpperCase();

    const text = `
🏦 <b>${bookmaker}</b> bukmekerni tanladingiz!  

💸 Kupon kodini olish uchun <b>10 ta do‘stni</b> botga taklif qiling.  
📨 Taklif tugmasini bosing va do‘stlaringizga yuboring 👇
`;

    // Havola yaratish
    const botInfo = await bot.getMe();
    const referralLink = `https://t.me/${botInfo.username}?start=${chatId}`;

    await bot.sendMessage(chatId, text, {
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [
            { text: "📨 Do‘stni taklif qilish", callback_data: "invite_friends" },
          ],
        ],
      },
    });

    // Havolani keyin foydalanish uchun saqlaymiz
    users[chatId] = { ...users[chatId], referralLink };
    return;
  }

  // === Do‘stni taklif qilish tugmasi bosilganda ===
  if (data === "invite_friends") {
    const referralLink = users[chatId]?.referralLink;
    if (!referralLink) {
      await bot.sendMessage(chatId, "⚠️ Taklif havolasini topib bo‘lmadi. Iltimos, qaytadan boshlang /start");
      return;
    }

    const inviteMessage = `
🤝 <b>Do‘stingizni taklif qiling!</b>

📲 Sizning taklif havolangiz:
<code>${referralLink}</code>

🗣 Do‘stlaringizga yuboring va ularga shunday yozing:
<i>“Do‘stim, sen ham biz bilan g‘alaba qil! Kuponni hoziroq ol!”</i>
`;

    await bot.sendMessage(chatId, inviteMessage, { parse_mode: "HTML" });
    return;
  }
});
