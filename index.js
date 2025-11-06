const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = process.env.BOT_TOKEN || "7454675594:AAFYU-QHScmLm_nykJi37eJwjSvSeRu33Nw";
const REQUIRED_INVITES = 10;
const COUPON_CODE = "NDNH2";
const IMAGE_URL = "https://www.pymnts.com/wp-content/uploads/2024/04/Meta-AI-tech.png?w=457";

// === Botni ishga tushiramiz ===
const bot = new TelegramBot(TOKEN, { polling: true });
const users = {}; // { userId: { referrals: Set(), invitedBy: userId } }
const userStates = {}; // Foydalanuvchi holatlarini kuzatish

console.log("✅ Sport kupon bot ishga tushdi...");

// === Yordamchi funksiya: xabar yuborish ===
async function sendHtml(chatId, text, buttons = null) {
  const options = { parse_mode: "HTML" };
  if (buttons) options.reply_markup = { inline_keyboard: buttons };
  await bot.sendMessage(chatId, text, options);
}

// === Yordamchi funksiya: callback query ni tugatish ===
async function answerCallbackQuery(query, text = "") {
  try {
    await bot.answerCallbackQuery(query.id, { text });
  } catch (error) {
    console.log("Callback query answer error:", error.message);
  }
}

// === START komandasi ===
bot.onText(/\/start(?: (.+))?/, async (msg, match) => {
  const userId = msg.from.id;
  const chatId = msg.chat.id;
  const referrerId = match[1];

  // Foydalanuvchi holatini tiklash
  userStates[userId] = { processing: false };

  // Referral tizimi
  if (referrerId && referrerId !== String(userId)) {
    if (!users[userId]) users[userId] = { referrals: new Set(), invitedBy: referrerId };
    if (!users[referrerId]) users[referrerId] = { referrals: new Set() };

    const referrer = users[referrerId];
    if (!referrer.referrals.has(userId)) {
      referrer.referrals.add(userId);

      const total = referrer.referrals.size;
      const remaining = Math.max(REQUIRED_INVITES - total, 0);

      if (total < REQUIRED_INVITES) {
        await sendHtml(
          referrerId,
          `👤 <b>Yangi do'st qo'shildi!</b>\nSizda <b>${total}</b> ta taklif bor.\nYana <b>${remaining}</b> ta do'st taklif qilsangiz — kupon kodi sizga yuboriladi 🎯`
        );
      } else if (total === REQUIRED_INVITES) {
        await sendHtml(
          referrerId,
          `🎉 <b>Tabriklaymiz!</b> Siz ${REQUIRED_INVITES} ta do'stni taklif qildingiz!\n\nKupon kodi: <b>${COUPON_CODE}</b>\n\n<b>07 NOYABR, 01:00 YEVROPA LIGASI:</b>\n⚽ Aston Villa vs Makkabi — Aston Villa (-1.5) (1.68 KF)\n⚽ Boloniya vs Brann — 1-taym Boloniya (1.78 KF)\n⚽ Braga vs Genk — Har ikkala taymda gol (1.64 KF)\n⚽ Viktoriya P. vs Fenerbahçe — Uglavoylar <8.5 (1.63 KF)\n<b>UMUMIY KOEFF: 8.12</b>`
        );
      }
    }
  }

  // Boshlang'ich xabar
  await sendHtml(chatId, `
⚽️ <b>Ushbu bot yordamida har kuni FUTBOL oyinlariga bepul kuponlar oling!</b>

💡 <b>Ishonchli kuponlar</b> har kuni AI yordamida tayyorlanadi.  
📋 Pastdagi tugmani bosing va ishonchli kupon oling 👇
`, [[{ text: "📋 Kupon olish", callback_data: "get_coupon" }]]);
});

// === CALLBACK bosilganda ===
bot.on("callback_query", async (query) => {
  const userId = query.from.id;
  const chatId = query.message.chat.id;
  const data = query.data;

  // Bir xil so'rovni qayta ishlashni oldini olish
  if (userStates[userId] && userStates[userId].processing) {
    await answerCallbackQuery(query, "⏳ Iltimos, biroz kuting...");
    return;
  }

  // Holatni "qayta ishlanmoqda" deb belgilash
  userStates[userId] = { processing: true };

  try {
    // === Kupon olish ===
    if (data === "get_coupon") {
      await answerCallbackQuery(query, "📋 Kupon yuborilmoqda...");
      
      await bot.sendPhoto(chatId, IMAGE_URL, {
        caption: `
🎯 <b>99.99% ishonchli kupon!</b>
Kuponni olish uchun bukmekerni tanlang 👇`,
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
    }

    // === Bukmeker tanlanganda ===
    else if (data.startsWith("bm_")) {
      await answerCallbackQuery(query, "🏦 Bukmeker tanlandi...");
      
      const bookmaker = data.replace("bm_", "").toUpperCase();
      const botInfo = await bot.getMe();
      const referralLink = `https://t.me/${botInfo.username}?start=${chatId}`;

      const text = `
🏦 <b>${bookmaker}</b> bukmekerni tanladingiz!

💸 FUTBOL oyinlariga ishonchli Kupon  olish uchun <b>${REQUIRED_INVITES} ta do'stni</b> taklif qiling.  
10 ta odam taklif qilinganda bot avtomatik KUPON yuboradi va galaba qiling 📨 Quyidagi tugmani bosing va ulashish oynasidan do'stlaringizga yuboring 👇
`;

      const shareText = encodeURIComponent(
        `Do'stim, sen ham biz bilan g'alaba qil! ⚽️ 99.99% ishonchli kuponlarni shu botdan ol! 🔥\n👉 ${referralLink}`
      );
      const shareUrl = `https://t.me/share/url?url=${referralLink}&text=${shareText}`;

      await sendHtml(chatId, text, [[{ text: "📨 Do'stni taklif qilish", url: shareUrl }]]);

      users[chatId] = { ...users[chatId], referralLink };
    }

  } catch (error) {
    console.error("Callback query error:", error);
    await answerCallbackQuery(query, "❌ Xatolik yuz berdi, qayta urinib ko'ring");
  } finally {
    // Holatni qayta tiklash
    setTimeout(() => {
      userStates[userId] = { processing: false };
    }, 1000);
  }
});

// === Xatoliklar bilan ishlash ===
bot.on("polling_error", (error) => {
  console.log("Polling error:", error.message);
});

bot.on("webhook_error", (error) => {
  console.log("Webhook error:", error.message);
});
