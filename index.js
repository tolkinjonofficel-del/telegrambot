const TelegramBot = require("node-telegram-bot-api");

// Railway yoki lokal uchun tokenni o'zgartirmasdan ishlatish
const token = process.env.BOT_TOKEN || "8114630640:AAE-VrMOvoe8M3IvlfNVU4Ge9IytJVbFZVA"; 

// polling: true -> botni doimiy ishlatadi
const bot = new TelegramBot(token, { polling: true });

console.log("✅ Strategik Bot ishga tushdi...");

// Start komandasi
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;

  const message = `
🎯 <b>Strategik bot bilan har kuni yangi yutuqlar!</b>

Har kuni ishonchli strategiyalar bilan yutib oling 💰
Tanlang — o‘zingizga yoqqan platforma 👇
`;

  const options = {
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [
        [
          { text: "💎 1xBet", url: "https://1xbet.com" },
          { text: "🔥 WinWin", url: "https://winwin.uz" }
        ],
        [
          { text: "⚽ MelBet", url: "https://melbet.com" },
          { text: "🏆 DBbet", url: "https://dbbet.com" }
        ],
        [
          { text: "💰 MegaPari", url: "https://megapari.com" }
        ]
      ]
    }
  };

  bot.sendMessage(chatId, message, options);
});

// Default javob
bot.on("message", (msg) => {
  if (!msg.text.startsWith("/start")) {
    bot.sendMessage(
      msg.chat.id,
      "⚡ /start buyrug‘ini yuboring va bugungi strategiyalarni ko‘ring!"
    );
  }
});
