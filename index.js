const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = "7454675594:AAFYU-QHScmLm_nykJi37eJwjSvSeRu33Nw"; // Tokeningizni kiriting
const ADMIN_ID = 7081746531; // Admin Telegram ID
const CHANNEL_LINK = "https://t.me/insayderai"; // Kanal havolasi

const bot = new TelegramBot(TOKEN, { polling: true });
console.log("✅ Sport Kupon Bot ishga tushdi...");

// === Kupon ma'lumotlari ===
let coupon = {
  title: "🎯 Bugungi AI Futbol Kuponi 🎯",
  text: `
<b>📅 07 Noyabr — Yevropa Ligasi</b>

⚽ <b>Aston Villa</b> vs <b>Makkabi</b>  
➡️ Tanlov: Aston Villa (-1.5)  
💸 Koef: 1.68  

⚽ <b>Boloniya</b> vs <b>Brann</b>  
➡️ Tanlov: 1-taymda Boloniya g‘alaba  
💸 Koef: 1.78  

⚽ <b>Braga</b> vs <b>Genk</b>  
➡️ Tanlov: Har ikkala taymda gol bo‘ladi  
💸 Koef: 1.64  

⚽ <b>Viktoriya P.</b> vs <b>Fenerbahçe</b>  
➡️ Tanlov: Uglavoylar jami <8.5  
💸 Koef: 1.63  

<b>🔥 Umumiy koeffitsient: 8.12</b>

🧠 Bu kupon sun’iy intellekt tahliliga asoslangan!
💰 Omad siz tomonda bo‘lsin!
`,
  requireShare: false,
};

const users = {};

// === Foydalanuvchiga xabar yuborish ===
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

  // Adminni xabardor qilish
  if (userId !== ADMIN_ID) {
    await bot.sendMessage(
      ADMIN_ID,
      `🧍‍♂️ <b>Yangi foydalanuvchi:</b>\n👤 ${username}\n🆔 ${userId}`,
      { parse_mode: "HTML" }
    );
  }

  const startText = `
⚽️ <b>Har kuni yangi futbol kuponlari!</b>

📊 Eng aniq AI tahlillar, 🎯 professional prognozlar va 💰 ishonchli kuponlar shu yerda.
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

  try {
    // === Kupon olish ===
    if (data === "get_coupon") {
      await bot.answerCallbackQuery(query.id, { text: "Kupon tayyorlanmoqda..." });

      await sendHtml(chatId, `${coupon.title}\n${coupon.text}`, [
        [{ text: "📨 Kuponni tarqatish", callback_data: "share_coupon" }],
      ]);
    }

    // === Kuponni tarqatish ===
    if (data === "share_coupon") {
      const botInfo = await bot.getMe();
      const shareText = encodeURIComponent(
        `🎯 Eng ishonchli futbol kuponlar!\nHar kuni yangi tahlillar bilan!\n👉 https://t.me/${botInfo.username}`
      );
      const shareUrl = `https://t.me/share/url?text=${shareText}`;
      await bot.answerCallbackQuery(query.id);
      await sendHtml(chatId, "📤 Kuponni do‘stlaringizga yuboring 👇", [
        [{ text: "🔗 Tarqatish havolasini ulashish", url: shareUrl }],
      ]);
    }

    // === ADMIN PANEL ===
    if (chatId === ADMIN_ID) {
      if (data === "admin_update_coupon") {
        await sendHtml(chatId, "📝 Yangi kupon matnini yuboring (HTML formatda).");
        bot.once("message", async (msg) => {
          coupon.text = msg.text;
          await sendHtml(chatId, "✅ Kupon yangilandi!");
        });
      }

      if (data === "admin_broadcast") {
        await sendHtml(chatId, "✉️ Foydalanuvchilarga yuboriladigan xabarni kiriting:");
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
  } catch (err) {
    console.error("❌ Xatolik:", err.message);
    await bot.sendMessage(chatId, "⚠️ Xatolik yuz berdi. Keyinroq urinib ko‘ring.");
  }
});

// === ADMIN PANEL KOMANDASI ===
bot.onText(/\/admin/, async (msg) => {
  if (msg.chat.id !== ADMIN_ID) return;
  await sendHtml(msg.chat.id, "🧩 <b>Admin panel:</b>", [
    [{ text: "🆕 Kupon matnini yangilash", callback_data: "admin_update_coupon" }],
    [{ text: "📨 Xabar yuborish", callback_data: "admin_broadcast" }],
  ]);
});
