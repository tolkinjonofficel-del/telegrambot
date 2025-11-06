const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = process.env.BOT_TOKEN || "7454675594:AAFYU-QHScmLm_nykJi37eJwjSvSeRu33Nw";
const ADMIN_ID = 7081746531;
const CHANNEL_ID = -1002296703235; // 👈 kanal ID ni shu yerga yozing (yoki @username)
const CHANNEL_LINK = "https://t.me/insayderai";

const bot = new TelegramBot(TOKEN, { polling: true });

// === Boshlang‘ich sozlamalar ===
let coupon = {
  title: "Bugungi AI kuponi",
  text: `
⚽ Aston Villa vs Makkabi — Aston Villa (-1.5) (1.68 KF)
⚽ Boloniya vs Brann — 1-taym Boloniya (1.78 KF)
⚽ Braga vs Genk — Har ikkala taymda gol (1.64 KF)
⚽ Viktoriya P. vs Fenerbahçe — Uglavoylar <8.5 (1.63 KF)
<b>UMUMIY KOEFF: 8.12</b>`,
  image: "https://www.pymnts.com/wp-content/uploads/2024/04/Meta-AI-tech.png?w=457"
};

console.log("✅ Kupon bot ishga tushdi...");

async function sendHtml(chatId, text, buttons = null) {
  const options = { parse_mode: "HTML" };
  if (buttons) options.reply_markup = { inline_keyboard: buttons };
  return bot.sendMessage(chatId, text, options);
}

// === START komandasi ===
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  if (userId !== ADMIN_ID) {
    await bot.sendMessage(
      ADMIN_ID,
      `🧍‍♂️ Yangi foydalanuvchi: ${msg.from.first_name} (ID: ${userId})`
    );
  }

  await sendHtml(
    chatId,
    `
⚽️ <b>Har kuni yangi futbol kuponlari!</b>

📊 <b>Professional tahlil</b>, 🎯 <b>aniq prognoz</b> va 💰 <b>ishonchli kuponlar</b> shu yerda.
`,
    [
      [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
      [{ text: "🎁 Bugungi kuponni olish", callback_data: "get_coupon" }]
    ]
  );
});

// === CALLBACK ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  await bot.answerCallbackQuery(query.id);

  if (data === "get_coupon") {
    try {
      // 🧠 Kanal obuna holatini tekshiramiz
      const member = await bot.getChatMember(CHANNEL_ID, chatId);
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

      // ✅ Agar a’zo bo‘lsa — kupon yuboriladi
      await bot.sendPhoto(chatId, coupon.image, {
        caption: `<b>${coupon.title}</b>\n\n${coupon.text}`,
        parse_mode: "HTML",
        reply_markup: {
          inline_keyboard: [
            [{ text: "📨 Kuponni tarqatish", callback_data: "share_coupon" }]
          ]
        }
      });
    } catch (err) {
      console.error("❌ Obuna tekshirish xatosi:", err.message);

      // ⚠️ Agar bot kanalga kira olmasa yoki ruxsatsiz bo‘lsa
      await sendHtml(
        chatId,
        `⚠️ Obuna holatini aniqlab bo‘lmadi.\nBot kanalga admin sifatida qo‘shilganligini tekshiring.`,
        [[{ text: "📢 Kanalga o‘tish", url: CHANNEL_LINK }]]
      );
    }
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
