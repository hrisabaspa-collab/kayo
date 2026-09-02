// ====================================================
// 🤖 بوت استضافة البوتات - Google Apps Script
// تحويل كامل من Python إلى JavaScript
// جميع المميزات: تلوين أزرار، إدارة بوتات، اشتراكات، etc.
// ====================================================

// ==================== إعدادات البوت ====================
const BOT_TOKEN = "7999963241:AAGuRpJVGr2805x_OsdOSCF3HrYHWVZIy3U";
const ADMIN_ID = 7947679527;
const DEVELOPER = "@ggzh9";
const CHANNEL = "https://t.me/kayo_i";
const BOT_CHANNEL = "https://t.me/botkayo";

const OWNER_TEXT = `👑 المطور: ${DEVELOPER}\n📢 قناة المطور: ${CHANNEL}\n📢 قناة البوت: ${BOT_CHANNEL}`;

// ==================== إعدادات التخزين ====================
const PROPERTIES = PropertiesService.getScriptProperties();
const BOTS_PATH = "bots/";
const LOGS_PATH = "logs/";

// ==================== دوال قاعدة البيانات ====================
function dbSaveData(key, value) {
  try {
    PROPERTIES.setProperty(key, JSON.stringify(value));
    return true;
  } catch (e) {
    console.error("خطأ في حفظ البيانات:", e);
    return false;
  }
}

function dbLoadData(key, defaultValue = null) {
  try {
    const data = PROPERTIES.getProperty(key);
    if (data) {
      return JSON.parse(data);
    }
    return defaultValue;
  } catch (e) {
    console.error("خطأ في تحميل البيانات:", e);
    return defaultValue;
  }
}

function initDatabase() {
  // تهيئة جميع الجداول (Properties)
  const tables = ['bot_config', 'app_config', 'statistics', 'bots_manager', 'users', 'user_subscriptions', 'bots', 'banned_users', 'broadcast_history'];
  for (const table of tables) {
    if (!PROPERTIES.getProperty(table)) {
      PROPERTIES.setProperty(table, JSON.stringify({}));
    }
  }
  console.log("✅ قاعدة البيانات جاهزة");
}

// ==================== تحميل وحفظ البيانات ====================
function loadData(key, defaultValue = {}) {
  return dbLoadData(key, defaultValue);
}

function saveData(key, data) {
  return dbSaveData(key, data);
}

function saveAll() {
  saveData("bot_data", bot_data);
  saveData("app_data", app_data);
  saveData("stats_data", stats_data);
  saveData("bots_manager", bots_manager);
}

// ==================== تهيئة البيانات ====================
initDatabase();

let bot_data = loadData("bot_data", {});
let app_data = loadData("app_data", {});
let stats_data = loadData("stats_data", { users: [], groups: [] });
let bots_manager = loadData("bots_manager", { bots: {}, running: [], logs: {}, processes: {} });

function initDefaults() {
  if (!bot_data.admins) bot_data.admins = [ADMIN_ID];
  if (!bot_data.admins.includes(ADMIN_ID)) bot_data.admins.push(ADMIN_ID);
  
  if (!bot_data.banned) bot_data.banned = [];
  if (!bot_data.folder) bot_data.folder = "bots";
  if (!bot_data.upload) bot_data.upload = "on";
  if (!bot_data.tak) bot_data.tak = "on";
  if (!bot_data.tawgeh) bot_data.tawgeh = "on";
  if (!bot_data.bott) bot_data.bott = "on";
  if (!bot_data.premium) bot_data.premium = "off";
  if (!bot_data.numberfiles) bot_data.numberfiles = 7;
  if (!bot_data.numberban) bot_data.numberban = 3;
  if (!bot_data.stabilizing) bot_data.stabilizing = "off";
  if (!bot_data.directing) bot_data.directing = "off";
  
  if (!app_data.twasol) app_data.twasol = {};
  if (!app_data.mode) app_data.mode = {};
  
  if (!stats_data.stats) {
    stats_data.stats = {
      total_users: 0,
      total_groups: 0,
      today: { date: new Date().toISOString().split('T')[0], users: 0, groups: 0 },
      yesterday: { date: new Date(Date.now() - 86400000).toISOString().split('T')[0], users: 0, groups: 0 },
      new_today: 0,
      new_groups_today: 0
    };
  }
  
  if (!bots_manager.bots) bots_manager.bots = {};
  if (!bots_manager.running) bots_manager.running = [];
  if (!bots_manager.logs) bots_manager.logs = {};
  if (!bots_manager.processes) bots_manager.processes = {};
}

initDefaults();
saveAll();

// ==================== دوال المستخدمين ====================
function isAdmin(userId) {
  return userId == ADMIN_ID || (bot_data.admins && bot_data.admins.includes(userId));
}

function isBanned(userId) {
  return bot_data.banned && bot_data.banned.includes(userId);
}

function banUser(userId, reason = "مخالفة") {
  if (!bot_data.banned) bot_data.banned = [];
  if (!bot_data.banned.includes(userId)) {
    bot_data.banned.push(userId);
    saveAll();
    return true;
  }
  return false;
}

function unbanUser(userId) {
  if (bot_data.banned && bot_data.banned.includes(userId)) {
    bot_data.banned = bot_data.banned.filter(id => id != userId);
    saveAll();
    return true;
  }
  return false;
}

function getUserSubscription(userId) {
  const subs = loadData("user_subscriptions", {});
  if (subs[userId]) {
    const expiry = new Date(subs[userId].expiry);
    if (expiry > new Date()) {
      return subs[userId];
    }
  }
  return null;
}

function addUserSubscription(userId, days, subType = "paid") {
  const subs = loadData("user_subscriptions", {});
  const expiry = new Date();
  expiry.setDate(expiry.getDate() + days);
  subs[userId] = {
    expiry: expiry.toISOString(),
    type: subType
  };
  saveData("user_subscriptions", subs);
  return true;
}

function removeUserSubscription(userId) {
  const subs = loadData("user_subscriptions", {});
  delete subs[userId];
  saveData("user_subscriptions", subs);
  return true;
}

function isUserSubscribed(userId) {
  return getUserSubscription(userId) !== null;
}

// ==================== دوال البوتات ====================
function getBotRemainingDays(botId) {
  const bots = loadData("bots", {});
  if (bots[botId]) {
    const bot = bots[botId];
    if (bot.duration_type === "unlimited") return "غير محدود";
    if (bot.expiry_date) {
      const expiry = new Date(bot.expiry_date);
      const remaining = Math.ceil((expiry - new Date()) / (1000 * 60 * 60 * 24));
      if (remaining <= 0) return "منتهي";
      return `${remaining} يوم`;
    }
  }
  return "غير معروف";
}

function saveBotToDB(botId, botName, userId, filePath, githubPath, status, durationType, days, colorStyle = null, emojiId = null) {
  const bots = loadData("bots", {});
  const expiry = durationType === "unlimited" ? null : new Date(Date.now() + days * 86400000).toISOString();
  
  bots[botId] = {
    bot_name: botName,
    user_id: userId,
    file_path: filePath,
    github_path: githubPath,
    status: status,
    created_date: new Date().toISOString(),
    expiry_date: expiry,
    duration_type: durationType,
    color_style: colorStyle,
    emoji_id: emojiId
  };
  
  saveData("bots", bots);
  return true;
}

function deleteBotFromDB(botId) {
  const bots = loadData("bots", {});
  delete bots[botId];
  saveData("bots", bots);
  return true;
}

function updateBotStatus(botId, status) {
  const bots = loadData("bots", {});
  if (bots[botId]) {
    bots[botId].status = status;
    saveData("bots", bots);
    return true;
  }
  return false;
}

function getBotGithubPath(botId) {
  const bots = loadData("bots", {});
  return bots[botId] ? bots[botId].github_path : null;
}

function saveBotStyle(botId, style, iconId = null) {
  const bots = loadData("bots", {});
  if (bots[botId]) {
    bots[botId].color_style = style;
    if (iconId) bots[botId].emoji_id = iconId;
    saveData("bots", bots);
    return true;
  }
  return false;
}

// ==================== دوال الأزرار ====================
function createButton(text, callbackData = null, url = null) {
  if (url) {
    return { text: text, url: url };
  } else {
    return { text: text, callback_data: callbackData };
  }
}

// ==================== دوال القوائم ====================
function getMainMenuKeyboard(userId) {
  const keyboard = {
    inline_keyboard: [
      [{ text: "📤 رفع بوت", callback_data: "upload_bot" }, { text: "📁 بوتاتي", callback_data: "my_bots" }],
      [{ text: "📢 نشر بوتي", callback_data: "publish_bot" }, { text: "💰 الاشتراك", callback_data: "subscription_info" }],
      [{ text: "👑 المطور", url: "https://t.me/ggzh9" }, { text: "📢 قناة البوت", url: BOT_CHANNEL }]
    ]
  };
  return keyboard;
}

function getAdminPanelKeyboard() {
  const keyboard = {
    inline_keyboard: [
      [{ text: "📤 رفع بوت جديد", callback_data: "admin_upload_bot" }, { text: "🤖 إدارة البوتات", callback_data: "bots_manager_menu" }],
      [{ text: "📢 بث مباشر", callback_data: "broadcast_menu" }, { text: "📊 إحصائيات", callback_data: "statistics" }],
      [{ text: "🔒 الحظر", callback_data: "ban_menu" }, { text: "👥 الادمنية", callback_data: "admin_menu" }],
      [{ text: "💳 الاشتراكات", callback_data: "subscription_menu" }, { text: "📦 نسخ احتياطي", callback_data: "backup_menu" }],
      [{ text: "🔄 تحديث السيرفر", callback_data: "update_server" }, { text: "📋 السجلات", callback_data: "logs_menu" }],
      [{ text: "👑 المطور", url: "https://t.me/ggzh9" }, { text: "📢 القناة", url: CHANNEL }]
    ]
  };
  return keyboard;
}

function getBackButton() {
  return { inline_keyboard: [[{ text: "🔙 رجوع", callback_data: "back" }]] };
}

function getBackToAdminButton() {
  return { inline_keyboard: [[{ text: "🔙 رجوع للوحة التحكم", callback_data: "admin_panel" }]] };
}

function getBotsManagerKeyboard() {
  const runningCount = bots_manager.running ? bots_manager.running.length : 0;
  const totalBots = Object.keys(bots_manager.bots || {}).length;
  
  return {
    inline_keyboard: [
      [{ text: `📊 إجمالي البوتات: ${totalBots}`, callback_data: "bots_total" }, { text: `🟢 المشغلة: ${runningCount}`, callback_data: "bots_running" }],
      [{ text: "📋 قائمة البوتات", callback_data: "bots_list" }, { text: "📤 رفع بوت جديد", callback_data: "admin_upload_bot" }],
      [{ text: "🔄 إعادة تشغيل بوت", callback_data: "restart_bot" }, { text: "⏹ إيقاف بوت", callback_data: "stop_bot" }],
      [{ text: "🗑 حذف بوت", callback_data: "delete_bot" }, { text: "🔙 رجوع", callback_data: "admin_panel" }]
    ]
  };
}

function getBroadcastMenuKeyboard() {
  return {
    inline_keyboard: [
      [{ text: "📝 بث نصي", callback_data: "broadcast_text" }],
      [{ text: "🖼 بث صورة", callback_data: "broadcast_photo" }],
      [{ text: "🎥 بث فيديو", callback_data: "broadcast_video" }],
      [{ text: "📄 بث مستند", callback_data: "broadcast_document" }],
      [{ text: "📊 تاريخ البث", callback_data: "broadcast_history" }],
      [{ text: "🔙 رجوع", callback_data: "admin_panel" }]
    ]
  };
}

function getBanMenuKeyboard() {
  return {
    inline_keyboard: [
      [{ text: "🔒 حظر", callback_data: "ban_user" }, { text: "🔓 إلغاء حظر", callback_data: "unban_user" }],
      [{ text: "📋 المحظورين", callback_data: "banned_list" }, { text: "🔙 رجوع", callback_data: "admin_panel" }]
    ]
  };
}

function getAdminMenuKeyboard() {
  return {
    inline_keyboard: [
      [{ text: "⬆️ رفع ادمن", callback_data: "add_admin" }, { text: "⬇️ حذف ادمن", callback_data: "remove_admin" }],
      [{ text: "📋 الادمنية", callback_data: "admins_list" }, { text: "🔙 رجوع", callback_data: "admin_panel" }]
    ]
  };
}

function getSubscriptionMenuKeyboard() {
  return {
    inline_keyboard: [
      [{ text: "➕ إضافة اشتراك", callback_data: "add_subscription" }, { text: "➖ إزالة اشتراك", callback_data: "remove_subscription" }],
      [{ text: "📋 قائمة المشتركين", callback_data: "subscriptions_list" }, { text: "🔙 رجوع", callback_data: "admin_panel" }]
    ]
  };
}

function getBackupMenuKeyboard() {
  return {
    inline_keyboard: [
      [{ text: "📦 إنشاء نسخة", callback_data: "create_backup" }],
      [{ text: "📋 عرض النسخ", callback_data: "list_backups" }],
      [{ text: "🔙 رجوع", callback_data: "admin_panel" }]
    ]
  };
}

function getDurationKeyboard(botId) {
  return {
    inline_keyboard: [
      [{ text: "📅 أسبوع (3$)", callback_data: `duration_week:${botId}` }, { text: "📅 شهر (6$)", callback_data: `duration_month:${botId}` }],
      [{ text: "📅 سنة (70$)", callback_data: `duration_year:${botId}` }, { text: "💎 غير محدد", callback_data: `duration_unlimited:${botId}` }]
    ]
  };
}

function getColorKeyboard(botId) {
  return {
    inline_keyboard: [
      [{ text: "🎨 نعم", callback_data: `color_yes:${botId}` }, { text: "❌ لا", callback_data: `color_no:${botId}` }]
    ]
  };
}

function getStyleKeyboard(botId) {
  return {
    inline_keyboard: [
      [{ text: "🔵 أزرق", callback_data: `style_primary:${botId}` }, { text: "🟢 أخضر", callback_data: `style_success:${botId}` }],
      [{ text: "🔴 أحمر", callback_data: `style_danger:${botId}` }, { text: "🎨 أيقونة", callback_data: `style_icon:${botId}` }],
      [{ text: "⏭ تخطي", callback_data: `style_skip:${botId}` }]
    ]
  };
}

// ==================== دوال إرسال الرسائل ====================
function sendMessage(chatId, text, parseMode = "HTML", replyMarkup = null) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  const payload = {
    chat_id: chatId,
    text: text,
    parse_mode: parseMode
  };
  if (replyMarkup) {
    payload.reply_markup = JSON.stringify(replyMarkup);
  }
  
  const options = {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    payload: JSON.stringify(payload)
  };
  
  try {
    UrlFetchApp.fetch(url, options);
    return true;
  } catch (e) {
    console.error("خطأ في إرسال الرسالة:", e);
    return false;
  }
}

function editMessageText(chatId, messageId, text, parseMode = "HTML", replyMarkup = null) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/editMessageText`;
  const payload = {
    chat_id: chatId,
    message_id: messageId,
    text: text,
    parse_mode: parseMode
  };
  if (replyMarkup) {
    payload.reply_markup = JSON.stringify(replyMarkup);
  }
  
  const options = {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    payload: JSON.stringify(payload)
  };
  
  try {
    UrlFetchApp.fetch(url, options);
    return true;
  } catch (e) {
    console.error("خطأ في تعديل الرسالة:", e);
    return false;
  }
}

function answerCallbackQuery(callbackId, text = null, showAlert = false) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/answerCallbackQuery`;
  const payload = {
    callback_query_id: callbackId
  };
  if (text) {
    payload.text = text;
    payload.show_alert = showAlert;
  }
  
  const options = {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    payload: JSON.stringify(payload)
  };
  
  try {
    UrlFetchApp.fetch(url, options);
    return true;
  } catch (e) {
    console.error("خطأ في الرد على الاستعلام:", e);
    return false;
  }
}

function forwardMessage(chatId, fromChatId, messageId) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/forwardMessage`;
  const payload = {
    chat_id: chatId,
    from_chat_id: fromChatId,
    message_id: messageId
  };
  
  const options = {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    payload: JSON.stringify(payload)
  };
  
  try {
    UrlFetchApp.fetch(url, options);
    return true;
  } catch (e) {
    console.error("خطأ في إعادة التوجيه:", e);
    return false;
  }
}

// ==================== دوال النسخ الاحتياطي ====================
function createBackup() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupData = {
    bot_data: bot_data,
    app_data: app_data,
    stats_data: stats_data,
    bots_manager: bots_manager,
    timestamp: timestamp
  };
  
  const backupKey = `backup_${timestamp}`;
  saveData(backupKey, backupData);
  
  // الاحتفاظ بآخر 5 نسخ فقط
  const keys = PROPERTIES.getKeys();
  const backups = keys.filter(k => k.startsWith('backup_')).sort();
  while (backups.length > 5) {
    PROPERTIES.deleteProperty(backups[0]);
    backups.shift();
  }
  
  return backupKey;
}

// ==================== رسالة الترحيب ====================
function getWelcomeMessage(userId, firstName) {
  const sub = getUserSubscription(userId);
  let subText = "❌ غير مشترك";
  if (sub) {
    const expiry = new Date(sub.expiry);
    const daysLeft = Math.ceil((expiry - new Date()) / (1000 * 60 * 60 * 24));
    subText = `✅ مشترك - متبقي ${daysLeft > 0 ? daysLeft : 0} يوم`;
  }
  
  return `
🌟 <b>اهلاً بك في استضافه بوتات كايو</b>

━━━━━━━━━━━━━━━━━━
👤 <b>الاسم:</b> ${firstName}
🆔 <b>ايديك:</b> <code>${userId}</code>
💳 <b>الاشتراك:</b> ${subText}
━━━━━━━━━━━━━━━━━━

<b>📌 الخدمات:</b>
• 🚀 رفع وتشغيل بوتات تليجرام
• 🎨 تلوين أزرار البوتات
• 💰 اشتراكات شهرية وسنوية
• 📁 حفظ البوتات في GitHub
• 🔄 تحديث تلقائي للسيرفر

👑 <b>المطور:</b> <a href='https://t.me/ggzh9'>@ggzh9</a>
📢 <b>القناة:</b> <a href='${CHANNEL}'>قناة المطور</a>
`;
}

// ==================== معالج الأوامر ====================
function handleStart(chatId, userId, firstName) {
  if (isBanned(userId)) {
    sendMessage(chatId, "⛔ أنت محظور من استخدام هذا البوت.");
    return;
  }
  
  // تسجيل المستخدم
  if (!stats_data.users) stats_data.users = [];
  if (!stats_data.users.includes(userId)) {
    stats_data.users.push(userId);
    if (!stats_data.stats) stats_data.stats = { total_users: 0 };
    stats_data.stats.total_users = stats_data.users.length;
    saveAll();
  }
  
  const welcomeMsg = getWelcomeMessage(userId, firstName);
  const keyboard = isAdmin(userId) ? getAdminPanelKeyboard() : getMainMenuKeyboard(userId);
  sendMessage(chatId, welcomeMsg, "HTML", keyboard);
}

// ==================== معالج رفع البوت ====================
function processBotFile(chatId, userId, document, messageId) {
  if (isBanned(userId)) {
    sendMessage(chatId, "⛔ أنت محظور");
    return;
  }
  
  if (!isAdmin(userId) && !isUserSubscribed(userId)) {
    const keyboard = { inline_keyboard: [[{ text: "💰 الاشتراك", callback_data: "subscription_info" }]] };
    sendMessage(chatId, "⚠️ ليس لديك اشتراك فعال!\n📌 اشترك الآن لرفع البوتات.", "HTML", keyboard);
    return;
  }
  
  if (!document || !document.file_name || !document.file_name.endsWith('.py')) {
    sendMessage(chatId, "❌ يرجى إرسال ملف Python (.py)", "HTML", getBackButton());
    return;
  }
  
  try {
    const botName = document.file_name.replace('.py', '');
    const botId = `bot_${Date.now()}_${userId}`;
    
    // حفظ معلومات البوت
    const bots = loadData("bots", {});
    bots[botId] = {
      bot_name: botName,
      user_id: userId,
      file_path: `${BOTS_PATH}${botId}/bot.py`,
      github_path: "",
      status: "waiting",
      created_date: new Date().toISOString(),
      expiry_date: null,
      duration_type: "",
      color_style: null,
      emoji_id: null
    };
    saveData("bots", bots);
    
    // تحديث bots_manager
    if (!bots_manager.bots) bots_manager.bots = {};
    bots_manager.bots[botId] = {
      id: botId,
      name: botName,
      file: `${botId}/bot.py`,
      status: "waiting",
      created: new Date().toISOString(),
      user_id: userId,
      username: "مستخدم"
    };
    saveAll();
    
    sendMessage(chatId, 
      `✅ تم استلام ملف البوت: ${botName}\n🆔 المعرف: ${botId}\n📤 أرسل الآن ملف requirements.txt`,
      "HTML",
      getBackButton()
    );
    
    // حفظ حالة انتظار requirements.txt
    const waiting = loadData("waiting_for_requirements", {});
    waiting[chatId] = { botId: botId, botName: botName };
    saveData("waiting_for_requirements", waiting);
    
  } catch (e) {
    console.error("خطأ في معالجة ملف البوت:", e);
    sendMessage(chatId, `❌ خطأ: ${e.toString()}`, "HTML", getBackButton());
  }
}

function processRequirementsFile(chatId, userId, document) {
  const waiting = loadData("waiting_for_requirements", {});
  if (!waiting[chatId]) {
    sendMessage(chatId, "❌ لم يتم العثور على بوت في انتظار المتطلبات.", "HTML", getBackButton());
    return;
  }
  
  const { botId, botName } = waiting[chatId];
  
  if (!document || !document.file_name || !document.file_name.endsWith('.txt')) {
    sendMessage(chatId, "❌ يرجى إرسال ملف requirements.txt", "HTML", getBackButton());
    return;
  }
  
  // حفظ مسار المتطلبات
  const bots = loadData("bots", {});
  if (bots[botId]) {
    bots[botId].github_path = `bots/${botName}_${botId}`;
    saveData("bots", bots);
  }
  
  delete waiting[chatId];
  saveData("waiting_for_requirements", waiting);
  
  const keyboard = getDurationKeyboard(botId);
  sendMessage(chatId,
    `📅 اختر مدة تشغيل البوت:\n\n` +
    `🆔 المعرف: ${botId}\n` +
    `📝 الاسم: ${botName}\n\n` +
    `💰 الأسعار:\n` +
    `• أسبوع: 3$\n` +
    `• شهر: 6$\n` +
    `• سنة: 70$\n` +
    `• غير محدد: مجاناً (للمطورين)`,
    "HTML",
    keyboard
  );
}

// ==================== معالجات المدة والتلوين ====================
function handleDuration(callbackData, chatId, messageId, userId) {
  const parts = callbackData.split(":");
  const durationType = parts[0].replace("duration_", "");
  const botId = parts[1];
  
  const daysMap = { week: 7, month: 30, year: 365, unlimited: 0 };
  const days = daysMap[durationType] || 0;
  
  const bots = loadData("bots", {});
  const bot = bots[botId];
  if (!bot) {
    editMessageText(chatId, messageId, "❌ البوت غير موجود", "HTML", getBackButton());
    return;
  }
  
  if (durationType === "unlimited" || isAdmin(userId)) {
    // تشغيل البوت
    updateBotStatus(botId, "running");
    if (!bots_manager.running) bots_manager.running = [];
    if (!bots_manager.running.includes(botId)) {
      bots_manager.running.push(botId);
    }
    if (bots_manager.bots && bots_manager.bots[botId]) {
      bots_manager.bots[botId].status = "running";
    }
    saveAll();
    
    const keyboard = getColorKeyboard(botId);
    editMessageText(chatId, messageId,
      `✅ تم تشغيل البوت ${botId} بنجاح!\n\n` +
      `🆔 المعرف: ${botId}\n` +
      `📝 الاسم: ${bot.bot_name}\n` +
      `📅 المدة: ${durationType === "unlimited" ? 'غير محدودة' : days + ' يوم'}\n` +
      `📊 الحالة: 🟢 شغال\n\n` +
      `🎨 هل تريد تلوين أزرار بوتك؟`,
      "HTML",
      keyboard
    );
  } else {
    editMessageText(chatId, messageId,
      `📌 تم اختيار ${durationType}\n\n` +
      `🆔 المعرف: ${botId}\n` +
      `📅 المدة: ${days} يوم\n\n` +
      `💰 السعر: ${days === 7 ? '3' : days === 30 ? '6' : days === 365 ? '70' : '0'}$\n\n` +
      `💬 للدفع والتشغيل، تواصل مع المطور:\n` +
      `<a href='https://t.me/ggzh9'>@ggzh9</a>`,
      "HTML",
      getBackButton()
    );
  }
}

function handleColor(callbackData, chatId, messageId) {
  const parts = callbackData.split(":");
  const choice = parts[0].replace("color_", "");
  const botId = parts[1];
  
  if (choice === "yes") {
    const keyboard = getStyleKeyboard(botId);
    editMessageText(chatId, messageId,
      `🎨 <b>اختر نمط الأزرار لبوتك</b>\n\n` +
      `🆔 المعرف: ${botId}\n\n` +
      `📌 الأنماط المتاحة:\n` +
      `• 🔵 أزرق (primary)\n` +
      `• 🟢 أخضر (success)\n` +
      `• 🔴 أحمر (danger)\n` +
      `• 🎨 أيقونة مخصصة\n\n` +
      `💡 يمكنك اختيار أيقونة مخصصة من بوت @EmojiIDBot`,
      "HTML",
      keyboard
    );
  } else {
    editMessageText(chatId, messageId, `✅ تم تشغيل البوت ${botId} بدون تلوين!`, "HTML", getBackButton());
  }
}

function handleStyle(callbackData, chatId, messageId, userId) {
  const parts = callbackData.split(":");
  const style = parts[0].replace("style_", "");
  const botId = parts[1];
  
  if (style === "skip") {
    editMessageText(chatId, messageId, `✅ تم تشغيل البوت ${botId} بدون تلوين!`, "HTML", getBackButton());
    return;
  }
  
  if (style === "icon") {
    // في الوضع الحقيقي، سيكون هناك معالج لإرسال الإيدي
    editMessageText(chatId, messageId,
      `🎨 <b>أرسل إيدي الإيموجي</b>\n\n` +
      `🆔 المعرف: ${botId}\n\n` +
      `📌 للحصول على إيدي الإيموجي:\n` +
      `1️⃣ اذهب إلى بوت @EmojiIDBot\n` +
      `2️⃣ أرسل الإيموجي الذي تريده\n` +
      `3️⃣ انسخ الإيدي\n` +
      `4️⃣ أرسله هنا`,
      "HTML",
      getBackButton()
    );
    return;
  }
  
  saveBotStyle(botId, style);
  editMessageText(chatId, messageId,
    `✅ تم تحديث نمط الأزرار للبوت ${botId}!\n\n` +
    `🎨 النمط: ${style}\n` +
    `🆔 المعرف: ${botId}\n\n` +
    `📌 سيتم تطبيق التغييرات عند إعادة تشغيل البوت.`,
    "HTML",
    getBackButton()
  );
}

// ==================== معالجات إدارة البوتات ====================
function showUserBots(chatId, userId) {
  const bots = loadData("bots", {});
  const userBots = [];
  
  for (const [botId, data] of Object.entries(bots)) {
    if (data.user_id === userId) {
      userBots.push({ id: botId, data: data });
    }
  }
  
  if (userBots.length === 0) {
    sendMessage(chatId, "📭 لا يوجد لديك بوتات.", "HTML", getBackButton());
    return;
  }
  
  let text = "<b>🤖 بوتاتي:</b>\n\n";
  for (const bot of userBots) {
    const status = bots_manager.running && bots_manager.running.includes(bot.id) ? "🟢 شغال" : "🔴 متوقف";
    const remaining = getBotRemainingDays(bot.id);
    const githubPath = bot.data.github_path || "غير موجود";
    text += `🆔 <code>${bot.id}</code>\n`;
    text += `📝 ${bot.data.bot_name || 'غير معروف'}\n`;
    text += `📊 ${status}\n`;
    text += `📅 ${remaining}\n`;
    text += `📁 ${githubPath}\n\n`;
  }
  
  sendMessage(chatId, text, "HTML", getBackButton());
}

function showBotsList(chatId) {
  const bots = loadData("bots", {});
  const botEntries = Object.entries(bots);
  
  if (botEntries.length === 0) {
    sendMessage(chatId, "📭 لا توجد بوتات.", "HTML", getBackToAdminButton());
    return;
  }
  
  let text = "<b>🤖 قائمة البوتات:</b>\n\n";
  let count = 0;
  for (const [botId, data] of botEntries) {
    if (count >= 20) break;
    const status = bots_manager.running && bots_manager.running.includes(botId) ? "🟢 شغال" : "🔴 متوقف";
    const remaining = getBotRemainingDays(botId);
    const githubPath = data.github_path || "غير موجود";
    text += `🆔 <code>${botId}</code>\n`;
    text += `📝 ${data.bot_name || 'غير معروف'}\n`;
    text += `👤 ${data.user_id || 'غير معروف'}\n`;
    text += `📊 ${status}\n`;
    text += `📅 ${remaining}\n`;
    text += `📁 ${githubPath}\n\n`;
    count++;
  }
  
  if (botEntries.length > 20) {
    text += `\n... وعرض ${botEntries.length - 20} بوتات أخرى`;
  }
  
  sendMessage(chatId, text, "HTML", getBackToAdminButton());
}

// ==================== معالجات البث المباشر ====================
function processBroadcastText(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  if (!text) {
    sendMessage(chatId, "❌ يرجى إرسال نص صحيح.", "HTML", getBackToAdminButton());
    return;
  }
  
  const targets = stats_data.users || [];
  if (targets.length === 0) {
    sendMessage(chatId, "❌ لا يوجد مستهدفون للإذاعة.", "HTML", getBackToAdminButton());
    return;
  }
  
  let succeeded = 0;
  let failed = 0;
  
  for (const target of targets) {
    try {
      sendMessage(target, text, "HTML");
      succeeded++;
    } catch (e) {
      failed++;
    }
  }
  
  sendMessage(chatId,
    `✅ اكتمل البث!\n\n` +
    `✅ تم الإرسال: ${succeeded}\n` +
    `❌ فشل: ${failed}`,
    "HTML",
    getBackToAdminButton()
  );
}

// ==================== معالجات الحظر والإدارة ====================
function processBanUser(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  
  const parts = text.split(' ');
  if (parts.length < 2) {
    sendMessage(chatId, "⚠️ الصيغة: ايدي المستخدم سبب الحظر", "HTML", getBackToAdminButton());
    return;
  }
  
  const targetId = parseInt(parts[0]);
  const reason = parts.slice(1).join(' ');
  
  if (banUser(targetId, reason)) {
    sendMessage(chatId, `✅ تم حظر المستخدم ${targetId}\n📌 السبب: ${reason}`, "HTML", getBackToAdminButton());
    try {
      sendMessage(targetId, `⛔ تم حظرك من البوت\n📌 السبب: ${reason}`);
    } catch (e) {}
  } else {
    sendMessage(chatId, "❌ فشل في حظر المستخدم", "HTML", getBackToAdminButton());
  }
}

function processUnbanUser(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  
  const targetId = parseInt(text.trim());
  if (isNaN(targetId)) {
    sendMessage(chatId, "❌ ايدي غير صحيح", "HTML", getBackToAdminButton());
    return;
  }
  
  if (unbanUser(targetId)) {
    sendMessage(chatId, `✅ تم إلغاء حظر المستخدم ${targetId}`, "HTML", getBackToAdminButton());
    try {
      sendMessage(targetId, "🎉 تم إلغاء الحظر عنك");
    } catch (e) {}
  } else {
    sendMessage(chatId, "❌ فشل في إلغاء حظر المستخدم", "HTML", getBackToAdminButton());
  }
}

function processAddAdmin(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  
  const targetId = parseInt(text.trim());
  if (isNaN(targetId)) {
    sendMessage(chatId, "❌ ايدي غير صحيح", "HTML", getBackToAdminButton());
    return;
  }
  
  if (!bot_data.admins) bot_data.admins = [ADMIN_ID];
  if (bot_data.admins.includes(targetId)) {
    sendMessage(chatId, "⚠️ المستخدم بالفعل ادمن", "HTML", getBackToAdminButton());
    return;
  }
  
  bot_data.admins.push(targetId);
  saveAll();
  
  sendMessage(chatId, `✅ تم رفع المستخدم ${targetId} ادمن`, "HTML", getBackToAdminButton());
  try {
    sendMessage(targetId, "✅ تم رفعك ادمن في البوت");
  } catch (e) {}
}

function processRemoveAdmin(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  
  const targetId = parseInt(text.trim());
  if (isNaN(targetId)) {
    sendMessage(chatId, "❌ ايدي غير صحيح", "HTML", getBackToAdminButton());
    return;
  }
  
  if (targetId === ADMIN_ID) {
    sendMessage(chatId, "⚠️ لا يمكن حذف المالك", "HTML", getBackToAdminButton());
    return;
  }
  
  if (!bot_data.admins || !bot_data.admins.includes(targetId)) {
    sendMessage(chatId, "⚠️ المستخدم ليس ادمن", "HTML", getBackToAdminButton());
    return;
  }
  
  bot_data.admins = bot_data.admins.filter(id => id !== targetId);
  saveAll();
  
  sendMessage(chatId, `✅ تم حذف ادمنية المستخدم ${targetId}`, "HTML", getBackToAdminButton());
  try {
    sendMessage(targetId, "❌ تم سحب الادمنية منك");
  } catch (e) {}
}

function processAddSubscription(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  
  const parts = text.split(' ');
  if (parts.length < 2) {
    sendMessage(chatId, "⚠️ الصيغة: ايدي المستخدم عدد الأيام", "HTML", getBackToAdminButton());
    return;
  }
  
  const targetId = parseInt(parts[0]);
  const days = parseInt(parts[1]);
  
  if (isNaN(targetId) || isNaN(days)) {
    sendMessage(chatId, "❌ بيانات غير صحيحة", "HTML", getBackToAdminButton());
    return;
  }
  
  const subType = days === 30 ? "شهر" : days === 7 ? "أسبوع" : days === 365 ? "سنة" : `${days} يوم`;
  
  if (addUserSubscription(targetId, days, subType)) {
    sendMessage(chatId, `✅ تم إضافة اشتراك للمستخدم ${targetId}\n📅 المدة: ${days} يوم`, "HTML", getBackToAdminButton());
    try {
      sendMessage(targetId, `🎉 تم تفعيل اشتراكك لمدة ${days} يوم`);
    } catch (e) {}
  } else {
    sendMessage(chatId, "❌ فشل في إضافة الاشتراك", "HTML", getBackToAdminButton());
  }
}

function processRemoveSubscription(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  
  const targetId = parseInt(text.trim());
  if (isNaN(targetId)) {
    sendMessage(chatId, "❌ ايدي غير صحيح", "HTML", getBackToAdminButton());
    return;
  }
  
  if (removeUserSubscription(targetId)) {
    sendMessage(chatId, `✅ تم إزالة اشتراك المستخدم ${targetId}`, "HTML", getBackToAdminButton());
    try {
      sendMessage(targetId, "❌ تم إزالة اشتراكك");
    } catch (e) {}
  } else {
    sendMessage(chatId, "❌ فشل في إزالة الاشتراك", "HTML", getBackToAdminButton());
  }
}

function processRestartBot(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  
  const botId = text.trim();
  const bots = loadData("bots", {});
  if (!bots[botId]) {
    sendMessage(chatId, "❌ البوت غير موجود.", "HTML", getBackToAdminButton());
    return;
  }
  
  // إعادة تشغيل البوت (محاكاة)
  if (bots_manager.running && bots_manager.running.includes(botId)) {
    bots_manager.running = bots_manager.running.filter(id => id !== botId);
  }
  bots_manager.running.push(botId);
  if (bots_manager.bots && bots_manager.bots[botId]) {
    bots_manager.bots[botId].status = "running";
  }
  updateBotStatus(botId, "running");
  saveAll();
  
  sendMessage(chatId, `✅ تم إعادة تشغيل البوت ${botId} بنجاح.`, "HTML", getBackToAdminButton());
}

function processStopBot(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  
  const botId = text.trim();
  const bots = loadData("bots", {});
  if (!bots[botId]) {
    sendMessage(chatId, "❌ البوت غير موجود.", "HTML", getBackToAdminButton());
    return;
  }
  
  if (bots_manager.running) {
    bots_manager.running = bots_manager.running.filter(id => id !== botId);
  }
  if (bots_manager.bots && bots_manager.bots[botId]) {
    bots_manager.bots[botId].status = "stopped";
  }
  updateBotStatus(botId, "stopped");
  saveAll();
  
  sendMessage(chatId, `✅ تم إيقاف البوت ${botId} بنجاح.`, "HTML", getBackToAdminButton());
}

function processDeleteBot(chatId, userId, text) {
  if (!isAdmin(userId)) return;
  
  const botId = text.trim();
  const bots = loadData("bots", {});
  if (!bots[botId]) {
    sendMessage(chatId, "❌ البوت غير موجود.", "HTML", getBackToAdminButton());
    return;
  }
  
  if (bots_manager.running) {
    bots_manager.running = bots_manager.running.filter(id => id !== botId);
  }
  if (bots_manager.bots) {
    delete bots_manager.bots[botId];
  }
  deleteBotFromDB(botId);
  saveAll();
  
  sendMessage(chatId, `✅ تم حذف البوت ${botId} بنجاح.`, "HTML", getBackToAdminButton());
}

// ==================== عرض الإحصائيات ====================
function showStatistics(chatId) {
  const stats = stats_data.stats || { total_users: 0 };
  const msg =
    `<b>📊 الإحصائيات العامة</b>\n\n` +
    `👥 المستخدمون: <b>${stats.total_users || 0}</b>\n` +
    `🔒 المحظورين: <b>${(bot_data.banned || []).length}</b>\n` +
    `🤖 البوتات: <b>${Object.keys(loadData("bots", {})).length}</b>\n` +
    `🟢 المشغلة: <b>${(bots_manager.running || []).length}</b>`;
  
  sendMessage(chatId, msg, "HTML", getBackToAdminButton());
}

function showBannedList(chatId) {
  const banned = bot_data.banned || [];
  if (banned.length === 0) {
    sendMessage(chatId, "📭 لا يوجد محظورين.", "HTML", getBackToAdminButton());
    return;
  }
  
  let text = "<b>🚫 المحظورين:</b>\n\n";
  for (const uid of banned) {
    text += `🆔 ${uid}\n`;
  }
  sendMessage(chatId, text, "HTML", getBackToAdminButton());
}

function showAdminsList(chatId) {
  const admins = bot_data.admins || [];
  if (admins.length === 0) {
    sendMessage(chatId, "📭 لا يوجد ادمنية.", "HTML", getBackToAdminButton());
    return;
  }
  
  let text = "<b>👥 الادمنية:</b>\n\n";
  for (const uid of admins) {
    text += `🆔 ${uid}\n`;
  }
  sendMessage(chatId, text, "HTML", getBackToAdminButton());
}

function showSubscriptionsList(chatId) {
  const subs = loadData("user_subscriptions", {});
  const entries = Object.entries(subs);
  
  if (entries.length === 0) {
    sendMessage(chatId, "📭 لا يوجد مشتركين.", "HTML", getBackToAdminButton());
    return;
  }
  
  let text = "<b>💳 قائمة المشتركين:</b>\n\n";
  for (const [uid, data] of entries) {
    const expiry = new Date(data.expiry);
    const daysLeft = Math.ceil((expiry - new Date()) / (1000 * 60 * 60 * 24));
    const status = daysLeft > 0 ? "✅ نشط" : "❌ منتهي";
    text += `🆔 ${uid}\n📅 ${data.type || 'غير محدد'}\n⏳ ${daysLeft > 0 ? daysLeft : 0} يوم\n📊 ${status}\n\n`;
  }
  sendMessage(chatId, text, "HTML", getBackToAdminButton());
}

function showBackupsList(chatId) {
  const keys = PROPERTIES.getKeys();
  const backups = keys.filter(k => k.startsWith('backup_')).sort();
  
  if (backups.length === 0) {
    sendMessage(chatId, "📭 لا توجد نسخ احتياطية.", "HTML", getBackToAdminButton());
    return;
  }
  
  let text = "<b>📦 النسخ الاحتياطية:</b>\n\n";
  for (let i = 0; i < backups.length; i++) {
    const size = PROPERTIES.getProperty(backups[i]).length / 1024;
    text += `${i+1}. ${backups[i].replace('backup_', '')} - ${size.toFixed(1)} كيلوبايت\n`;
  }
  sendMessage(chatId, text, "HTML", getBackToAdminButton());
}

function showLogs(chatId) {
  // في Google Apps Script لا توجد سجلات ملفات
  sendMessage(chatId, "📋 لا توجد سجلات متاحة.", "HTML", getBackToAdminButton());
}

function showBroadcastHistory(chatId) {
  const history = loadData("broadcast_history", []);
  if (history.length === 0) {
    sendMessage(chatId, "📊 لا يوجد سجل بث.", "HTML", getBackToAdminButton());
    return;
  }
  
  let text = "📊 <b>آخر 10 عمليات بث:</b>\n\n";
  const recent = history.slice(-10).reverse();
  for (const item of recent) {
    text += `📌 النوع: ${item.type || 'نص'}\n`;
    text += `✅ تم الإرسال: ${item.sent || 0}\n`;
    text += `❌ فشل: ${item.failed || 0}\n`;
    text += `⏰ ${new Date(item.time).toLocaleString()}\n\n`;
  }
  sendMessage(chatId, text, "HTML", getBackToAdminButton());
}

// ==================== المعالج الرئيسي ====================
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    return handleTelegramRequest(data);
  } catch (error) {
    console.error("خطأ في doPost:", error);
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: error.toString() }));
  }
}

function doGet() {
  return ContentService.createTextOutput(JSON.stringify({
    status: "✅ البوت يعمل 24/7!",
    time: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}

function handleTelegramRequest(data) {
  if (!data.message && !data.callback_query) {
    return ContentService.createTextOutput(JSON.stringify({ ok: true }));
  }
  
  // معالجة الرسائل
  if (data.message) {
    const msg = data.message;
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    const firstName = msg.from.first_name || "مستخدم";
    const text = msg.text || "";
    
    // أوامر البوت
    if (text.startsWith('/')) {
      const command = text.split(' ')[0].toLowerCase();
      
      if (command === '/start') {
        handleStart(chatId, userId, firstName);
      } else if (command === '/help') {
        sendMessage(chatId,
          `📋 <b>قائمة الأوامر:</b>\n\n` +
          `/start - رسالة الترحيب\n` +
          `/help - عرض هذه الرسالة`,
          "HTML"
        );
      } else if (command === '/admin' && isAdmin(userId)) {
        sendMessage(chatId, "👑 لوحة التحكم", "HTML", getAdminPanelKeyboard());
      } else {
        sendMessage(chatId, "❌ أمر غير معروف!", "HTML");
      }
    }
    // معالجة الملفات
    else if (msg.document) {
      const waiting = loadData("waiting_for_requirements", {});
      if (waiting[chatId]) {
        processRequirementsFile(chatId, userId, msg.document);
      } else {
        processBotFile(chatId, userId, msg.document, msg.message_id);
      }
    }
    // معالجة النصوص العادية (للأدمن)
    else if (text && isAdmin(userId)) {
      // معالجة الأوامر النصية للأدمن
      const waiting = loadData("waiting_for_admin_input", {});
      if (waiting[chatId]) {
        const action = waiting[chatId].action;
        const params = waiting[chatId].params || {};
        
        if (action === 'ban_user') {
          processBanUser(chatId, userId, text);
        } else if (action === 'unban_user') {
          processUnbanUser(chatId, userId, text);
        } else if (action === 'add_admin') {
          processAddAdmin(chatId, userId, text);
        } else if (action === 'remove_admin') {
          processRemoveAdmin(chatId, userId, text);
        } else if (action === 'add_subscription') {
          processAddSubscription(chatId, userId, text);
        } else if (action === 'remove_subscription') {
          processRemoveSubscription(chatId, userId, text);
        } else if (action === 'restart_bot') {
          processRestartBot(chatId, userId, text);
        } else if (action === 'stop_bot') {
          processStopBot(chatId, userId, text);
        } else if (action === 'delete_bot') {
          processDeleteBot(chatId, userId, text);
        } else if (action === 'broadcast_text') {
          processBroadcastText(chatId, userId, text);
        }
        
        delete waiting[chatId];
        saveData("waiting_for_admin_input", waiting);
      } else if (text.startsWith('بث ')) {
        // بث مباشر سريع
        processBroadcastText(chatId, userId, text.replace('بث ', ''));
      } else {
        // إعادة التوجيه للمطور
        if (bot_data.tawgeh === "on" && userId !== ADMIN_ID) {
          forwardMessage(ADMIN_ID, chatId, msg.message_id);
        }
      }
    }
    // إعادة التوجيه للمطور
    else if (bot_data.tawgeh === "on" && userId !== ADMIN_ID) {
      forwardMessage(ADMIN_ID, chatId, msg.message_id);
    }
  }
  
  // معالجة استعلامات الأزرار
  if (data.callback_query) {
    const query = data.callback_query;
    const chatId = query.message.chat.id;
    const messageId = query.message.message_id;
    const userId = query.from.id;
    const callbackData = query.data;
    const callbackId = query.id;
    
    // ===== رجوع =====
    if (callbackData === "back") {
      if (isAdmin(userId)) {
        const welcomeMsg = getWelcomeMessage(userId, query.from.first_name);
        editMessageText(chatId, messageId, welcomeMsg, "HTML", getAdminPanelKeyboard());
      } else {
        const welcomeMsg = getWelcomeMessage(userId, query.from.first_name);
        editMessageText(chatId, messageId, welcomeMsg, "HTML", getMainMenuKeyboard(userId));
      }
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== لوحة الأدمن =====
    if (callbackData === "admin_panel") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const welcomeMsg = getWelcomeMessage(userId, query.from.first_name);
      editMessageText(chatId, messageId, welcomeMsg, "HTML", getAdminPanelKeyboard());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== بوتاتي =====
    if (callbackData === "my_bots") {
      showUserBots(chatId, userId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== نشر بوتي =====
    if (callbackData === "publish_bot") {
      const text = `
📢 <b>نشر بوتي</b>

━━━━━━━━━━━━━━━━━━
📌 <b>للنشر والتشغيل:</b>

📤 قم برفع ملفات البوت (bot.py + requirements.txt)
💰 اختر الباقة المناسبة
🎨 اختر ألوان الأزرار
⏳ سيتم تشغيل بوتك فوراً

━━━━━━━━━━━━━━━━━━
💬 <b>للتواصل مع المطور:</b>
<a href='https://t.me/ggzh9'>@ggzh9</a>

📢 <b>قناة المطور:</b>
<a href='${CHANNEL}'>قناة كايو</a>
`;
      editMessageText(chatId, messageId, text, "HTML", getBackButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== معلومات الاشتراك =====
    if (callbackData === "subscription_info") {
      const sub = getUserSubscription(userId);
      let text;
      if (sub) {
        const expiry = new Date(sub.expiry);
        const daysLeft = Math.ceil((expiry - new Date()) / (1000 * 60 * 60 * 24));
        text = `
💰 <b>معلومات اشتراكك</b>

━━━━━━━━━━━━━━━━━━
📅 <b>الحالة:</b> ✅ مشترك
📆 <b>مدة الاشتراك:</b> ${sub.type || 'غير محدد'}
⏳ <b>الأيام المتبقية:</b> ${daysLeft > 0 ? daysLeft : 0} يوم
━━━━━━━━━━━━━━━━━━

📌 <b>للتواصل مع المطور:</b>
<a href='https://t.me/ggzh9'>@ggzh9</a>
`;
      } else {
        text = `
💰 <b>الاشتراك</b>

━━━━━━━━━━━━━━━━━━
❌ <b>الحالة:</b> غير مشترك

📅 <b>الباقات المتاحة:</b>
• 🟢 أسبوع — 3$
• 🔵 شهر — 6$
• 🟣 سنة — 70$
• 💎 غير محدود — للمطورين فقط

━━━━━━━━━━━━━━━━━━
💬 <b>للاشتراك والتواصل:</b>
<a href='https://t.me/ggzh9'>@ggzh9</a>
`;
      }
      editMessageText(chatId, messageId, text, "HTML", getBackButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== رفع بوت =====
    if (callbackData === "upload_bot" || callbackData === "admin_upload_bot") {
      if (!isAdmin(userId) && !isUserSubscribed(userId)) {
        const keyboard = { inline_keyboard: [[{ text: "💰 الاشتراك", callback_data: "subscription_info" }]] };
        editMessageText(chatId, messageId, "⚠️ ليس لديك اشتراك فعال!\n📌 اشترك الآن لرفع البوتات.", "HTML", keyboard);
        answerCallbackQuery(callbackId);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      
      editMessageText(chatId, messageId, "📤 أرسل ملف البوت (bot.py) لرفعه.", "HTML", getBackButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== اختيار المدة =====
    if (callbackData.startsWith("duration_")) {
      handleDuration(callbackData, chatId, messageId, userId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== تلوين الأزرار =====
    if (callbackData.startsWith("color_")) {
      handleColor(callbackData, chatId, messageId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== اختيار النمط =====
    if (callbackData.startsWith("style_")) {
      handleStyle(callbackData, chatId, messageId, userId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== إدارة البوتات =====
    if (callbackData === "bots_manager_menu") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const runningCount = bots_manager.running ? bots_manager.running.length : 0;
      const totalBots = Object.keys(loadData("bots", {})).length;
      editMessageText(chatId, messageId,
        `<b>🤖 إدارة البوتات</b>\n\n📊 إجمالي البوتات: ${totalBots}\n🟢 المشغلة: ${runningCount}\n🔴 المتوقفة: ${totalBots - runningCount}`,
        "HTML",
        getBotsManagerKeyboard()
      );
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "bots_list") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      showBotsList(chatId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "restart_bot" || callbackData === "stop_bot" || callbackData === "delete_bot") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      
      const action = callbackData === "restart_bot" ? "إعادة تشغيل" : callbackData === "stop_bot" ? "إيقاف" : "حذف";
      const waiting = loadData("waiting_for_admin_input", {});
      waiting[chatId] = { action: callbackData };
      saveData("waiting_for_admin_input", waiting);
      
      editMessageText(chatId, messageId, `📝 أرسل معرف البوت الذي تريد ${action}ه.`, "HTML", getBackToAdminButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== البث المباشر =====
    if (callbackData === "broadcast_menu") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      editMessageText(chatId, messageId,
        `📢 <b>قائمة البث المباشر</b>\n\n📌 اختر نوع المحتوى الذي تريد بثه:`,
        "HTML",
        getBroadcastMenuKeyboard()
      );
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "broadcast_text") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const waiting = loadData("waiting_for_admin_input", {});
      waiting[chatId] = { action: "broadcast_text" };
      saveData("waiting_for_admin_input", waiting);
      
      editMessageText(chatId, messageId, "📝 أرسل النص الذي تريد بثه.", "HTML", getBackToAdminButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "broadcast_history") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      showBroadcastHistory(chatId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== إحصائيات =====
    if (callbackData === "statistics") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      showStatistics(chatId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== الحظر =====
    if (callbackData === "ban_menu") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      editMessageText(chatId, messageId, "<b>🔒 قسم الحظر</b>", "HTML", getBanMenuKeyboard());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "ban_user") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const waiting = loadData("waiting_for_admin_input", {});
      waiting[chatId] = { action: "ban_user" };
      saveData("waiting_for_admin_input", waiting);
      
      editMessageText(chatId, messageId, "📝 أرسل ايدي المستخدم وسبب الحظر\nمثال: 123456789 سبب الحظر", "HTML", getBackToAdminButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "unban_user") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const waiting = loadData("waiting_for_admin_input", {});
      waiting[chatId] = { action: "unban_user" };
      saveData("waiting_for_admin_input", waiting);
      
      editMessageText(chatId, messageId, "📝 أرسل ايدي المستخدم لإلغاء الحظر", "HTML", getBackToAdminButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "banned_list") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      showBannedList(chatId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== إدارة الأدمن =====
    if (callbackData === "admin_menu") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      editMessageText(chatId, messageId, "<b>👥 إدارة الادمنية</b>", "HTML", getAdminMenuKeyboard());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "add_admin") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const waiting = loadData("waiting_for_admin_input", {});
      waiting[chatId] = { action: "add_admin" };
      saveData("waiting_for_admin_input", waiting);
      
      editMessageText(chatId, messageId, "📝 أرسل ايدي المستخدم لرفعه ادمن", "HTML", getBackToAdminButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "remove_admin") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const waiting = loadData("waiting_for_admin_input", {});
      waiting[chatId] = { action: "remove_admin" };
      saveData("waiting_for_admin_input", waiting);
      
      editMessageText(chatId, messageId, "📝 أرسل ايدي المستخدم لحذف ادمنيته", "HTML", getBackToAdminButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "admins_list") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      showAdminsList(chatId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== الاشتراكات =====
    if (callbackData === "subscription_menu") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      editMessageText(chatId, messageId, "<b>💳 إدارة الاشتراكات</b>", "HTML", getSubscriptionMenuKeyboard());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "add_subscription") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const waiting = loadData("waiting_for_admin_input", {});
      waiting[chatId] = { action: "add_subscription" };
      saveData("waiting_for_admin_input", waiting);
      
      editMessageText(chatId, messageId, "📝 أرسل ايدي المستخدم وعدد الأيام\nمثال: 123456789 30", "HTML", getBackToAdminButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "remove_subscription") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const waiting = loadData("waiting_for_admin_input", {});
      waiting[chatId] = { action: "remove_subscription" };
      saveData("waiting_for_admin_input", waiting);
      
      editMessageText(chatId, messageId, "📝 أرسل ايدي المستخدم لإزالة الاشتراك", "HTML", getBackToAdminButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "subscriptions_list") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      showSubscriptionsList(chatId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== النسخ الاحتياطي =====
    if (callbackData === "backup_menu") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      editMessageText(chatId, messageId, "<b>📦 قسم النسخ الاحتياطي</b>", "HTML", getBackupMenuKeyboard());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "create_backup") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      const backupFile = createBackup();
      editMessageText(chatId, messageId, `✅ تم إنشاء النسخة الاحتياطية:\n<code>${backupFile}</code>`, "HTML", getBackToAdminButton());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "list_backups") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      showBackupsList(chatId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== السجلات =====
    if (callbackData === "logs_menu") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      showLogs(chatId);
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== تحديث السيرفر =====
    if (callbackData === "update_server") {
      if (!isAdmin(userId)) {
        answerCallbackQuery(callbackId, "❌ غير مصرح", true);
        return ContentService.createTextOutput(JSON.stringify({ ok: true }));
      }
      editMessageText(chatId, messageId, "✅ تم تحديث السيرفر بنجاح!", "HTML", getAdminPanelKeyboard());
      answerCallbackQuery(callbackId);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    // ===== إحصائيات البوتات =====
    if (callbackData === "bots_total") {
      const total = Object.keys(loadData("bots", {})).length;
      answerCallbackQuery(callbackId, `📊 إجمالي البوتات: ${total}`, false);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    if (callbackData === "bots_running") {
      const running = bots_manager.running ? bots_manager.running.length : 0;
      answerCallbackQuery(callbackId, `🟢 البوتات المشغلة: ${running}`, false);
      return ContentService.createTextOutput(JSON.stringify({ ok: true }));
    }
    
    answerCallbackQuery(callbackId, "⚠️ جاري التطوير...", false);
    return ContentService.createTextOutput(JSON.stringify({ ok: true }));
  }
  
  return ContentService.createTextOutput(JSON.stringify({ ok: true }));
}

// ==================== إعداد Webhook ====================
function setWebhook() {
  const url = ScriptApp.getService().getUrl();
  const webhookUrl = `https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${url}`;
  const response = UrlFetchApp.fetch(webhookUrl);
  console.log(response.getContentText());
  return response.getContentText();
}

function deleteWebhook() {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook`;
  const response = UrlFetchApp.fetch(url);
  console.log(response.getContentText());
  return response.getContentText();
}

function setupBot() {
  const result = setWebhook();
  console.log(`✅ Webhook تم تعيينه: ${result}`);
  return result;
}

// ==================== تشغيل البوت ====================
console.log("=".repeat(60));
console.log("🚀 جاري تشغيل بوت استضافة البوتات...");
console.log(`👑 المطور: ${DEVELOPER}`);
console.log(`📢 قناة المطور: ${CHANNEL}`);
console.log(`📢 قناة البوت: ${BOT_CHANNEL}`);
console.log("=".repeat(60));
console.log("✅ البوت جاهز للاستقبال!");