const TelegramBot = require("node-telegram-bot-api");

// Railway yoki lokal token (BotFather’dan olingan)
const token = process.env.BOT_TOKEN || "8320792971:AAG6APrNu2wJgYSJreRPYkGjpt3o5JEeWYM";
const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategiya sinov bot ishga tushdi...");

// --- /start komandasi ---
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;

  const message = `
✨ <b>Xush kelibsiz! O'yin strategiyalari botiga!</b> ✨

🎮 <b>Bot imkoniyatlari:</b>
• 🎯 Ishonchli platformalar  
• 💰 Samarali strategiyalar  
• 🚀 Tez daromad olish  
• 📊 Professional ko'rsatkichlar  

💎 Pul ko'paytirish uchun kerakli platformani tanlang:
`;

  const options = {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          { text: "💎 1xBet", callback_data: "1xbet" }
        ]
      ]
    }
  };

  bot.sendMessage(chatId, message, options);
});


// --- 1xBet tugmasi bosilganda ---
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  if (data === "1xbet") {
    const imageUrl = "https://t.me/insayderAI/665";
    const apkUrl = "https://t.me/upaymeuz/3542";

    const caption = `
*🎰 1xBet platformasi tanlandi!* ✅

Royhatdan o'tish uchun:
📱 Android: <a href="${apkUrl}">APK yuklab oling</a>  
📱 iPhone: Havola tez orada joylanadi  

Botni faollashtirish uchun <b>"AIFUT"</b> promokodini yozing va uni ro'yhatdan o'tishda kiriting! 👆✅
`;

    // Rasm yuborish
    await bot.sendPhoto(chatId, imageUrl, {
      caption: caption,
      parse_mode: "HTML"
    });

    // Keyingi xabar — o'yinlar tanlash
    await bot.sendMessage(chatId, `
💰 <b>Daromad olish uchun qaysi o'yinni o'ynashni tanlaysiz?</b>

📊 <b>1xBet haqida:</b>
• 🎯 Ishonchlilik: 98%  
• ⚡ Tezkorlik: A+  
• 💰 Bonus: 150% gacha  
• 📱 Qulaylik: Mobil optimallashtirilgan  

❗️ AIFUT promokodini ro'yhatdan o'tishda kiriting — shunda aniq signallar olasiz.
`, {
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [
            { text: "🍏 Apple of Fortune", url: "https://t.me/AiFUTbot" },
            { text: "✈️ Aviator", url: "https://t.me/AiFUTbot" }
          ],
          [
            { text: "⚽ Penalty", url: "https://t.me/AiFUTbot" },
            { text: "🚀 JetX", url: "https://t.me/AiFUTbot" }
          ]
        ]
      }
    });
  }
});
