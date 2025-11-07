const TelegramBot = require("node-telegram-bot-api");

// === Sozlamalar ===
const TOKEN = "7454675594:AAE5Obhl2WUxIMYpbw7o31QArwxZr7DQYck";
const ADMIN_ID = 7081746531;
const CHANNEL_LINK = "https://t.me/insayderai";

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
➡️ <i>Tanlov:</i> Uglavoylar jami &lt;8.5  
💸 <i>Koef:</i> 1.63  

🔥 <b>Umumiy koeffitsient:</b> 8.12  

🧠 Bu kupon <b>AI tahlili</b> asosida tuzilgan!  
💰 Omad siz tomonda bo‘lsin!`,
};

// === Tizim sozlamalari ===
let requireReferrals = true; // Majburiy tarqatish yoqilganmi
let requiredCount = 5; // Kupon olish uchun necha odam taklif qilish kerak

// === Foydalanuvchilar bazasi ===
// { userId: { referrals: Set([...]), invitedBy: userId } }
const users = {};

// === Yordamchi funksiya ===
async function sendHtml(chatId, text, buttons = null) {
    const opts = { parse_mode: "HTML" };
    if (buttons) opts.reply_markup = { inline_keyboard: buttons };
    return bot.sendMessage(chatId, text, opts);
}

// === START komandasi ===
bot.onText(/\/start(?:\s+(\d+))?/, async (msg, match) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    const referrerId = match[1];
    const username = msg.from.username ? `@${msg.from.username}` : msg.from.first_name;

    // Foydalanuvchini bazaga kiritish
    if (!users[userId]) users[userId] = { referrals: new Set(), invitedBy: referrerId || null };

    // === REFERAL TIZIMI ===
    if (referrerId && referrerId !== String(userId)) {
        if (!users[referrerId]) users[referrerId] = { referrals: new Set() };
        const referrer = users[referrerId];

        if (!referrer.referrals.has(userId)) {
            referrer.referrals.add(userId);

            const total = referrer.referrals.size;
            const remaining = Math.max(requiredCount - total, 0);

            // Har yangi foydalanuvchi qo‘shilganda referalga habar yuboriladi
            if (total < requiredCount) {
                await sendHtml(
                    referrerId,
                    `👤 <b>1 ta yangi do‘st qo‘shildi!</b>\nSizda hozirda <b>${total}</b> ta taklif mavjud.\nYana <b>${remaining}</b> ta do‘st taklif qilsangiz — kupon sizga yuboriladi 🎯`
                );
            }

            // Agar kerakli son to‘ldi
            if (total >= requiredCount) {
                await sendHtml(
                    referrerId,
                    `🎉 <b>Tabriklaymiz!</b> Siz ${requiredCount} ta do‘stni taklif qildingiz!\nQuyidagi kupon sizga taqdim etiladi:\n\n${coupon.title}\n\n${coupon.text}`
                );
            }
        }
    }

    // Adminni yangi foydalanuvchidan xabardor qilish
    if (userId !== ADMIN_ID) {
        await sendHtml(ADMIN_ID, `🧍‍♂️ Yangi foydalanuvchi: ${username}\n🆔 ${userId}`);
    }

    // Foydalanuvchi uchun menyu
    await sendHtml(
        chatId,
        `
⚽️ <b>Har kuni yangi futbol kuponlari!</b>

📊 Eng aniq AI tahlillar, 🎯 professional prognozlar  
va 💰 ishonchli kuponlar shu yerda.`,
        [
            [{ text: "📢 Kanalga a’zo bo‘lish", url: CHANNEL_LINK }],
            [{ text: "🎁 Bugungi kuponni olish", callback_data: "get_coupon" }],
        ]
    );
});

// === CALLBACKLAR ===
bot.on("callback_query", async (query) => {
    const chatId = query.message.chat.id;
    const userId = chatId;
    const data = query.data;

    try {
        if (data === "get_coupon") {
            await bot.answerCallbackQuery(query.id);

            // === Agar majburiy tarqatish o‘chirilgan bo‘lsa, kuponni darhol yuborish ===
            if (!requireReferrals) {
                return sendHtml(chatId, `${coupon.title}\n\n${coupon.text}`, [
                    [{ text: "📨 Kuponni tarqatish", callback_data: "share_coupon" }],
                ]);
            }

            // === Referral havolasi yaratish ===
            const botInfo = await bot.getMe();
            const referralLink = `https://t.me/${botInfo.username}?start=${userId}`;
            const total = users[userId]?.referrals?.size || 0;
            const remaining = Math.max(requiredCount - total, 0);

            if (total >= requiredCount) {
                return sendHtml(chatId, `${coupon.title}\n\n${coupon.text}`);
            } else {
                await sendHtml(
                    chatId,
                    `📢 Kuponni olish uchun <b>${requiredCount}</b> ta do‘stni taklif qiling!\nSizda hozirda <b>${total}</b> ta taklif bor.\nYana <b>${remaining}</b> ta do‘st kerak 👇`,
                    [
                        [
                            {
                                text: "📨 Do‘stni taklif qilish",
                                url: `https://t.me/share/url?url=${referralLink}&text=🎯 Eng ishonchli kuponlarni shu botdan ol!`,
                            },
                        ],
                    ]
                );
            }
        }

        if (data === "share_coupon") {
            const botInfo = await bot.getMe();
            const shareUrl = `https://t.me/share/url?text=🎯 Eng ishonchli futbol kuponlar! 👉 https://t.me/${botInfo.username}`;
            await bot.answerCallbackQuery(query.id);
            await sendHtml(chatId, "📤 Kuponni do‘stlaringizga yuboring 👇", [
                [{ text: "🔗 Tarqatish havolasi", url: shareUrl }],
            ]);
        }

        // === ADMIN PANEL ===
        if (chatId === ADMIN_ID) {
            if (data === "admin_update_coupon") {
                await sendHtml(chatId, "📝 Yangi kupon matnini yuboring (HTML formatda):");
                bot.once("message", async (msg) => {
                    coupon.text = msg.text;
                    await sendHtml(chatId, "✅ Kupon yangilandi!");
                });
            }

            if (data === "admin_broadcast") {
                await sendHtml(chatId, "✉️ Xabar yuborish:");
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

            if (data === "admin_toggle_ref") {
                requireReferrals = !requireReferrals;
                await sendHtml(
                    chatId,
                    requireReferrals
                        ? "✅ Majburiy tarqatish yoqildi."
                        : "❌ Majburiy tarqatish o‘chirildi."
                );
            }

            if (data === "admin_set_refcount") {
                await sendHtml(chatId, "🔢 Kupon olish uchun kerakli do‘stlar sonini kiriting:");
                bot.once("message", async (msg) => {
                    const num = parseInt(msg.text);
                    if (!isNaN(num) && num > 0) {
                        requiredCount = num;
                        await sendHtml(chatId, `✅ Endi kupon olish uchun ${requiredCount} ta do‘st kerak.`);
                    } else {
                        await sendHtml(chatId, "⚠️ Noto‘g‘ri qiymat!");
                    }
                });
            }
        }
    } catch (err) {
        console.error("❌ Xatolik:", err.message);
    }
});

// === ADMIN PANEL KOMANDASI ===
bot.onText(/\/admin/, async (msg) => {
    if (msg.chat.id !== ADMIN_ID) return;
    await sendHtml(msg.chat.id, "🧩 <b>Admin panel:</b>", [
        [{ text: "🆕 Kupon yangilash", callback_data: "admin_update_coupon" }],
        [{ text: "📨 Xabar yuborish", callback_data: "admin_broadcast" }],
        [{ text: "⚙️ Majburiy tarqatish ON/OFF", callback_data: "admin_toggle_ref" }],
        [{ text: "🔢 Taklif sonini o‘zgartirish", callback_data: "admin_set_refcount" }],
    ]);
});
