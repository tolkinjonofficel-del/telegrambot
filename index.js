const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = process.env.BOT_TOKEN || "7454675594:AAFYU-QHScmLm_nykJi37eJwjSvSeRu33Nw";
const ADMIN_ID = 7081746531; // 👈 Admin ID
const CHANNEL_USERNAME = "@insayderai";
const CHANNEL_LINK = "https://t.me/insayderai";

// === O‘zgaruvchilar ===
let coupon = {
  title: "Bugungi AI kuponi",
  text: "⚽️ Aston Villa vs Makkabi — Aston Villa (-1.5) (1.68 KF)\n⚽️ Boloniya vs Brann — 1-taym Boloniya (1.78 KF)\n⚽️ Braga vs Genk — Har ikkala taymda gol (1.64 KF)\n⚽️ Viktoriya P. vs Fenerbahçe — Uglavoylar <8.5 (1.63 KF)\n<b>UMUMIY KOEFF: 8.12</b>",
  image: "https://www.pymnts.com/wp-content/uploads/2024/04/Meta-AI-tech.png?w=457",
  buttons: [
    [{ text: "📨 Kuponni tarqatish", callback_data: "share_coupon" }]
  ]
};

const bot = new TelegramBot(TOKEN, { polling: true });
const users = {};

console.log("✅ AI Sport Kupon bot ishga tushdi...");

// === Yordamchi funksiya ===
async function sendHtml(chatId, text, buttons = null) {
  const opts = { parse_mode: "HTML" };
  if (buttons) opts.reply_markup = { inline_keyboard: buttons };
  return bot.sendMessage(chatId, text, opts);
}

// === START komandasi ===
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  // 🔔 Adminga yangi foydalanuvchi haqida bildirish
  if (userId !== ADMIN_ID) {
    await bot.sendMessage(
      ADMIN_ID,
      `🧍‍♂️ <b>Yangi foydalanuvchi:</b>\n👤 ${msg.from.first_name}\n🆔 ${userId}`,
      { parse_mode: "HTML" }
    );
  }

  const startText = `
⚽️ <b>Ushbu bot har kuni futbol o‘yinlariga yangi kupon joylab boradi!</b>

📊 Eng aniq AI tahlillar, 🎯 professional prognozlar va 💰 ishonchli kuponlar shu yerda!
`;

  const buttons = [
    [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
    [{ text: "🎁 Bugungi kuponni olish", callback_data: "get_coupon" }]
  ];

  await sendHtml(chatId, startText, buttons);
});

// === Callbacklar ===
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
          `❌ <b>Siz kanalga a’zo emassiz!</b>\nKuponni olish uchun quyidagi kanalda a’zo bo‘ling 👇`,
          [
            [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
            [{ text: "✅ A’zo bo‘ldim", callback_data: "get_coupon" }]
          ]
        );
      }

      // 2️⃣ A’zo bo‘lgan — kuponni ko‘rsatish
      await bot.sendPhoto(chatId, coupon.image, {
        caption: `<b>${coupon.title}</b>\n\n${coupon.text}`,
        parse_mode: "HTML",
        reply_markup: { inline_keyboard: coupon.buttons }
      });
    } catch (err) {
      console.error("❌ Obuna tekshirish xatosi:", err.message);
      await sendHtml(chatId, "⚠️ Obuna holatini tekshirishda xatolik. Keyinroq urinib ko‘ring.");
    }
  }

  // === Kuponni tarqatish ===
  if (data === "share_coupon") {
    const shareText = encodeURIComponent(
      `🎯 Eng ishonchli futbol kuponlar! Har kuni yangilanadi ⚽️\nBotga qo‘shil: https://t.me/${(await bot.getMe()).username}`
    );
    const shareUrl = `https://t.me/share/url?text=${shareText}`;

    await sendHtml(chatId, "📤 Kuponni do‘stlaringizga yuboring 👇", [
      [{ text: "🔗 Tarqatish havolasini ulashish", url: shareUrl }]
    ]);
  }
});

// === ADMIN PANEL ===
bot.onText(/\/admin/, async (msg) => {
  if (msg.chat.id !== ADMIN_ID) return;

  await sendHtml(msg.chat.id, "🧩 <b>Admin panel:</b>", [
    [{ text: "🆕 Kupon qo‘shish / tahrirlash", callback_data: "admin_update_coupon" }],
    [{ text: "➕ Tugma qo‘shish", callback_data: "admin_add_button" }],
    [{ text: "📢 Foydalanuvchilarga xabar yuborish", callback_data: "admin_broadcast" }]
  ]);
});

bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;
  await bot.answerCallbackQuery(query.id);
  if (chatId !== ADMIN_ID) return;

  // === Kuponni yangilash ===
  if (data === "admin_update_coupon") {
    await sendHtml(chatId, "📝 Kupon matnini yuboring (rasm bilan yoki rasm holda).");
    bot.once("message", async (msg) => {
      if (msg.photo) {
        const photoId = msg.photo[msg.photo.length - 1].file_id;
        coupon.image = photoId;
        coupon.text = msg.caption || coupon.text;
      } else {
        coupon.text = msg.text;
      }
      await sendHtml(chatId, "✅ Kupon yangilandi!");
    });
  }

  // === Tugma qo‘shish ===
  if (data === "admin_add_button") {
    await sendHtml(chatId, "🔘 Yangi tugma matnini kiriting (masalan: Tarqatish havolasi):");
    bot.once("message", async (msg) => {
      const buttonText = msg.text;
      await sendHtml(chatId, "🔗 Tugma havolasini kiriting (yoki callback_data yozing):");
      bot.once("message", async (msg2) => {
        const buttonUrl = msg2.text;
        coupon.buttons.push([{ text: buttonText, url: buttonUrl }]);
        await sendHtml(chatId, `✅ Tugma qo‘shildi: ${buttonText}`);
      });
    });
  }

  // === Xabar yuborish ===
  if (data === "admin_broadcast") {
    await sendHtml(chatId, "📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:");
    bot.once("message", async (msg) => {
      const text = msg.text;
      let count = 0;
      for (const id of Object.keys(users)) {
        try {
          await sendHtml(id, `📢 <b>Admin xabari:</b>\n${text}`);
          count++;
        } catch (e) {}
      }
      await sendHtml(chatId, `✅ ${count} ta foydalanuvchiga yuborildi.`);
    });
  }
});
