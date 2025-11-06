const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = process.env.BOT_TOKEN || "7454675594:AAFYU-QHScmLm_nykJi37eJwjSvSeRu33Nw";
const CHANNEL_USERNAME = "@insayderai"; // obuna tekshirish uchun kanal
const CHANNEL_LINK = "https://t.me/insayderai";
const ADMIN_ID = 7081746531; // 👈 o'zingizning Telegram ID'ingizni kiriting

// === Dastur o‘zgaruvchilari ===
let coupon = {
  text: "Hozircha kupon mavjud emas. Admin tomonidan yangilanadi.",
  image: null,
  inviteLimit: 3 // necha do‘st taklif qilgandan keyin kupon beriladi
};

const bot = new TelegramBot(TOKEN, { polling: true });
const users = {}; // { userId: { invitedBy, referrals: Set() } }

console.log("✅ Kupon bot ishga tushdi...");

// === Xabar yuborish (HTML format) ===
async function sendHtml(chatId, text, buttons = null) {
  const opts = { parse_mode: "HTML" };
  if (buttons) opts.reply_markup = { inline_keyboard: buttons };
  return bot.sendMessage(chatId, text, opts);
}

// === START komandasi ===
bot.onText(/\/start(?: (.+))?/, async (msg, match) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const referrerId = match[1];

  // Adminni foydalanuvchilardan xabardor qilish
  if (userId !== ADMIN_ID) {
    await bot.sendMessage(ADMIN_ID, `🧍‍♂️ Yangi foydalanuvchi qo‘shildi:\n👤 ${msg.from.first_name}\n🆔 ${userId}`);
  }

  // Referral tizimi
  if (referrerId && referrerId !== String(userId)) {
    if (!users[userId]) users[userId] = { invitedBy: referrerId, referrals: new Set() };
    if (!users[referrerId]) users[referrerId] = { referrals: new Set() };
    const referrer = users[referrerId];
    if (!referrer.referrals.has(userId)) {
      referrer.referrals.add(userId);
      const total = referrer.referrals.size;

      await bot.sendMessage(
        referrerId,
        `👤 <b>1 ta yangi do‘st qo‘shildi!</b>\nSizda hozirda <b>${total}</b> ta taklif bor.`,
        { parse_mode: "HTML" }
      );
    }
  }

  await sendHtml(
    chatId,
    `
⚽️ <b>Ushbu bot har kuni futbol o‘yinlariga yangi kuponlar joylab boradi!</b>

📊 <b>Professional tahlillar</b>, 🎯 <b>aniq prognozlar</b> va 💰 <b>ishonchli kuponlar</b> shu yerda!

👇 Quyidagi tugmalardan foydalaning:
`,
    [
      [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
      [{ text: "🎁 Bugungi kuponni olish", callback_data: "get_coupon" }]
    ]
  );
});

// === CALLBACK TIZIMI ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;
  await bot.answerCallbackQuery(query.id);

  // === Kupon olish ===
  if (data === "get_coupon") {
    try {
      // 1️⃣ Kanalga obuna tekshirish
      const member = await bot.getChatMember(CHANNEL_USERNAME, chatId);
      const subscribed = ["member", "administrator", "creator"].includes(member.status);

      if (!subscribed) {
        return sendHtml(
          chatId,
          `❌ <b>Siz kanalga a’zo emassiz!</b>\nKuponni olish uchun avval quyidagi kanalda a’zo bo‘ling 👇`,
          [
            [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
            [{ text: "✅ A’zo bo‘ldim", callback_data: "get_coupon" }]
          ]
        );
      }

      // 2️⃣ Foydalanuvchi necha do‘st taklif qilganini tekshirish
      const user = users[chatId];
      const referrals = user?.referrals?.size || 0;

      if (referrals < coupon.inviteLimit) {
        const remaining = coupon.inviteLimit - referrals;
        const botInfo = await bot.getMe();
        const referralLink = `https://t.me/${botInfo.username}?start=${chatId}`;

        return sendHtml(
          chatId,
          `👥 <b>Siz hali ${remaining} ta do‘stni taklif qilishingiz kerak!</b>\n\n🗣 Quyidagi havolani do‘stlaringizga yuboring:\n<code>${referralLink}</code>`,
          [[{ text: "📨 Do‘stni taklif qilish", url: `https://t.me/share/url?url=${referralLink}` }]]
        );
      }

      // 3️⃣ Agar hammasi to‘g‘ri bo‘lsa — kupon yuboriladi
      if (coupon.image) {
        await bot.sendPhoto(chatId, coupon.image, { caption: coupon.text, parse_mode: "HTML" });
      } else {
        await sendHtml(chatId, `🎯 <b>Bugungi kupon:</b>\n\n${coupon.text}`);
      }
    } catch (err) {
      console.error("❌ Kupon xatosi:", err.message);
      await sendHtml(chatId, `⚠️ Obunani tekshirishda xato. Keyinroq urinib ko‘ring.`);
    }
  }
});


// === ADMIN PANEL ===
bot.onText(/\/admin/, async (msg) => {
  const chatId = msg.chat.id;
  if (chatId !== ADMIN_ID) return;

  await sendHtml(
    chatId,
    "🛠 <b>Admin panel:</b>",
    [
      [{ text: "📝 Kuponni yangilash", callback_data: "admin_update_coupon" }],
      [{ text: "📊 Limitni o‘zgartirish", callback_data: "admin_set_limit" }],
      [{ text: "📤 Barcha foydalanuvchilarga xabar yuborish", callback_data: "admin_broadcast" }]
    ]
  );
});

// === ADMIN TUGMALAR ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;
  await bot.answerCallbackQuery(query.id);

  if (chatId !== ADMIN_ID) return; // faqat admin

  // Kuponni yangilash
  if (data === "admin_update_coupon") {
    await sendHtml(chatId, "📝 Kupon matnini yuboring (rasm yuborish ixtiyoriy).");
    bot.once("message", async (msg) => {
      if (msg.photo) {
        const photoId = msg.photo[msg.photo.length - 1].file_id;
        const caption = msg.caption || "Kupon matni yo‘q.";
        coupon = { text: caption, image: photoId, inviteLimit: coupon.inviteLimit };
      } else {
        coupon = { ...coupon, text: msg.text };
      }
      await sendHtml(chatId, "✅ Kupon yangilandi!");
    });
  }

  // Limitni o‘zgartirish
  if (data === "admin_set_limit") {
    await sendHtml(chatId, "⚙️ Yangi limitni kiriting (masalan: 3)");
    bot.once("message", async (msg) => {
      const limit = parseInt(msg.text);
      if (isNaN(limit)) return sendHtml(chatId, "❌ Noto‘g‘ri raqam!");
      coupon.inviteLimit = limit;
      await sendHtml(chatId, `✅ Limit yangilandi! Endi foydalanuvchi ${limit} ta do‘st taklif qilsa kupon oladi.`);
    });
  }

  // Foydalanuvchilarga xabar yuborish
  if (data === "admin_broadcast") {
    await sendHtml(chatId, "✉️ Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:");
    bot.once("message", async (msg) => {
      const text = msg.text;
      let sent = 0;
      for (const id of Object.keys(users)) {
        try {
          await bot.sendMessage(id, `📢 <b>Admin xabari:</b>\n${text}`, { parse_mode: "HTML" });
          sent++;
        } catch (e) {}
      }
      await sendHtml(chatId, `✅ ${sent} ta foydalanuvchiga xabar yuborildi.`);
    });
  }
});
