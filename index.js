const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = process.env.BOT_TOKEN || "7454675594:AAFYU-QHScmLm_nykJi37eJwjSvSeRu33Nw";
const ADMIN_ID = 7081746531;
const CHANNEL_LINK = "https://t.me/insayderai";

const bot = new TelegramBot(TOKEN, { polling: true });

// === Dastur o‘zgaruvchilari ===
let coupon = {
  title: "Bugungi AI kuponi",
  text: `
⚽ Aston Villa vs Makkabi — Aston Villa (-1.5) (1.68 KF)
⚽ Boloniya vs Brann — 1-taym Boloniya (1.78 KF)
⚽ Braga vs Genk — Har ikkala taymda gol (1.64 KF)
⚽ Viktoriya P. vs Fenerbahçe — Uglavoylar <8.5 (1.63 KF)
<b>UMUMIY KOEFF: 8.12</b>`,
  image: "https://www.pymnts.com/wp-content/uploads/2024/04/Meta-AI-tech.png?w=457",
  requireShare: false,
  buttons: [
    [{ text: "📨 Kuponni tarqatish", callback_data: "share_coupon" }]
  ]
};

const users = {}; // { userId: { username } }

console.log("✅ Sport Kupon Bot ishga tushdi...");

// === Xabar yuborish yordamchisi ===
async function sendHtml(chatId, text, buttons = null) {
  const options = { parse_mode: "HTML" };
  if (buttons) options.reply_markup = { inline_keyboard: buttons };
  return bot.sendMessage(chatId, text, options);
}

// === START komandasi ===
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const username = msg.from.username ? `@${msg.from.username}` : msg.from.first_name;

  // 🧾 Adminni yangi foydalanuvchidan xabardor qilish
  if (userId !== ADMIN_ID) {
    await bot.sendMessage(
      ADMIN_ID,
      `🧍‍♂️ <b>Yangi foydalanuvchi:</b>\n👤 ${username}\n🆔 ${userId}`,
      { parse_mode: "HTML" }
    );
  }

  users[userId] = { username };

  // Start menyu
  await sendHtml(
    chatId,
    `
⚽️ <b>Har kuni yangi futbol kuponlari!</b>

📊 <b>Professional tahlillar</b>, 🎯 <b>aniq prognozlar</b> va 💰 <b>ishonchli kuponlar</b> shu yerda.
`,
    [
      [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
      [{ text: "🎁 Bugungi kuponni olish", callback_data: "get_coupon" }]
    ]
  );
});

// === CALLBACKLAR ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;
  await bot.answerCallbackQuery(query.id);

  // === Kuponni olish ===
  if (data === "get_coupon") {
    if (coupon.requireShare) {
      return sendHtml(
        chatId,
        `📢 Ushbu kuponni olishdan avval uni do‘stlaringiz bilan ulashing 👇`,
        [[{ text: "🔗 Kuponni tarqatish", callback_data: "share_coupon" }]]
      );
    }

    // Kupon yuborish
    await bot.sendPhoto(chatId, coupon.image, {
      caption: `<b>${coupon.title}</b>\n\n${coupon.text}`,
      parse_mode: "HTML",
      reply_markup: { inline_keyboard: coupon.buttons }
    });
  }

  // === Kuponni tarqatish ===
  if (data === "share_coupon") {
    const botInfo = await bot.getMe();
    const shareText = encodeURIComponent(
      `🎯 Eng ishonchli futbol kuponlar!\nHar kuni yangi tahlillar bilan!\n👉 https://t.me/${botInfo.username}`
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

  await sendHtml(msg.chat.id, "🛠 <b>Admin panel:</b>", [
    [{ text: "🆕 Kupon qo‘shish / yangilash", callback_data: "admin_update_coupon" }],
    [{ text: "➕ Tugma qo‘shish", callback_data: "admin_add_button" }],
    [{ text: "📨 Xabar yuborish", callback_data: "admin_broadcast" }],
    [{ text: "⚙️ Kupon uchun tarqatish sharti", callback_data: "admin_share_condition" }]
  ]);
});


// === ADMIN CALLBACK ===
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
        const caption = msg.caption || "Kupon yangilandi.";
        coupon.image = photoId;
        coupon.text = caption;
      } else {
        coupon.text = msg.text;
      }
      await sendHtml(chatId, "✅ Kupon yangilandi!");
    });
  }

  // === Yangi tugma qo‘shish ===
  if (data === "admin_add_button") {
    await sendHtml(chatId, "🔘 Tugma nomini yozing:");
    bot.once("message", async (msg) => {
      const btnName = msg.text;
      await sendHtml(chatId, "🔗 Tugma havolasini yozing (yoki callback_data):");
      bot.once("message", async (msg2) => {
        const btnLink = msg2.text;
        coupon.buttons.push([{ text: btnName, url: btnLink }]);
        await sendHtml(chatId, `✅ Yangi tugma qo‘shildi: ${btnName}`);
      });
    });
  }

  // === Tarqatish shartini o‘rnatish ===
  if (data === "admin_share_condition") {
    await sendHtml(
      chatId,
      `⚙️ Kelgusi kupon uchun “Tarqatish majburiymi?”\n\n🟢 Ha yoki 🔴 Yo‘q deb yozing:`
    );
    bot.once("message", async (msg) => {
      const answer = msg.text.toLowerCase();
      coupon.requireShare = ["ha", "ha.", "ha✅"].includes(answer);
      await sendHtml(
        chatId,
        coupon.requireShare
          ? "✅ Endi foydalanuvchilar kupon olishdan oldin uni tarqatishlari shart."
          : "❌ Endi kupon olishda tarqatish majburiy emas."
      );
    });
  }

  // === Foydalanuvchilarga xabar yuborish ===
  if (data === "admin_broadcast") {
    await sendHtml(chatId, "✉️ Yuboriladigan xabar matnini yozing:");
    bot.once("message", async (msg) => {
      const text = msg.text;
      let count = 0;
      for (const id of Object.keys(users)) {
        try {
          await bot.sendMessage(id, `📢 <b>Admin xabari:</b>\n${text}`, { parse_mode: "HTML" });
          count++;
        } catch (e) {}
      }
      await sendHtml(chatId, `✅ ${count} ta foydalanuvchiga xabar yuborildi.`);
    });
  }
});
