const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = "7454675594:AAFYU-QHScmLm_nykJi37eJwjSvSeRu33Nw"; // Tokeningizni shu yerga yozing
const ADMIN_ID = 7081746531; // O'zingizning Telegram ID
const CHANNEL_LINK = "https://t.me/insayderai"; // Kanal havolasi

const bot = new TelegramBot(TOKEN, { polling: true });
console.log("✅ Kupon bot ishga tushdi...");

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
};

// === Foydalanuvchilar bazasi (RAM ichida) ===
const users = {};

// === Yordamchi funksiya ===
function sendHtml(chatId, text, buttons = null) {
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

  // Adminga yangi foydalanuvchi haqida xabar
  if (userId !== ADMIN_ID) {
    await bot.sendMessage(
      ADMIN_ID,
      `🧍‍♂️ <b>Yangi foydalanuvchi qo‘shildi:</b>\n👤 ${username}\n🆔 ${userId}`,
      { parse_mode: "HTML" }
    );
  }

  const startText = `
⚽️ <b>Har kuni yangi futbol kuponlari!</b>

📊 Professional tahlil, 🎯 aniq prognoz va 💰 ishonchli kuponlar shu yerda.
`;

  await sendHtml(chatId, startText, [
    [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
    [{ text: "🎁 Bugungi kuponni olish", callback_data: "get_coupon" }],
  ]);
});

// === CALLBACKLAR ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  // Kupon olish
  if (data === "get_coupon") {
    try {
      await bot.answerCallbackQuery(query.id, { text: "Kupon yuklanmoqda..." });

      await bot.sendPhoto(chatId, coupon.image, {
        caption: `<b>${coupon.title}</b>\n\n${coupon.text}`,
        parse_mode: "HTML",
        reply_markup: {
          inline_keyboard: [
            [{ text: "📨 Kuponni tarqatish", callback_data: "share_coupon" }],
          ],
        },
      });
    } catch (err) {
      console.error("❌ Kupon yuborishda xato:", err.message);
      await bot.sendMessage(chatId, "⚠️ Kuponni yuborishda xatolik yuz berdi. Keyinroq urinib ko‘ring.");
    }
  }

  // Kuponni tarqatish
  if (data === "share_coupon") {
    try {
      const botInfo = await bot.getMe();
      const shareText = encodeURIComponent(
        `🎯 Eng ishonchli futbol kuponlar!\nHar kuni yangi tahlillar bilan!\n👉 https://t.me/${botInfo.username}`
      );
      const shareUrl = `https://t.me/share/url?text=${shareText}`;
      await bot.answerCallbackQuery(query.id);
      await sendHtml(chatId, "📤 Kuponni do‘stlaringizga yuboring 👇", [
        [{ text: "🔗 Tarqatish havolasini ulashish", url: shareUrl }],
      ]);
    } catch (err) {
      console.error("❌ Share xatosi:", err.message);
    }
  }

  // === ADMIN PANEL BOSHQARUVI ===
  if (chatId === ADMIN_ID) {
    if (data === "admin_update_coupon") {
      await sendHtml(chatId, "📝 Kupon matnini yuboring (rasm bilan yoki rasm holda):");
      bot.once("message", async (msg) => {
        try {
          if (msg.photo) {
            const photoId = msg.photo[msg.photo.length - 1].file_id;
            coupon.image = photoId;
            coupon.text = msg.caption || coupon.text;
          } else {
            coupon.text = msg.text;
          }
          await sendHtml(chatId, "✅ Kupon yangilandi!");
        } catch (err) {
          console.error("Kupon yangilash xatosi:", err.message);
        }
      });
    }

    if (data === "admin_share_condition") {
      await sendHtml(chatId, "⚙️ Tarqatish majburiy bo‘lsinmi? (ha/yo‘q)");
      bot.once("message", async (msg) => {
        const answer = msg.text.toLowerCase();
        coupon.requireShare = answer.startsWith("ha");
        await sendHtml(
          chatId,
          coupon.requireShare
            ? "✅ Tarqatish majburiy qilib qo‘yildi."
            : "❌ Endi kupon olish erkin."
        );
      });
    }

    if (data === "admin_broadcast") {
      await sendHtml(chatId, "✉️ Foydalanuvchilarga yuboriladigan xabarni yozing:");
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
  }
});

// === ADMIN PANEL ===
bot.onText(/\/admin/, async (msg) => {
  if (msg.chat.id !== ADMIN_ID) return;
  await sendHtml(msg.chat.id, "🧩 <b>Admin panel:</b>", [
    [{ text: "🆕 Kupon qo‘shish / yangilash", callback_data: "admin_update_coupon" }],
    [{ text: "📨 Xabar yuborish", callback_data: "admin_broadcast" }],
    [{ text: "⚙️ Tarqatish majburiyligi", callback_data: "admin_share_condition" }],
  ]);
});
