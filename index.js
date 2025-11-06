const TelegramBot = require("node-telegram-bot-api");

// 🔑 BOT TOKEN — o‘zingizning tokeningizni yozing
const token = process.env.BOT_TOKEN || "7454675594:AAFywGrnS-9Qo7zeLYOSdhKi1zxP04O1qhg";

const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategik daromad bot ishga tushdi...");

// === /start komandasi ===
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;

  // 💬 Start xabari
  const message = `
💡 <b>Ushbu bot orqali o‘yinlarga strategiyalar va ishonchli maslahatlar oling!</b>  
💰 <b>Biz bilan birga daromadga chiqing.</b>

📈 <b>Daromad qilish yo‘lini tanlang:</b>
`;

  const options = {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          { text: "✈️ Aviator", callback_data: "aviator" },
          { text: "🍏 Apple of Fortune", callback_data: "apple" }
        ],
        [
          { text: "🐔 Chicken Road", callback_data: "chicken" },
          { text: "🎰 Kazinolar", callback_data: "casino" }
        ],
        [
          { text: "⚽ Sportga Stavka", callback_data: "sport" }
        ]
      ]
    }
  };

  await bot.sendMessage(chatId, message, options);
});

// === O'yin yo'nalishi tanlanganda ===
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  // O'yin tanlanganda — bukmekerni tanlash menyusi chiqadi
  const games = ["aviator", "apple", "chicken", "casino", "sport"];

  if (games.includes(data)) {
    await bot.sendMessage(
      chatId,
      `
🎯 <b>Kerakli bukmekerni tanlang:</b>
`,
      {
        parse_mode: "HTML",
        reply_markup: {
          inline_keyboard: [
            [
              { text: "💎 1xBet", callback_data: "1xbet" },
              { text: "🔥 Melbet", callback_data: "melbet" }
            ],
            [
              { text: "⚡ Winwin", callback_data: "winwin" },
              { text: "🏆 DBbet", callback_data: "dbbet" }
            ]
          ]
        }
      }
    );
    return;
  }

  // === Bukmeker tanlanganda ===
  const bookmakers = {
    "1xbet": "1xBet",
    "melbet": "Melbet",
    "winwin": "Winwin",
    "dbbet": "DBbet"
  };

  if (bookmakers[data]) {
    const bookmakerName = bookmakers[data];

    await bot.sendMessage(
      chatId,
      `
✅ <b>${bookmakerName}</b> bukmekerni tanladingiz!

💸 <b>AIFUT</b> promokod orqali ro‘yxatdan o‘ting va  
🎁 <b>200$ gacha bonus</b>ni qo‘lga kiriting!

📱 Boshlash uchun quyidagi havolani oching:
👉 <a href="https://t.me/aifutbot">t.me/aifutbot</a>
`,
      { parse_mode: "HTML", disable_web_page_preview: true }
    );

    return;
  }
});
