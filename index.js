const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = "7454675594:AAFYU-QHScmLm_nykJi37eJwjSvSeRu33Nw"; // o'zingizning tokeningizni kiriting
const ADMIN_ID = 7081746531;
const CHANNEL_LINK = "https://t.me/insayderai";

const bot = new TelegramBot(TOKEN, { polling: true });
console.log("✅ Sport Kupon Bot ishga tushdi...");

// === Kupon ma'lumotlari ===
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
  buttons: [[{ text: "📨 Kuponni tarqatish", callback_data: "share_coupon" }]],
};

// === Foydalanuvchilar ===
const users = {};

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
  const username = msg.from.username ? `@${msg.from.username}` : msg.from.first_name;

  if (!users[userId]) users[userId] = { username };

  // 🔔 Adminga xabar
  if (userId !== ADMIN_ID) {
    await bot.sendMessage(
      ADMIN_ID,
      `🧍‍♂️ <b>Yangi foydalanuvchi:</b>\n👤 ${username}\n🆔 ${userId}`,
      { parse_mode: "HTML" }
    );
  }

  // Boshlang‘ich menyu
  await sendHtml(
    chatId,
    `
⚽️ <b>Har kuni yangi futbol kuponlari!</b>

📊 Professional tahlil, 🎯 aniq prognoz va 💰 ishonchli kuponlar shu yerda.
`,
    [
      [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
      [{ text: "🎁 Bugungi kuponni olish", callback_data: "get_coupon" }],
    ]
  );
});

// === Bitta yagona CALLBACK listener ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  try {
    // === Kupon olish ===
    if (data === "get_coupon") {
      if (coupon.requireShare) {
        return sendHtml(
          chatId,
          "📢 Ushbu kuponni olishdan oldin uni do‘stlaringizga yuboring 👇",
          [[{ text: "🔗 Kuponni tarqatish", callback_data: "share_coupon" }]]
        );
      }

      // Kuponni yuborish
      await bot.sendPhoto(chatId, coupon.image, {
        caption: `<b>${coupon.title}</b>\n\n${coupon.text}`,
        parse_mode: "HTML",
        reply_markup: { inline_keyboard: coupon.buttons },
      });
    }

    // === Kuponni tarqatish ===
    else if (data === "share_coupon") {
      const botInfo = await bot.getMe();
      const shareText = encodeURIComponent(
        `🎯 Eng ishonchli futbol kuponlar!\nHar kuni yangi tahlillar bilan!\n👉 https://t.me/${botInfo.username}`
      );
      const shareUrl = `https://t.me/share/url?text=${shareText}`;
      await sendHtml(chatId, "📤 Kuponni do‘stlaringizga yuboring 👇", [
        [{ text: "🔗 Tarqatish havolasini ulashish", url: shareUrl }],
      ]);
    }

    // === ADMIN PANEL BOSHQARUVI ===
    else if (data === "admin_update_coupon" && chatId === ADMIN_ID) {
      await sendHtml(chatId, "📝 Kupon matnini yuboring (rasm bilan yoki rasm holda):");
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

    else if (data === "admin_add_button" && chatId === ADMIN_ID) {
      await sendHtml(chatId, "🔘 Tugma nomini kiriting:");
      bot.once("message", async (msg) => {
        const name = msg.text;
        await sendHtml(chatId, "🔗 Tugma havolasini kiriting (yoki callback_data):");
        bot.once("message", async (msg2) => {
          const link = msg2.text;
          coupon.buttons.push([{ text: name, url: link }]);
          await sendHtml(chatId, `✅ Yangi tugma qo‘shildi: ${name}`);
        });
      });
    }

    else if (data === "admin_share_condition" && chatId === ADMIN_ID) {
      await sendHtml(chatId, "⚙️ Tarqatish majburiy bo‘lsinmi? (ha/yo‘q)");
      bot.once("message", async (msg) => {
        coupon.requireShare = msg.text.toLowerCase().startsWith("ha");
        await sendHtml(
          chatId,
          coupon.requireShare
            ? "✅ Tarqatish majburiy qilib qo‘yildi."
            : "❌ Tarqatish majburiy emas endi."
        );
      });
    }

    else if (data === "admin_broadcast" && chatId === ADMIN_ID) {
      await sendHtml(chatId, "✉️ Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:");
      bot.once("message", async (msg) => {
        const text = msg.text;
        let count = 0;
        for (const id of Object.keys(users)) {
          try {
            await sendHtml(id, `📢 <b>Admin xabari:</b>\n${text}`);
            count++;
          } catch {}
        }
        await sendHtml(chatId, `✅ ${count} ta foydalanuvchiga yuborildi.`);
      });
    }

    else if (data === "open_admin_panel" && chatId === ADMIN_ID) {
      await sendHtml(chatId, "🧩 <b>Admin panel:</b>", [
        [{ text: "🆕 Kupon qo‘shish / yangilash", callback_data: "admin_update_coupon" }],
        [{ text: "➕ Tugma qo‘shish", callback_data: "admin_add_button" }],
        [{ text: "📨 Xabar yuborish", callback_data: "admin_broadcast" }],
        [{ text: "⚙️ Tarqatish majburiyligi", callback_data: "admin_share_condition" }],
      ]);
    }

    await bot.answerCallbackQuery(query.id);
  } catch (err) {
    console.error("❌ Xatolik:", err.message);
  }
});

// === ADMIN KOMANDASI ===
bot.onText(/\/admin/, async (msg) => {
  if (msg.chat.id !== ADMIN_ID) return;
  await sendHtml(msg.chat.id, "🧩 <b>Admin panel:</b>", [
    [{ text: "🆕 Kupon qo‘shish / yangilash", callback_data: "admin_update_coupon" }],
    [{ text: "➕ Tugma qo‘shish", callback_data: "admin_add_button" }],
    [{ text: "📨 Xabar yuborish", callback_data: "admin_broadcast" }],
    [{ text: "⚙️ Tarqatish majburiyligi", callback_data: "admin_share_condition" }],
  ]);
});
