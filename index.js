const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = "7454675594:AAFYU-QHScmLm_nykJi37eJwjSvSeRu33Nw"; // Bot tokeningiz
const ADMIN_ID = 7081746531; // Sizning Telegram ID
const CHANNEL_LINK = "https://t.me/insayderai"; // Kanal havolasi

// === Botni ishga tushiramiz ===
const bot = new TelegramBot(TOKEN, { polling: true });
console.log("✅ Kupon bot ishga tushdi...");

// === Kupon ma'lumotlari ===
let coupon = {
  title: "🎯 Bugungi AI Futbol Kuponi 🎯",
  text: `
📅 <b>07 Noyabr — Yevropa Ligasi</b>

⚽ <b>Aston Villa</b> vs <b>Makkabi</b>  
➡️ <i>Tanlov:</i> Aston Villa (-1.5)  
💸 <i>Koef:</i> 1.68  

⚽ <b>Boloniya</b> vs <b>Brann</b>  
➡️ <i>Tanlov:</i> 1-taymda Boloniya g‘alaba  
💸 <i>Koef:</i> 1.78  

⚽ <b>Braga</b> vs <b>Genk</b>  
➡️ <i>Tanlov:</i> Har ikkala taymda gol bo‘ladi  
💸 <i>Koef:</i> 1.64  

⚽ <b>Viktoriya P.</b> vs <b>Fenerbahçe</b>  
➡️ <i>Tanlov:</i> Uglavoylar jami <8.5  
💸 <i>Koef:</i> 1.63  

🔥 <b>Umumiy koeffitsient:</b> 8.12  

🧠 Bu kupon <b>AI tahlili</b> asosida tuzilgan!  
💰 Omad siz tomonda bo‘lsin!`,
};

// === Foydalanuvchilar bazasi (xotirada) ===
const users = {};

// === Xabar yuborish uchun yordamchi ===
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

  // Foydalanuvchini ro‘yxatga olish
  if (!users[userId]) users[userId] = { username };

  // Adminga yangi foydalanuvchi haqida xabar
  if (userId !== ADMIN_ID) {
    await bot.sendMessage(
      ADMIN_ID,
      `🧍‍♂️ <b>Yangi foydalanuvchi qo‘shildi:</b>\n👤 ${username}\n🆔 ${userId}`,
      { parse_mode: "HTML" }
    );
  }

  // Foydalanuvchiga menyu yuborish
  const welcomeText = `
⚽️ <b>Har kuni yangi futbol kuponlari!</b>

📊 Eng aniq AI tahlillar, 🎯 professional prognozlar  
va 💰 ishonchli kuponlar shu yerda.`;

  const buttons = [
    [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
    [{ text: "🎁 Bugungi kuponni olish", callback_data: "get_coupon" }],
  ];

  await sendHtml(chatId, welcomeText, buttons);
});

// === CALLBACKLAR ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  try {
    // === Kupon olish ===
    if (data === "get_coupon") {
      await bot.answerCallbackQuery(query.id, { text: "Kupon tayyorlanmoqda..." });

      await sendHtml(
        chatId,
        `${coupon.title}\n\n${coupon.text}`,
        [[{ text: "📨 Kuponni tarqatish", callback_data: "share_coupon" }]]
      );
    }

    // === Kuponni tarqatish ===
    if (data === "share_coupon") {
      const botInfo = await bot.getMe();
      const shareText = encodeURIComponent(
        `🎯 Eng ishonchli futbol kuponlar! Har kuni yangi tahlillar bilan!\n👉 https://t.me/${botInfo.username}`
      );
      const shareUrl = `https://t.me/share/url?text=${shareText}`;
      await bot.answerCallbackQuery(query.id);
      await sendHtml(chatId, "📤 Kuponni do‘stlaringizga yuboring 👇", [
        [{ text: "🔗 Tarqatish havolasini ulashish", url: shareUrl }],
      ]);
    }

    // === ADMIN PANEL ===
    if (chatId === ADMIN_ID) {
      // Kuponni yangilash
      if (data === "admin_update_coupon") {
        await sendHtml(chatId, "📝 Yangi kupon matnini kiriting (HTML formatda):");
        bot.once("message", async (msg) => {
          coupon.text = msg.text;
          await sendHtml(chatId, "✅ Kupon yangilandi!");
        });
      }

      // Xabar yuborish
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
  } catch (err) {
    console.error("❌ Xatolik:", err.message);
    await sendHtml(chatId, "⚠️ Xatolik yuz berdi. Keyinroq urinib ko‘ring.");
  }
});

// === ADMIN PANEL KOMANDASI ===
bot.onText(/\/admin/, async (msg) => {
  if (msg.chat.id !== ADMIN_ID) return;
  await sendHtml(msg.chat.id, "🧩 <b>Admin panel:</b>", [
    [{ text: "🆕 Kuponni yangilash", callback_data: "admin_update_coupon" }],
    [{ text: "📨 Xabar yuborish", callback_data: "admin_broadcast" }],
  ]);
});
