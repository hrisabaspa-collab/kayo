# bot.py - النسخة المحدثة بالكامل
import telebot
import requests
import json
import os
import re
import shutil
import time
import subprocess
import sys
import signal
import hashlib
import sqlite3
import threading
import base64
import zipfile
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from github import Github
import logging

# ==================== إعدادات التسجيل ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== الإعدادات الأساسية ====================
API_TOKEN = "7999963241:AAH57nQ23f0XSS2cFbcrEDm8yty5ZrglGkw"
ADMIN_ID = 7947679527
DEVELOPER = "@ggzh9"
CHANNEL = "https://t.me/kayo_i"
BOT_CHANNEL = "https://t.me/botkayo"

GITHUB_TOKEN = "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"
GITHUB_REPO = "yesssssssie-debug/bot-kayo"

OWNER_TEXT = f"""👑 المطور: {DEVELOPER}
📢 قناة المطور: {CHANNEL}
📢 قناة البوت: {BOT_CHANNEL}"""

# ==================== أسعار الاشتراك بالنجوم ====================
PRICES = {
    "يوم": 10,
    "اسبوع": 50,
    "شهر": 600
}

bot = telebot.TeleBot(API_TOKEN)

# ==================== إعدادات المسارات ====================
DATA_PATH = "data/"
BACKUP_PATH = "backups/"
BOTS_PATH = "bots/"
FILES_PATH = "files/"
LOGS_PATH = "logs/"
TEMP_PATH = "temp/"
BACKUP_ZIP_PATH = "backup_zips/"

for path in [DATA_PATH, BACKUP_PATH, BOTS_PATH, FILES_PATH, LOGS_PATH, TEMP_PATH, BACKUP_ZIP_PATH]:
    os.makedirs(path, exist_ok=True)

# ==================== قاعدة البيانات ====================
DB_PATH = "bot_data.db"

def init_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS bot_config (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS app_config (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS statistics (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bots_manager (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, join_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_subscriptions (user_id INTEGER PRIMARY KEY, expiry_date TEXT, subscription_type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bots (bot_id TEXT PRIMARY KEY, bot_name TEXT, user_id INTEGER, file_path TEXT, github_path TEXT, status TEXT, created_date TEXT, expiry_date TEXT, duration_type TEXT, color_style TEXT, emoji_id TEXT, star_cost INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS banned_users (user_id INTEGER PRIMARY KEY, reason TEXT, ban_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS broadcast_history (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER, content_type TEXT, content TEXT, sent_count INTEGER, failed_count INTEGER, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS star_transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount INTEGER, type TEXT, description TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pending_payments (user_id INTEGER PRIMARY KEY, bot_id TEXT, stars INTEGER, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bot_access_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id TEXT, user_id INTEGER, action TEXT, created_at TEXT)''')
    
    conn.commit()
    conn.close()
    logger.info("✅ قاعدة البيانات جاهزة")

def db_save_data(table: str, key: str, value: Any):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(f"REPLACE INTO {table} (key, value) VALUES (?, ?)", (key, json.dumps(value, ensure_ascii=False)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في حفظ البيانات: {e}")
        return False

def db_load_data(table: str, key: str, default: Any = None) -> Any:
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(f"SELECT value FROM {table} WHERE key = ?", (key,))
        result = c.fetchone()
        conn.close()
        if result:
            return json.loads(result[0])
        return default
    except:
        return default

# ==================== دوال GitHub المتقدمة ====================
def create_github_folder(folder_path: str):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        file_path = f"{folder_path}/.keep"
        content = "# هذا المجلد مخصص للبوتات المرفوعة"
        encoded = base64.b64encode(content.encode()).decode()
        try:
            repo.create_file(file_path, f"إنشاء مجلد {folder_path}", encoded, branch="main")
        except:
            pass
        return True
    except Exception as e:
        logger.error(f"خطأ في إنشاء المجلد: {e}")
        return False

def upload_file_to_github(file_path: str, github_path: str, commit_message: str = "رفع ملف"):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        with open(file_path, "rb") as f:
            content = f.read()
        encoded_content = base64.b64encode(content).decode("utf-8")
        try:
            contents = repo.get_contents(github_path)
            repo.update_file(github_path, commit_message, encoded_content, contents.sha, branch="main")
        except:
            repo.create_file(github_path, commit_message, encoded_content, branch="main")
        return True
    except Exception as e:
        logger.error(f"خطأ في رفع الملف: {e}")
        return False

def delete_file_from_github(github_path: str, commit_message: str = "حذف ملف"):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        try:
            contents = repo.get_contents(github_path)
            repo.delete_file(github_path, commit_message, contents.sha, branch="main")
            return True
        except:
            return True
    except Exception as e:
        logger.error(f"خطأ في حذف الملف: {e}")
        return False

def delete_folder_from_github(folder_path: str, commit_message: str = "حذف مجلد"):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        try:
            contents = repo.get_contents(folder_path)
            for content in contents:
                repo.delete_file(content.path, commit_message, content.sha, branch="main")
            return True
        except:
            return True
    except Exception as e:
        logger.error(f"خطأ في حذف المجلد: {e}")
        return False

def upload_bot_to_github(bot_folder: str, bot_name: str, bot_id: str):
    try:
        github_folder = f"bots/{bot_name}_{bot_id}"
        create_github_folder(github_folder)
        
        bot_file = os.path.join(bot_folder, "bot.py")
        if os.path.exists(bot_file):
            upload_file_to_github(bot_file, f"{github_folder}/bot.py", f"رفع بوت {bot_name}")
        
        req_file = os.path.join(bot_folder, "requirements.txt")
        if os.path.exists(req_file):
            upload_file_to_github(req_file, f"{github_folder}/requirements.txt", f"رفع متطلبات {bot_name}")
        
        logger.info(f"✅ تم رفع البوت {bot_id} إلى GitHub: {github_folder}")
        return github_folder
    except Exception as e:
        logger.error(f"خطأ في رفع البوت إلى GitHub: {e}")
        return None

def delete_bot_from_github(bot_id: str, github_path: str):
    try:
        if github_path:
            delete_folder_from_github(github_path, f"حذف بوت {bot_id}")
            logger.info(f"✅ تم حذف البوت {bot_id} من GitHub")
            return True
        return False
    except Exception as e:
        logger.error(f"خطأ في حذف البوت من GitHub: {e}")
        return False

def trigger_auto_deploy():
    """تحديث السيرفر تلقائياً عبر GitHub"""
    try:
        file_path = os.path.join(TEMP_PATH, "deploy_trigger.txt")
        with open(file_path, "w") as f:
            f.write(f"تحديث تلقائي - {datetime.now().isoformat()}")
        
        upload_file_to_github(file_path, "deploy_trigger.txt", "تحديث تلقائي للسيرفر")
        os.remove(file_path)
        logger.info("✅ تم تحديث السيرفر تلقائياً")
        return True
    except Exception as e:
        logger.error(f"خطأ في تحديث السيرفر: {e}")
        return False

# ==================== دوال المستخدمين والاشتراكات ====================
def get_user_subscription(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT expiry_date, subscription_type FROM user_subscriptions WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        if result:
            return {"expiry": datetime.fromisoformat(result[0]), "type": result[1]}
        return None
    except:
        return None

def add_user_subscription(user_id: int, days: int, sub_type: str = "paid"):
    try:
        expiry = (datetime.now() + timedelta(days=days)).isoformat()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("REPLACE INTO user_subscriptions (user_id, expiry_date, subscription_type) VALUES (?, ?, ?)",
                  (user_id, expiry, sub_type))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def remove_user_subscription(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM user_subscriptions WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def is_user_subscribed(user_id: int) -> bool:
    sub = get_user_subscription(user_id)
    if not sub:
        return False
    return sub["expiry"] > datetime.now()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def is_banned(user_id: int) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT 1 FROM banned_users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result is not None
    except:
        return False

def ban_user(user_id: int, reason: str = "مخالفة"):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO banned_users (user_id, reason, ban_date) VALUES (?, ?, ?)",
                  (user_id, reason, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def unban_user(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM banned_users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ==================== دوال معاملات النجوم ====================
def add_star_transaction(user_id: int, amount: int, trans_type: str, description: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO star_transactions (user_id, amount, type, description, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
                  (user_id, amount, trans_type, description))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_star_transactions(user_id: int, limit: int = 10):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM star_transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
        results = c.fetchall()
        conn.close()
        return results
    except:
        return []

def add_pending_payment(user_id: int, bot_id: str, stars: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("REPLACE INTO pending_payments (user_id, bot_id, stars, created_at) VALUES (?, ?, ?, ?)",
                  (user_id, bot_id, stars, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_pending_payment(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT bot_id, stars FROM pending_payments WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        if result:
            return {"bot_id": result[0], "stars": result[1]}
        return None
    except:
        return None

def remove_pending_payment(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM pending_payments WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def log_bot_access(bot_id: str, user_id: int, action: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO bot_access_logs (bot_id, user_id, action, created_at) VALUES (?, ?, ?, ?)",
                  (bot_id, user_id, action, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ==================== دوال البوتات ====================
def save_bot_to_db(bot_id: str, bot_name: str, user_id: int, file_path: str, github_path: str, status: str, duration_type: str, days: int, color_style: str = None, emoji_id: str = None, star_cost: int = 0):
    try:
        if duration_type == "unlimited":
            expiry_date = None
        else:
            expiry_date = (datetime.now() + timedelta(days=days)).isoformat()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""REPLACE INTO bots (bot_id, bot_name, user_id, file_path, github_path, status, created_date, expiry_date, duration_type, color_style, emoji_id, star_cost) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (bot_id, bot_name, user_id, file_path, github_path, status, datetime.now().isoformat(), expiry_date, duration_type, color_style, emoji_id, star_cost))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_bot_from_db(bot_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM bots WHERE bot_id = ?", (bot_id,))
        result = c.fetchone()
        conn.close()
        return result
    except:
        return None

def delete_bot_from_db(bot_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM bots WHERE bot_id = ?", (bot_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def update_bot_status(bot_id: str, status: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE bots SET status = ? WHERE bot_id = ?", (status, bot_id))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_bot_github_path(bot_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT github_path FROM bots WHERE bot_id = ?", (bot_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def get_bot_remaining_days(bot_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT expiry_date, duration_type FROM bots WHERE bot_id = ?", (bot_id,))
        result = c.fetchone()
        conn.close()
        if not result:
            return "غير معروف"
        expiry_date, duration_type = result
        if duration_type == "unlimited":
            return "غير محدود"
        if expiry_date:
            expiry = datetime.fromisoformat(expiry_date)
            remaining = (expiry - datetime.now()).days
            if remaining <= 0:
                return "منتهي"
            return f"{remaining} يوم"
        return "غير معروف"
    except:
        return "غير معروف"

def get_bot_owner(bot_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM bots WHERE bot_id = ?", (bot_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def check_expired_bots():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("SELECT bot_id, github_path FROM bots WHERE expiry_date IS NOT NULL AND expiry_date < ? AND status = 'running'", (now,))
        expired = c.fetchall()
        conn.close()
        
        for bot in expired:
            bot_id = bot[0]
            github_path = bot[1]
            
            stop_bot_process(bot_id)
            update_bot_status(bot_id, "expired")
            
            if github_path:
                delete_bot_from_github(bot_id, github_path)
            
            bot_folder = os.path.join(BOTS_PATH, bot_id)
            if os.path.exists(bot_folder):
                shutil.rmtree(bot_folder)
            
            logger.info(f"⏹ تم إيقاف وحذف البوت {bot_id} بسبب انتهاء الصلاحية")
            trigger_auto_deploy()
        
        return len(expired)
    except Exception as e:
        logger.error(f"خطأ في التحقق من البوتات المنتهية: {e}")
        return 0

# ==================== تحميل وحفظ البيانات ====================
def load_data(file_name: str, default: dict = None) -> dict:
    table_map = {"bot.json": "bot_config", "app.json": "app_config", "statistics.json": "statistics", "bots_manager.json": "bots_manager"}
    table = table_map.get(file_name, "bot_config")
    key = file_name.replace(".json", "")
    return db_load_data(table, key, default or {})

def save_data(file_name: str, data: dict):
    table_map = {"bot.json": "bot_config", "app.json": "app_config", "statistics.json": "statistics", "bots_manager.json": "bots_manager"}
    table = table_map.get(file_name, "bot_config")
    key = file_name.replace(".json", "")
    db_save_data(table, key, data)

def save_all():
    global bot_data, app_data, stats_data, bots_manager
    save_data("bot.json", bot_data)
    save_data("app.json", app_data)
    save_data("statistics.json", stats_data)
    save_data("bots_manager.json", bots_manager)

# ==================== تهيئة البيانات ====================
init_database()

bot_data = load_data("bot.json", {})
app_data = load_data("app.json", {})
stats_data = load_data("statistics.json", {"users": [], "groups": []})
bots_manager = load_data("bots_manager.json", {"bots": {}, "running": [], "logs": {}, "processes": {}})

def init_defaults():
    if "admins" not in bot_data:
        bot_data["admins"] = [ADMIN_ID]
    if ADMIN_ID not in bot_data["admins"]:
        bot_data["admins"].append(ADMIN_ID)
    
    bot_data.setdefault("banned", [])
    bot_data.setdefault("folder", "bots")
    bot_data.setdefault("upload", "on")
    bot_data.setdefault("tak", "on")
    bot_data.setdefault("tawgeh", "on")
    bot_data.setdefault("bott", "on")
    bot_data.setdefault("premium", "off")
    bot_data.setdefault("numberfiles", 7)
    bot_data.setdefault("numberban", 3)
    bot_data.setdefault("stabilizing", "off")
    bot_data.setdefault("directing", "off")
    bot_data.setdefault("backup_enabled", True)
    
    app_data.setdefault("twasol", {})
    app_data.setdefault("mode", {})
    app_data.setdefault("last_backup", None)
    
    stats_data.setdefault("stats", {
        "total_users": 0,
        "total_groups": 0,
        "today": {"date": datetime.now().strftime("%Y-%m-%d"), "users": 0, "groups": 0},
        "yesterday": {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "users": 0, "groups": 0},
        "new_today": 0,
        "new_groups_today": 0,
        "total_bots_created": 0,
        "total_stars_earned": 0,
    })
    
    bots_manager.setdefault("bots", {})
    bots_manager.setdefault("running", [])
    bots_manager.setdefault("logs", {})
    bots_manager.setdefault("processes", {})

init_defaults()
save_all()

# ==================== دوال الأزرار الملونة ====================
def create_colored_button(text: str, callback_data: str = None, url: str = None, style: str = "primary", icon_emoji_id: str = None):
    try:
        if url:
            return telebot.types.InlineKeyboardButton(
                text=text,
                url=url,
                style=style,
                icon_custom_emoji_id=icon_emoji_id
            )
        else:
            return telebot.types.InlineKeyboardButton(
                text=text,
                callback_data=callback_data,
                style=style,
                icon_custom_emoji_id=icon_emoji_id
            )
    except TypeError:
        if url:
            return telebot.types.InlineKeyboardButton(text=text, url=url)
        else:
            return telebot.types.InlineKeyboardButton(text=text, callback_data=callback_data)

# ==================== القوائم ====================
def main_menu_keyboard(user_id: int):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        create_colored_button("📤 رفع بوت", callback_data="upload_bot", style="success"),
        create_colored_button("📁 بوتاتي", callback_data="my_bots", style="primary")
    )
    keyboard.add(
        create_colored_button("📢 نشر بوتي", callback_data="publish_bot", style="primary"),
        create_colored_button("⭐ أسعار الاشتراك", callback_data="prices", style="success")
    )
    keyboard.add(
        create_colored_button("👑 المطور", url="https://t.me/ggzh9", style="primary"),
        create_colored_button("📢 قناة البوت", url=BOT_CHANNEL, style="primary")
    )
    return keyboard

def admin_panel_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        create_colored_button("📤 رفع بوت جديد", callback_data="admin_upload_bot", style="success"),
        create_colored_button("🤖 إدارة البوتات", callback_data="bots_manager_menu", style="primary")
    )
    keyboard.add(
        create_colored_button("📢 بث مباشر", callback_data="broadcast_menu", style="primary"),
        create_colored_button("📊 إحصائيات", callback_data="statistics", style="primary")
    )
    keyboard.add(
        create_colored_button("🔒 الحظر", callback_data="ban_menu", style="danger"),
        create_colored_button("👥 الادمنية", callback_data="admin_menu", style="primary")
    )
    keyboard.add(
        create_colored_button("⭐ الاشتراكات", callback_data="subscription_menu", style="success"),
        create_colored_button("📦 نسخ احتياطي", callback_data="backup_menu", style="primary")
    )
    keyboard.add(
        create_colored_button("🔄 تحديث السيرفر", callback_data="update_server", style="success"),
        create_colored_button("📋 السجلات", callback_data="logs_menu", style="primary")
    )
    keyboard.add(
        create_colored_button("💾 استرجاع معلومات", callback_data="restore_menu", style="primary"),
        create_colored_button("👑 المطور", url="https://t.me/ggzh9", style="primary")
    )
    keyboard.add(
        create_colored_button("📢 القناة", url=CHANNEL, style="primary")
    )
    return keyboard

def publish_menu_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        create_colored_button("📅 يوم (10 ⭐)", callback_data="publish_day", style="primary"),
        create_colored_button("📅 أسبوع (50 ⭐)", callback_data="publish_week", style="success"),
        create_colored_button("📅 شهر (600 ⭐)", callback_data="publish_month", style="danger")
    )
    keyboard.add(create_colored_button("🔙 رجوع", callback_data="back", style="primary"))
    return keyboard

def back_button():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(create_colored_button("🔙 رجوع", callback_data="back", style="primary"))
    return keyboard

def back_to_admin():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(create_colored_button("🔙 رجوع للوحة التحكم", callback_data="admin_panel", style="primary"))
    return keyboard

def bots_manager_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    running_count = len(bots_manager.get("running", []))
    total_bots = len(bots_manager.get("bots", {}))
    
    keyboard.add(create_colored_button(f"📊 إجمالي البوتات: {total_bots}", callback_data="bots_total", style="primary"))
    keyboard.add(create_colored_button(f"🟢 المشغلة: {running_count}", callback_data="bots_running", style="success"))
    keyboard.add(create_colored_button("📋 قائمة البوتات", callback_data="bots_list", style="primary"))
    keyboard.add(create_colored_button("📤 رفع بوت جديد", callback_data="admin_upload_bot", style="success"))
    keyboard.add(create_colored_button("🔄 إعادة تشغيل بوت", callback_data="restart_bot", style="primary"))
    keyboard.add(create_colored_button("⏹ إيقاف بوت", callback_data="stop_bot", style="danger"))
    keyboard.add(create_colored_button("🗑 حذف بوت", callback_data="delete_bot", style="danger"))
    keyboard.add(create_colored_button("📊 سجلات البوت", callback_data="bot_logs", style="primary"))
    keyboard.add(create_colored_button("🔙 رجوع", callback_data="admin_panel", style="primary"))
    return keyboard

# ==================== إدارة العمليات ====================
running_processes = {}
process_lock = threading.Lock()

def start_bot_process(bot_id: str, bot_file: str) -> bool:
    try:
        if not os.path.exists(bot_file):
            logger.error(f"❌ ملف البوت غير موجود: {bot_file}")
            return False
        
        cmd = f"nohup python3 {bot_file} > /dev/null 2>&1 &"
        os.system(cmd)
        
        logger.info(f"✅ تم تشغيل البوت {bot_id} بشكل مستقل")
        
        with process_lock:
            running_processes[bot_id] = {
                'pid': 0,
                'started': datetime.now().isoformat(),
                'status': 'running',
                'independent': True
            }
            
            if "processes" not in bots_manager:
                bots_manager["processes"] = {}
            bots_manager["processes"][bot_id] = {
                'pid': 0,
                'started': datetime.now().isoformat()
            }
            
            if bot_id not in bots_manager.get("running", []):
                if "running" not in bots_manager:
                    bots_manager["running"] = []
                bots_manager["running"].append(bot_id)
            
            if bot_id in bots_manager.get("bots", {}):
                bots_manager["bots"][bot_id]["status"] = "running"
            save_all()
        
        update_bot_status(bot_id, "running")
        log_bot_access(bot_id, 0, "started")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت {bot_id}: {e}")
        return False

def stop_bot_process(bot_id: str) -> bool:
    try:
        with process_lock:
            if bot_id in running_processes:
                os.system(f"pkill -f {bot_id}")
                del running_processes[bot_id]
            
            if bot_id in bots_manager.get("running", []):
                bots_manager["running"].remove(bot_id)
            
            if bot_id in bots_manager.get("bots", {}):
                bots_manager["bots"][bot_id]["status"] = "stopped"
            save_all()
        
        update_bot_status(bot_id, "stopped")
        log_bot_access(bot_id, 0, "stopped")
        return True
    except:
        return False

def monitor_bots():
    while True:
        try:
            expired = check_expired_bots()
            if expired > 0:
                trigger_auto_deploy()
            
            # التحقق من البوتات المشغلة
            for bot_id, data in list(bots_manager.get("bots", {}).items()):
                if bot_id in bots_manager.get("running", []):
                    bot_file = os.path.join(BOTS_PATH, data.get("file", ""))
                    if not os.path.exists(bot_file):
                        stop_bot_process(bot_id)
                        update_bot_status(bot_id, "missing")
                        github_path = get_bot_github_path(bot_id)
                        if github_path:
                            restore_bot_from_github(bot_id, github_path)
                            trigger_auto_deploy()
            
            time.sleep(30)
        except Exception as e:
            logger.error(f"❌ خطأ في المراقبة: {e}")
            time.sleep(60)

def restore_bot_from_github(bot_id: str, github_path: str):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        
        try:
            content = repo.get_contents(f"{github_path}/bot.py")
            bot_content = base64.b64decode(content.content)
            bot_folder = os.path.join(BOTS_PATH, bot_id)
            os.makedirs(bot_folder, exist_ok=True)
            with open(os.path.join(bot_folder, "bot.py"), "wb") as f:
                f.write(bot_content)
        except:
            pass
        
        try:
            content = repo.get_contents(f"{github_path}/requirements.txt")
            req_content = base64.b64decode(content.content)
            bot_folder = os.path.join(BOTS_PATH, bot_id)
            os.makedirs(bot_folder, exist_ok=True)
            with open(os.path.join(bot_folder, "requirements.txt"), "wb") as f:
                f.write(req_content)
        except:
            pass
        
        bot_file = os.path.join(BOTS_PATH, bot_id, "bot.py")
        if os.path.exists(bot_file):
            start_bot_process(bot_id, bot_file)
            update_bot_status(bot_id, "running")
            return True
        
        return False
    except Exception as e:
        logger.error(f"خطأ في استعادة البوت: {e}")
        return False

# ==================== وظائف النسخ الاحتياطي ====================
def create_full_backup():
    """إنشاء نسخة احتياطية كاملة لجميع بيانات البوت"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = os.path.join(BACKUP_ZIP_PATH, f"full_backup_{timestamp}.zip")
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # إضافة قاعدة البيانات
            if os.path.exists(DB_PATH):
                zipf.write(DB_PATH, "bot_data.db")
            
            # إضافة ملفات البوتات
            if os.path.exists(BOTS_PATH):
                for root, dirs, files in os.walk(BOTS_PATH):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join("bots", os.path.relpath(file_path, BOTS_PATH))
                        zipf.write(file_path, arcname)
            
            # إضافة ملفات البيانات
            for data_file in ["bot.json", "app.json", "statistics.json", "bots_manager.json"]:
                if os.path.exists(data_file):
                    zipf.write(data_file, data_file)
            
            # إضافة سجلات
            if os.path.exists("bot.log"):
                zipf.write("bot.log", "bot.log")
            
            # إضافة معلومات النسخة
            info_data = {
                "timestamp": timestamp,
                "version": "1.0",
                "total_bots": len(bots_manager.get("bots", {})),
                "total_users": len(stats_data.get("users", [])),
                "created_by": DEVELOPER
            }
            zipf.writestr("backup_info.json", json.dumps(info_data, indent=2, ensure_ascii=False))
        
        logger.info(f"✅ تم إنشاء نسخة احتياطية كاملة: {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
        return None

def auto_backup():
    """وظيفة النسخ الاحتياطي التلقائي - تعمل كل 24 ساعة"""
    while True:
        try:
            if bot_data.get("backup_enabled", True):
                backup_file = create_full_backup()
                if backup_file:
                    # إرسال النسخة للمالك
                    with open(backup_file, 'rb') as f:
                        bot.send_document(
                            ADMIN_ID,
                            f,
                            caption=f"📦 **نسخة احتياطية تلقائية**\n\n"
                                   f"🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                   f"🤖 عدد البوتات: {len(bots_manager.get('bots', {}))}\n"
                                   f"👥 عدد المستخدمين: {len(stats_data.get('users', []))}\n"
                                   f"📁 حجم الملف: {os.path.getsize(backup_file) / 1024 / 1024:.2f} ميجابايت",
                            parse_mode="Markdown"
                        )
                    
                    # تحديث وقت آخر نسخة
                    app_data["last_backup"] = datetime.now().isoformat()
                    save_data("app.json", app_data)
                    
                    logger.info("✅ تم إرسال النسخة الاحتياطية التلقائية للمالك")
            
            # الانتظار 24 ساعة
            time.sleep(86400)  # 24 ساعة
        except Exception as e:
            logger.error(f"❌ خطأ في النسخ الاحتياطي التلقائي: {e}")
            time.sleep(3600)  # انتظر ساعة ثم حاول مرة أخرى

def restore_from_backup(zip_file_path: str):
    """استرجاع جميع البيانات من ملف ZIP"""
    try:
        # إنشاء مجلد مؤقت للاستخراج
        temp_restore = os.path.join(TEMP_PATH, "restore_temp")
        if os.path.exists(temp_restore):
            shutil.rmtree(temp_restore)
        os.makedirs(temp_restore)
        
        # استخراج الملف
        with zipfile.ZipFile(zip_file_path, 'r') as zipf:
            zipf.extractall(temp_restore)
        
        # استرجاع قاعدة البيانات
        db_file = os.path.join(temp_restore, "bot_data.db")
        if os.path.exists(db_file):
            # نسخ احتياطي للقاعدة الحالية
            if os.path.exists(DB_PATH):
                backup_db = f"{DB_PATH}.backup"
                shutil.copy2(DB_PATH, backup_db)
            
            # نسخ القاعدة الجديدة
            shutil.copy2(db_file, DB_PATH)
            logger.info("✅ تم استرجاع قاعدة البيانات")
        
        # استرجاع ملفات البوتات
        bots_restore = os.path.join(temp_restore, "bots")
        if os.path.exists(bots_restore):
            if os.path.exists(BOTS_PATH):
                shutil.rmtree(BOTS_PATH)
            shutil.copytree(bots_restore, BOTS_PATH)
            logger.info("✅ تم استرجاع ملفات البوتات")
        
        # استرجاع ملفات البيانات
        for data_file in ["bot.json", "app.json", "statistics.json", "bots_manager.json"]:
            file_path = os.path.join(temp_restore, data_file)
            if os.path.exists(file_path):
                shutil.copy2(file_path, data_file)
                logger.info(f"✅ تم استرجاع {data_file}")
        
        # إعادة تحميل البيانات
        global bot_data, app_data, stats_data, bots_manager
        bot_data = load_data("bot.json", {})
        app_data = load_data("app.json", {})
        stats_data = load_data("statistics.json", {})
        bots_manager = load_data("bots_manager.json", {})
        
        # إعادة تشغيل البوتات
        for bot_id in bots_manager.get("running", []):
            if bot_id in bots_manager.get("bots", {}):
                bot_file = os.path.join(BOTS_PATH, bots_manager["bots"][bot_id]["file"])
                if os.path.exists(bot_file):
                    start_bot_process(bot_id, bot_file)
        
        # تنظيف المجلد المؤقت
        shutil.rmtree(temp_restore)
        
        logger.info("✅ تم استرجاع جميع البيانات بنجاح")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في استرجاع البيانات: {e}")
        return False

# ==================== رسالة الترحيب الجديدة ====================
def get_welcome_message(user_id: int, first_name: str) -> str:
    sub = get_user_subscription(user_id)
    if sub:
        days_left = (sub["expiry"] - datetime.now()).days
        if days_left > 0:
            expiry_text = f"✅ نشط - متبقي {days_left} يوم"
        else:
            expiry_text = "❌ منتهي"
        sub_type = f"📦 {sub['type']}"
    else:
        expiry_text = "❌ غير مشترك"
        sub_type = "❌ لا يوجد"
    
    return f"""
🌟 <b>مرحباً بك في استضافة كايو</b> 🚀

━━━━━━━━━━━━━━━━━━
👤 <b>الاسم:</b> {first_name}
🆔 <b>ايديك:</b> <code>{user_id}</code>
💳 <b>الاشتراك:</b> {expiry_text}
━━━━━━━━━━━━━━━━━━

<b>📌 الخدمات المتاحة:</b>
• 🚀 رفع وتشغيل بوتات تليجرام
• 🎨 تلوين أزرار البوتات
• ⭐ اشتراكات بالنجوم
• 📁 حفظ البوتات في GitHub

<b>⭐ الأسعار:</b>
يوم: 10⭐ | أسبوع: 50⭐ | شهر: 600⭐

👑 <b>المطور:</b> <a href='https://t.me/ggzh9'>@ggzh9</a>
📢 <b>القناة:</b> <a href='{CHANNEL}'>قناة كايو</a>
"""

# ==================== الأوامر ====================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    if is_banned(user_id):
        bot.reply_to(message, "⛔ أنت محظور من استخدام هذا البوت.")
        return
    
    if user_id not in stats_data["users"]:
        stats_data["users"].append(user_id)
        stats_data["stats"]["total_users"] = len(stats_data["users"])
        stats_data["stats"]["today"]["users"] += 1
        stats_data["stats"]["new_today"] += 1
        save_all()
        try:
            bot.send_message(ADMIN_ID, f"🆕 مستخدم جديد\nالايدي: {user_id}\nاليوزر: @{message.from_user.username or 'لا يوجد'}\nالاسم: {first_name}", parse_mode="HTML")
        except:
            pass
    
    welcome_msg = get_welcome_message(user_id, first_name)
    
    if is_admin(user_id):
        bot.reply_to(message, welcome_msg, parse_mode="HTML", reply_markup=admin_panel_keyboard())
    else:
        bot.reply_to(message, welcome_msg, parse_mode="HTML", reply_markup=main_menu_keyboard(user_id))

# ==================== معالج رفع البوت ====================
def process_bot_file(message):
    user_id = message.from_user.id
    
    if is_banned(user_id):
        bot.reply_to(message, "⛔ أنت محظور")
        return
    
    if not is_admin(user_id) and not is_user_subscribed(user_id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(create_colored_button("⭐ شراء اشتراك", callback_data="prices", style="success"))
        bot.reply_to(message, "⚠️ ليس لديك اشتراك فعال!\n📌 اشترك الآن بالنجوم لرفع البوتات.", reply_markup=keyboard)
        return
    
    if not message.document:
        bot.reply_to(message, "❌ يرجى إرسال ملف bot.py", reply_markup=back_button())
        return
    
    if not message.document.file_name.endswith('.py'):
        bot.reply_to(message, "❌ يرجى إرسال ملف Python (.py)", reply_markup=back_button())
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        bot_name = message.document.file_name.replace('.py', '')
        bot_id = f"bot_{int(time.time())}_{user_id}"
        
        bot_folder = os.path.join(BOTS_PATH, bot_id)
        os.makedirs(bot_folder, exist_ok=True)
        
        bot_file_path = os.path.join(bot_folder, "bot.py")
        with open(bot_file_path, "wb") as f:
            f.write(downloaded_file)
        
        save_bot_to_db(bot_id, bot_name, user_id, bot_file_path, "", "waiting", "", 0)
        
        bot_info = {
            "id": bot_id,
            "name": bot_name,
            "file": f"{bot_id}/bot.py",
            "status": "waiting",
            "created": datetime.now().isoformat(),
            "user_id": user_id,
            "username": message.from_user.username or "لا يوجد"
        }
        bots_manager["bots"][bot_id] = bot_info
        save_all()
        
        stats_data["stats"]["total_bots_created"] += 1
        save_all()
        
        msg = bot.reply_to(
            message,
            f"✅ تم استلام ملف البوت: {bot_name}\n🆔 المعرف: {bot_id}\n📤 أرسل الآن ملف requirements.txt",
            reply_markup=back_button()
        )
        bot.register_next_step_handler(msg, process_requirements_file, bot_id, bot_folder, bot_name)
    except Exception as e:
        logger.error(f"خطأ في معالجة ملف البوت: {e}")
        bot.reply_to(message, f"❌ خطأ: {str(e)}", reply_markup=back_button())

def process_requirements_file(message, bot_id, bot_folder, bot_name):
    user_id = message.from_user.id
    
    if not message.document:
        bot.reply_to(message, "❌ يرجى إرسال ملف requirements.txt", reply_markup=back_button())
        return
    
    if not message.document.file_name.endswith('.txt'):
        bot.reply_to(message, "❌ يرجى إرسال ملف requirements.txt", reply_markup=back_button())
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        req_file_path = os.path.join(bot_folder, "requirements.txt")
        with open(req_file_path, "wb") as f:
            f.write(downloaded_file)
        
        github_path = upload_bot_to_github(bot_folder, bot_name, bot_id)
        if github_path:
            save_bot_to_db(bot_id, bot_name, user_id, os.path.join(bot_folder, "bot.py"), github_path, "waiting", "", 0)
        
        trigger_auto_deploy()
        
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            create_colored_button("📅 يوم (10 ⭐)", callback_data=f"duration_day:{bot_id}", style="primary"),
            create_colored_button("📅 أسبوع (50 ⭐)", callback_data=f"duration_week:{bot_id}", style="success")
        )
        keyboard.add(
            create_colored_button("📅 شهر (600 ⭐)", callback_data=f"duration_month:{bot_id}", style="danger"),
            create_colored_button("💎 غير محدد (للمطورين)", callback_data=f"duration_unlimited:{bot_id}", style="primary")
        )
        
        bot.reply_to(
            message,
            f"📅 اختر مدة تشغيل البوت:\n\n"
            f"🆔 المعرف: {bot_id}\n"
            f"📝 الاسم: {bot_name}\n"
            f"📁 GitHub: {github_path if github_path else 'جاري الرفع'}\n\n"
            f"⭐ الأسعار بالنجوم:\n"
            f"• يوم: 10 نجوم\n"
            f"• أسبوع: 50 نجوم\n"
            f"• شهر: 600 نجوم\n"
            f"• غير محدد: مجاناً (للمطورين)",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"خطأ في معالجة ملف المتطلبات: {e}")
        bot.reply_to(message, f"❌ خطأ: {str(e)}", reply_markup=back_button())

# ==================== معالجات الأزرار ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    
    if is_banned(user_id):
        bot.answer_callback_query(call.id, "⛔ أنت محظور", show_alert=True)
        return
    
    # ===== رجوع =====
    if call.data == "back":
        try:
            if is_admin(user_id):
                welcome_msg = get_welcome_message(user_id, call.from_user.first_name)
                bot.edit_message_text(welcome_msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=admin_panel_keyboard())
            else:
                welcome_msg = get_welcome_message(user_id, call.from_user.first_name)
                bot.edit_message_text(welcome_msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=main_menu_keyboard(user_id))
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== لوحة الأدمن =====
    if call.data == "admin_panel":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            welcome_msg = get_welcome_message(user_id, call.from_user.first_name)
            bot.edit_message_text(welcome_msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=admin_panel_keyboard())
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== بوتاتي =====
    if call.data == "my_bots":
        show_user_bots(call.message, user_id)
        bot.answer_callback_query(call.id)
        return
    
    # ===== نشر بوتي =====
    if call.data == "publish_bot":
        text = """
📢 <b>نشر بوتي</b>

━━━━━━━━━━━━━━━━━━
📌 اختر مدة النشر:

⭐ <b>الباقات المتاحة:</b>
• يوم: 10 نجوم
• أسبوع: 50 نجوم  
• شهر: 600 نجوم

💡 عند اختيار الباقة، سيطلب منك البوت دفع المبلغ بالنجوم
سيتم تفعيل بوتك فوراً بعد الدفع
"""
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=publish_menu_keyboard())
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== اختيار مدة النشر =====
    if call.data.startswith("publish_"):
        handle_publish_duration(call)
        return
    
    # ===== أسعار الاشتراك =====
    if call.data == "prices":
        text = """
⭐ <b>أسعار الاشتراك بالنجوم</b>

━━━━━━━━━━━━━━━━━━
📅 <b>الباقات المتاحة:</b>

• 🟢 <b>يوم</b> — 10 نجوم
• 🔵 <b>أسبوع</b> — 50 نجوم
• 🟣 <b>شهر</b> — 600 نجوم
• 💎 <b>غير محدود</b> — للمطورين فقط

━━━━━━━━━━━━━━━━━━
📌 <b>كيفية الدفع:</b>
• أرسل النجوم إلى البوت
• سيتم تفعيل الاشتراك تلقائياً

💬 <b>للتواصل مع المطور:</b>
<a href='https://t.me/ggzh9'>@ggzh9</a>

📢 <b>قناة المطور:</b>
<a href='{CHANNEL}'>قناة كايو</a>
"""
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== رفع بوت =====
    if call.data == "upload_bot":
        if not is_admin(user_id) and not is_user_subscribed(user_id):
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(create_colored_button("⭐ شراء اشتراك", callback_data="prices", style="success"))
            bot.edit_message_text(
                "⚠️ ليس لديك اشتراك فعال!\n📌 اشترك الآن بالنجوم لرفع البوتات.",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
            bot.answer_callback_query(call.id)
            return
        
        try:
            msg = bot.edit_message_text("📤 أرسل ملف البوت (bot.py) لرفعه.", call.message.chat.id, call.message.message_id, reply_markup=back_button())
            bot.register_next_step_handler(msg, process_bot_file)
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== اختيار المدة =====
    if call.data.startswith("duration_"):
        handle_duration(call)
        return
    
    # ===== تلوين الأزرار =====
    if call.data.startswith("color_"):
        handle_color(call)
        return
    
    # ===== اختيار النمط =====
    if call.data.startswith("style_"):
        handle_style(call)
        return
    
    # ===== تحديث السيرفر =====
    if call.data == "update_server":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            bot.edit_message_text("⏳ جاري تحديث السيرفر...", call.message.chat.id, call.message.message_id)
            if trigger_auto_deploy():
                bot.edit_message_text("✅ تم تحديث السيرفر بنجاح!", call.message.chat.id, call.message.message_id, reply_markup=admin_panel_keyboard())
            else:
                bot.edit_message_text("❌ فشل تحديث السيرفر", call.message.chat.id, call.message.message_id, reply_markup=admin_panel_keyboard())
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== إدارة البوتات =====
    if call.data == "bots_manager_menu":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            bot.edit_message_text(
                f"<b>🤖 إدارة البوتات</b>\n\n📊 إجمالي البوتات: {len(bots_manager.get('bots', {}))}\n🟢 المشغلة: {len(bots_manager.get('running', []))}\n🔴 المتوقفة: {len(bots_manager.get('bots', {})) - len(bots_manager.get('running', []))}",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=bots_manager_keyboard()
            )
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "admin_upload_bot":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            msg = bot.edit_message_text("📤 أرسل ملف البوت (bot.py) لرفعه.", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
            bot.register_next_step_handler(msg, process_bot_file)
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "bots_list":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        
        bots = bots_manager.get("bots", {})
        if not bots:
            try:
                bot.edit_message_text("📭 لا توجد بوتات.", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
            except:
                pass
            bot.answer_callback_query(call.id)
            return
        
        text = "<b>🤖 قائمة البوتات:</b>\n\n"
        for bot_id, data in list(bots.items())[:20]:
            status = "🟢 شغال" if bot_id in bots_manager.get("running", []) else "🔴 متوقف"
            remaining = get_bot_remaining_days(bot_id)
            github_path = get_bot_github_path(bot_id) or "غير موجود"
            text += f"🆔 <code>{bot_id}</code>\n📝 {data.get('name', 'غير معروف')}\n👤 {data.get('username', 'غير معروف')}\n📊 {status}\n📅 {remaining}\n📁 {github_path}\n\n"
        
        if len(bots) > 20:
            text += f"\n... وعرض {len(bots) - 20} بوتات أخرى"
        
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_to_admin())
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "restart_bot":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            msg = bot.edit_message_text("📝 أرسل معرف البوت الذي تريد إعادة تشغيله.", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
            bot.register_next_step_handler(msg, process_restart_bot)
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "stop_bot":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            msg = bot.edit_message_text("📝 أرسل معرف البوت الذي تريد إيقافه.", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
            bot.register_next_step_handler(msg, process_stop_bot)
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "delete_bot":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            msg = bot.edit_message_text("📝 أرسل معرف البوت الذي تريد حذفه.", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
            bot.register_next_step_handler(msg, process_delete_bot)
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "bot_logs":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            msg = bot.edit_message_text("📝 أرسل معرف البوت لعرض سجلاته.", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
            bot.register_next_step_handler(msg, process_show_bot_logs)
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== قائمة البث المباشر =====
    if call.data == "broadcast_menu":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(create_colored_button("📝 بث نصي", callback_data="broadcast_text", style="primary"))
        keyboard.add(create_colored_button("🖼 بث صورة", callback_data="broadcast_photo", style="primary"))
        keyboard.add(create_colored_button("🎥 بث فيديو", callback_data="broadcast_video", style="primary"))
        keyboard.add(create_colored_button("📄 بث مستند", callback_data="broadcast_document", style="primary"))
        keyboard.add(create_colored_button("📊 تاريخ البث", callback_data="broadcast_history", style="primary"))
        keyboard.add(create_colored_button("🔙 رجوع", callback_data="admin_panel", style="primary"))
        
        bot.edit_message_text(
            "📢 <b>قائمة البث المباشر</b>\n\n"
            "📌 اختر نوع المحتوى الذي تريد بثه:\n"
            "• نص: رسالة نصية عادية\n"
            "• صورة: صورة مع وصف\n"
            "• فيديو: فيديو مع وصف\n"
            "• مستند: ملف مع وصف",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "broadcast_text":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text(
            "📝 أرسل النص الذي تريد بثه.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_to_admin()
        )
        bot.register_next_step_handler(msg, process_broadcast_text)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "broadcast_photo":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text(
            "🖼 أرسل الصورة التي تريد بثها.\n"
            "📝 يمكنك إضافة وصف مع الصورة.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_to_admin()
        )
        bot.register_next_step_handler(msg, process_broadcast_photo)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "broadcast_video":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text(
            "🎥 أرسل الفيديو الذي تريد بثه.\n"
            "📝 يمكنك إضافة وصف مع الفيديو.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_to_admin()
        )
        bot.register_next_step_handler(msg, process_broadcast_video)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "broadcast_document":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text(
            "📄 أرسل المستند الذي تريد بثه.\n"
            "📝 يمكنك إضافة وصف مع المستند.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_to_admin()
        )
        bot.register_next_step_handler(msg, process_broadcast_document)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "broadcast_history":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, content_type, content, sent_count, failed_count, created_at FROM broadcast_history ORDER BY created_at DESC LIMIT 10")
            history = c.fetchall()
            conn.close()
            
            if not history:
                text = "📊 لا يوجد سجل بث."
            else:
                text = "📊 <b>آخر 10 عمليات بث:</b>\n\n"
                for item in history:
                    text += f"🆔 {item[0]}\n"
                    text += f"📌 النوع: {item[1]}\n"
                    text += f"📝 المحتوى: {item[2][:50]}...\n"
                    text += f"✅ تم الإرسال: {item[3]}\n"
                    text += f"❌ فشل: {item[4]}\n"
                    text += f"⏰ {item[5][:16]}\n\n"
            
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_to_admin())
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== إحصائيات =====
    if call.data == "statistics":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        stats = stats_data["stats"]
        msg = (
            "<b>📊 الإحصائيات العامة</b>\n\n"
            f"👥 المستخدمون: <b>{stats['total_users']}</b>\n"
            f"📁 الملفات: <b>{bot_data.get('file', 0)}</b>\n"
            f"🔒 المحظورين: <b>{len(bot_data.get('banned', []))}</b>\n"
            f"🤖 البوتات: <b>{len(bots_manager.get('bots', {}))}</b>\n"
            f"🟢 المشغلة: <b>{len(bots_manager.get('running', []))}</b>\n"
            f"📦 بوتات GitHub: <b>{len([b for b in bots_manager.get('bots', {}).values() if b.get('github_path')])}</b>\n"
            f"⭐ نجوم مجمعة: <b>{stats.get('total_stars_earned', 0)}</b>\n"
            f"📅 آخر نسخة: <b>{app_data.get('last_backup', 'لا يوجد')[:16] if app_data.get('last_backup') else 'لا يوجد'}</b>"
        )
        try:
            bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_to_admin())
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== حظر =====
    if call.data == "ban_menu":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            create_colored_button("🔒 حظر", callback_data="ban_user", style="danger"),
            create_colored_button("🔓 إلغاء حظر", callback_data="unban_user", style="success")
        )
        keyboard.add(create_colored_button("📋 المحظورين", callback_data="banned_list", style="primary"))
        keyboard.add(create_colored_button("🔙 رجوع", callback_data="admin_panel", style="primary"))
        bot.edit_message_text("<b>🔒 قسم الحظر</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "ban_user":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text("📝 أرسل ايدي المستخدم وسبب الحظر\nمثال: 123456789 سبب الحظر", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
        bot.register_next_step_handler(msg, process_ban_user)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "unban_user":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text("📝 أرسل ايدي المستخدم لإلغاء الحظر", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
        bot.register_next_step_handler(msg, process_unban_user)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "banned_list":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT user_id, reason, ban_date FROM banned_users")
            banned = c.fetchall()
            conn.close()
            
            if not banned:
                text = "📭 لا يوجد محظورين."
            else:
                text = "<b>🚫 المحظورين:</b>\n\n"
                for uid, reason, date in banned:
                    text += f"🆔 {uid}\n📌 {reason}\n⏰ {date[:16]}\n\n"
            
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_to_admin())
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== إدارة الأدمن =====
    if call.data == "admin_menu":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            create_colored_button("⬆️ رفع ادمن", callback_data="add_admin", style="success"),
            create_colored_button("⬇️ حذف ادمن", callback_data="remove_admin", style="danger")
        )
        keyboard.add(create_colored_button("📋 الادمنية", callback_data="admins_list", style="primary"))
        keyboard.add(create_colored_button("🔙 رجوع", callback_data="admin_panel", style="primary"))
        bot.edit_message_text("<b>👥 إدارة الادمنية</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "add_admin":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text("📝 أرسل ايدي المستخدم لرفعه ادمن", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
        bot.register_next_step_handler(msg, process_add_admin)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "remove_admin":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text("📝 أرسل ايدي المستخدم لحذف ادمنيته", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
        bot.register_next_step_handler(msg, process_remove_admin)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "admins_list":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        admins = bot_data.get("admins", [])
        if not admins:
            text = "📭 لا يوجد ادمنية."
        else:
            text = "<b>👥 الادمنية:</b>\n"
            for uid in admins:
                try:
                    chat_member = bot.get_chat_member(uid, uid)
                    name = chat_member.user.full_name
                    text += f"• {name} - 🆔 {uid}\n"
                except:
                    text += f"• 🆔 {uid}\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_to_admin())
        bot.answer_callback_query(call.id)
        return
    
    # ===== الاشتراكات =====
    if call.data == "subscription_menu":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            create_colored_button("➕ إضافة اشتراك", callback_data="add_subscription", style="success"),
            create_colored_button("➖ إزالة اشتراك", callback_data="remove_subscription", style="danger")
        )
        keyboard.add(create_colored_button("📋 قائمة المشتركين", callback_data="subscriptions_list", style="primary"))
        keyboard.add(create_colored_button("🔙 رجوع", callback_data="admin_panel", style="primary"))
        bot.edit_message_text("<b>⭐ إدارة الاشتراكات</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "add_subscription":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text("📝 أرسل ايدي المستخدم وعدد الأيام\nمثال: 123456789 30", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
        bot.register_next_step_handler(msg, process_add_subscription)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "remove_subscription":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text("📝 أرسل ايدي المستخدم لإزالة الاشتراك", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
        bot.register_next_step_handler(msg, process_remove_subscription)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "subscriptions_list":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT user_id, expiry_date, subscription_type FROM user_subscriptions")
            subs = c.fetchall()
            conn.close()
            
            if not subs:
                text = "📭 لا يوجد مشتركين."
            else:
                text = "<b>⭐ قائمة المشتركين:</b>\n\n"
                for uid, expiry, sub_type in subs:
                    expiry_date = datetime.fromisoformat(expiry)
                    days_left = (expiry_date - datetime.now()).days
                    status = "✅ نشط" if days_left > 0 else "❌ منتهي"
                    text += f"🆔 {uid}\n📅 {sub_type}\n⏳ {days_left} يوم\n📊 {status}\n\n"
            
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_to_admin())
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    # ===== نسخ احتياطي =====
    if call.data == "backup_menu":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(create_colored_button("📦 إنشاء نسخة", callback_data="create_backup", style="success"))
        keyboard.add(create_colored_button("📋 عرض النسخ", callback_data="list_backups", style="primary"))
        keyboard.add(create_colored_button("🔙 رجوع", callback_data="admin_panel", style="primary"))
        bot.edit_message_text("<b>📦 قسم النسخ الاحتياطي</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "create_backup":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            bot.edit_message_text("⏳ جاري إنشاء النسخة الاحتياطية...", call.message.chat.id, call.message.message_id)
        except:
            pass
        
        backup_file = create_full_backup()
        if backup_file:
            try:
                with open(backup_file, 'rb') as f:
                    bot.send_document(
                        call.message.chat.id,
                        f,
                        caption=f"📦 **نسخة احتياطية كاملة**\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        parse_mode="Markdown"
                    )
                bot.edit_message_text("✅ تم إنشاء وإرسال النسخة الاحتياطية!", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
            except:
                pass
        else:
            try:
                bot.edit_message_text("❌ فشل في إنشاء النسخة الاحتياطية", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
            except:
                pass
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "list_backups":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        backups = sorted([f for f in os.listdir(BACKUP_ZIP_PATH) if f.endswith('.zip')])
        if not backups:
            text = "📭 لا توجد نسخ احتياطية."
        else:
            text = "<b>📦 النسخ الاحتياطية:</b>\n"
            for i, b in enumerate(backups[-10:], 1):
                size = os.path.getsize(os.path.join(BACKUP_ZIP_PATH, b)) / 1024 / 1024
                text += f"{i}. {b} - {size:.1f} ميجابايت\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_to_admin())
        bot.answer_callback_query(call.id)
        return
    
    # ===== استرجاع المعلومات =====
    if call.data == "restore_menu":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(create_colored_button("📤 استرجاع من ملف ZIP", callback_data="restore_zip", style="primary"))
        keyboard.add(create_colored_button("🔙 رجوع", callback_data="admin_panel", style="primary"))
        
        bot.edit_message_text(
            "<b>💾 استرجاع المعلومات</b>\n\n"
            "📌 أرسل ملف ZIP للنسخة الاحتياطية التي تريد استرجاعها.\n"
            "⚠️ تحذير: سيتم استبدال جميع البيانات الحالية!",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "restore_zip":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        msg = bot.edit_message_text(
            "📤 أرسل ملف ZIP للنسخة الاحتياطية التي تريد استرجاعها.\n\n"
            "⚠️ تحذير: سيتم استبدال جميع البيانات الحالية!",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_to_admin()
        )
        bot.register_next_step_handler(msg, process_restore_zip)
        bot.answer_callback_query(call.id)
        return
    
    # ===== سجلات =====
    if call.data == "logs_menu":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ غير مصرح", show_alert=True)
            return
        try:
            with open("bot.log", "r", encoding="utf-8") as f:
                logs = f.read().splitlines()[-30:]
                text = "📋 <b>آخر 30 سطر من السجلات:</b>\n\n"
                for log in logs:
                    text += f"{log}\n"
            
            if len(text) > 4000:
                text = text[:4000] + "\n... (تم الاقتطاع)"
            
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_to_admin())
        except:
            bot.edit_message_text("❌ لا توجد سجلات.", call.message.chat.id, call.message.message_id, reply_markup=back_to_admin())
        bot.answer_callback_query(call.id)
        return
    
    # ===== إحصائيات البوتات =====
    if call.data == "bots_total":
        bot.answer_callback_query(call.id, f"📊 إجمالي البوتات: {len(bots_manager.get('bots', {}))}")
        return
    
    if call.data == "bots_running":
        bot.answer_callback_query(call.id, f"🟢 البوتات المشغلة: {len(bots_manager.get('running', []))}")
        return
    
    bot.answer_callback_query(call.id, "⚠️ جاري التطوير...")

# ==================== معالجات اختيار المدة ====================
def handle_duration(call):
    user_id = call.from_user.id
    data_parts = call.data.split(":")
    duration_type = data_parts[0].replace("duration_", "")
    bot_id = data_parts[1]
    
    days_map = {"day": 1, "week": 7, "month": 30, "unlimited": 0}
    days = days_map.get(duration_type, 0)
    stars_cost = {"day": 10, "week": 50, "month": 600, "unlimited": 0}
    cost = stars_cost.get(duration_type, 0)
    
    bot_folder = os.path.join(BOTS_PATH, bot_id)
    bot_file = os.path.join(bot_folder, "bot.py")
    bot_data_db = get_bot_from_db(bot_id)
    bot_name = bot_data_db[1] if bot_data_db else bot_id
    github_path = bot_data_db[4] if bot_data_db else ""
    
    if duration_type == "unlimited" or is_admin(user_id):
        if start_bot_process(bot_id, bot_file):
            update_bot_status(bot_id, "running")
            save_bot_to_db(bot_id, bot_name, user_id, bot_file, github_path, "running", duration_type, days)
            trigger_auto_deploy()
            
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                create_colored_button("🎨 نعم", callback_data=f"color_yes:{bot_id}", style="success"),
                create_colored_button("❌ لا", callback_data=f"color_no:{bot_id}", style="danger")
            )
            
            bot.edit_message_text(
                f"✅ تم تشغيل البوت {bot_id} بنجاح!\n\n"
                f"🆔 المعرف: {bot_id}\n"
                f"📝 الاسم: {bot_name}\n"
                f"📅 المدة: {'غير محدودة' if duration_type == 'unlimited' else f'{days} يوم'}\n"
                f"📁 GitHub: {github_path}\n"
                f"📊 الحالة: 🟢 شغال\n\n"
                f"🎨 هل تريد تلوين أزرار بوتك؟",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )
        else:
            bot.edit_message_text(
                f"❌ فشل في تشغيل البوت {bot_id}",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=back_button()
            )
    else:
        # طلب الدفع بالنجوم
        add_pending_payment(user_id, bot_id, cost)
        
        bot.edit_message_text(
            f"📌 تم اختيار {duration_type}\n\n"
            f"🆔 المعرف: {bot_id}\n"
            f"📅 المدة: {days} يوم\n"
            f"⭐ السعر: {cost} نجوم\n"
            f"📁 GitHub: {github_path}\n\n"
            f"💬 للدفع، أرسل {cost} نجوم إلى البوت.\n"
            f"سيتم تفعيل البوت تلقائياً بعد استلام النجوم.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=back_button()
        )
    
    bot.answer_callback_query(call.id)

# ==================== معالجة اختيار مدة النشر ====================
def handle_publish_duration(call):
    user_id = call.from_user.id
    
    duration_map = {
        "publish_day": {"days": 1, "stars": 10, "name": "يوم"},
        "publish_week": {"days": 7, "stars": 50, "name": "أسبوع"},
        "publish_month": {"days": 30, "stars": 600, "name": "شهر"}
    }
    
    duration = duration_map.get(call.data)
    if not duration:
        bot.answer_callback_query(call.id, "❌ خيار غير صحيح")
        return
    
    if is_admin(user_id):
        # المالك مجاني
        text = f"""
✅ تم تفعيل {duration['name']} مجاناً للمالك!

📅 المدة: {duration['days']} يوم
⭐ السعر: {duration['stars']} نجوم (مجاناً للمالك)

📌 يمكنك الآن رفع بوتك من خلال زر "رفع بوت"
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
        bot.answer_callback_query(call.id)
        return
    
    # للمستخدمين العاديين - طلب دفع
    add_pending_payment(user_id, "publish_subscription", duration['stars'])
    
    text = f"""
📌 تم اختيار باقة {duration['name']}

⭐ السعر: {duration['stars']} نجوم
📅 المدة: {duration['days']} يوم

💬 لإتمام الدفع، أرسل {duration['stars']} نجوم إلى البوت.
سيتم تفعيل اشتراكك فوراً بعد استلام النجوم.
"""
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
    bot.answer_callback_query(call.id)

# ==================== معالجات تلوين الأزرار ====================
def handle_color(call):
    user_id = call.from_user.id
    data_parts = call.data.split(":")
    choice = data_parts[0].replace("color_", "")
    bot_id = data_parts[1]
    
    if choice == "yes":
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            create_colored_button("🔵 أزرق", callback_data=f"style_primary:{bot_id}", style="primary"),
            create_colored_button("🟢 أخضر", callback_data=f"style_success:{bot_id}", style="success")
        )
        keyboard.add(
            create_colored_button("🔴 أحمر", callback_data=f"style_danger:{bot_id}", style="danger"),
            create_colored_button("🎨 أيقونة", callback_data=f"style_icon:{bot_id}", style="primary")
        )
        keyboard.add(
            create_colored_button("⏭ تخطي", callback_data=f"style_skip:{bot_id}", style="primary")
        )
        
        bot.edit_message_text(
            f"🎨 <b>اختر نمط الأزرار لبوتك</b>\n\n"
            f"🆔 المعرف: {bot_id}\n\n"
            f"📌 الأنماط المتاحة:\n"
            f"• 🔵 أزرق (primary)\n"
            f"• 🟢 أخضر (success)\n"
            f"• 🔴 أحمر (danger)\n"
            f"• 🎨 أيقونة مخصصة\n\n"
            f"💡 يمكنك اختيار أيقونة مخصصة من بوت @EmojiIDBot",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        bot.edit_message_text(
            f"✅ تم تشغيل البوت {bot_id} بدون تلوين!",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button()
        )
    
    bot.answer_callback_query(call.id)

def handle_style(call):
    user_id = call.from_user.id
    data_parts = call.data.split(":")
    style = data_parts[0].replace("style_", "")
    bot_id = data_parts[1]
    
    if style == "skip":
        bot.edit_message_text(
            f"✅ تم تشغيل البوت {bot_id} بدون تلوين!",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button()
        )
        bot.answer_callback_query(call.id)
        return
    
    if style == "icon":
        bot.edit_message_text(
            f"🎨 <b>أرسل إيدي الإيموجي</b>\n\n"
            f"🆔 المعرف: {bot_id}\n\n"
            f"📌 للحصول على إيدي الإيموجي:\n"
            f"1️⃣ اذهب إلى بوت @EmojiIDBot\n"
            f"2️⃣ أرسل الإيموجي الذي تريده\n"
            f"3️⃣ انسخ الإيدي\n"
            f"4️⃣ أرسله هنا",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=back_button()
        )
        bot.register_next_step_handler(call.message, process_icon_id, bot_id, style)
        bot.answer_callback_query(call.id)
        return
    
    save_bot_style(bot_id, style)
    
    bot.edit_message_text(
        f"✅ تم تحديث نمط الأزرار للبوت {bot_id}!\n\n"
        f"🎨 النمط: {style}\n"
        f"🆔 المعرف: {bot_id}\n\n"
        f"📌 سيتم تطبيق التغييرات عند إعادة تشغيل البوت.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=back_button()
    )
    bot.answer_callback_query(call.id)

def process_icon_id(message, bot_id, style):
    icon_id = message.text.strip()
    
    if not icon_id or len(icon_id) < 10:
        bot.reply_to(message, "❌ إيدي غير صحيح، يرجى المحاولة مرة أخرى", reply_markup=back_button())
        return
    
    save_bot_style(bot_id, "icon", icon_id)
    
    bot.reply_to(
        message,
        f"✅ تم تحديث أيقونة البوت {bot_id}!\n\n"
        f"🎨 الإيدي: <code>{icon_id}</code>\n"
        f"🆔 المعرف: {bot_id}\n\n"
        f"📌 سيتم تطبيق التغييرات عند إعادة تشغيل البوت.",
        parse_mode="HTML",
        reply_markup=back_button()
    )

def save_bot_style(bot_id: str, style: str, icon_id: str = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if icon_id:
            c.execute("UPDATE bots SET color_style = ?, emoji_id = ? WHERE bot_id = ?", (style, icon_id, bot_id))
        else:
            c.execute("UPDATE bots SET color_style = ? WHERE bot_id = ?", (style, bot_id))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ==================== معالجات البث المباشر ====================
def save_broadcast_history(admin_id, content_type, content, sent_count, failed_count):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO broadcast_history (admin_id, content_type, content, sent_count, failed_count, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (admin_id, content_type, content[:200], sent_count, failed_count, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except:
        pass

def process_broadcast_text(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    text = message.text
    if not text:
        bot.reply_to(message, "❌ يرجى إرسال نص صحيح.", reply_markup=back_to_admin())
        return
    
    send_broadcast(message, text, "text", None)

def process_broadcast_photo(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if not message.photo:
        bot.reply_to(message, "❌ يرجى إرسال صورة.", reply_markup=back_to_admin())
        return
    
    photo = message.photo[-1].file_id
    caption = message.caption or ""
    send_broadcast(message, photo, "photo", caption)

def process_broadcast_video(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if not message.video:
        bot.reply_to(message, "❌ يرجى إرسال فيديو.", reply_markup=back_to_admin())
        return
    
    video = message.video.file_id
    caption = message.caption or ""
    send_broadcast(message, video, "video", caption)

def process_broadcast_document(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if not message.document:
        bot.reply_to(message, "❌ يرجى إرسال مستند.", reply_markup=back_to_admin())
        return
    
    document = message.document.file_id
    caption = message.caption or ""
    send_broadcast(message, document, "document", caption)

def send_broadcast(message, content, content_type, caption):
    user_id = message.from_user.id
    
    targets = stats_data["users"]
    if not targets:
        bot.reply_to(message, "❌ لا يوجد مستهدفون للإذاعة.", reply_markup=back_to_admin())
        return
    
    status_msg = bot.reply_to(message, f"⏳ جاري بدء البث لـ {len(targets)} مستخدم...")
    
    succeeded = 0
    failed = 0
    
    for target in targets:
        try:
            if content_type == "text":
                bot.send_message(target, content)
            elif content_type == "photo":
                bot.send_photo(target, content, caption=caption)
            elif content_type == "video":
                bot.send_video(target, content, caption=caption)
            elif content_type == "document":
                bot.send_document(target, content, caption=caption)
            succeeded += 1
        except:
            failed += 1
        time.sleep(0.1)
    
    save_broadcast_history(user_id, content_type, str(content), succeeded, failed)
    
    bot.edit_message_text(
        f"✅ اكتمل البث!\n\n"
        f"✅ تم الإرسال: {succeeded}\n"
        f"❌ فشل: {failed}",
        status_msg.chat.id,
        status_msg.message_id,
        reply_markup=back_to_admin()
    )

# ==================== معالجة النجوم (الدفع) ====================
@bot.message_handler(content_types=['successful_payment'])
def handle_stars_payment(message):
    """معالجة الدفع بالنجوم"""
    user_id = message.from_user.id
    payment = message.successful_payment
    amount = payment.total_amount // 100  # Telegram Stars (1 Star = 100 units)
    currency = payment.currency
    
    # تسجيل المعاملة
    add_star_transaction(user_id, amount, "payment", f"دفع {amount} نجوم")
    
    # تحديث إحصائيات النجوم
    stats_data["stats"]["total_stars_earned"] = stats_data["stats"].get("total_stars_earned", 0) + amount
    save_all()
    
    # التحقق من الدفع المعلق
    pending = get_pending_payment(user_id)
    
    if pending:
        bot_id = pending["bot_id"]
        stars_needed = pending["stars"]
        
        if amount >= stars_needed:
            # دفع ناجح
            if bot_id == "publish_subscription":
                # اشتراك نشر
                days = 1
                sub_type = "يوم"
                if amount >= 600:
                    days = 30
                    sub_type = "شهر"
                elif amount >= 50:
                    days = 7
                    sub_type = "أسبوع"
                
                add_user_subscription(user_id, days, sub_type)
                remove_pending_payment(user_id)
                
                # إشعار للمالك
                bot.send_message(
                    ADMIN_ID,
                    f"⭐ دفع نجوم - اشتراك نشر\n"
                    f"المستخدم: {user_id}\n"
                    f"المبلغ: {amount} نجوم\n"
                    f"الباقة: {sub_type}\n"
                    f"المتبقي: {amount - stars_needed} نجوم"
                )
                
                bot.reply_to(
                    message,
                    f"✅ تم تفعيل اشتراك {sub_type} بنجاح!\n"
                    f"📅 المدة: {days} يوم\n"
                    f"⭐ تم خصم {stars_needed} نجوم"
                )
            else:
                # تفعيل بوت
                bot_data_db = get_bot_from_db(bot_id)
                if bot_data_db:
                    bot_name = bot_data_db[1]
                    github_path = bot_data_db[4]
                    days_map = {"day": 1, "week": 7, "month": 30}
                    duration_type = "day"
                    if amount >= 600:
                        duration_type = "month"
                    elif amount >= 50:
                        duration_type = "week"
                    days = days_map.get(duration_type, 1)
                    
                    bot_folder = os.path.join(BOTS_PATH, bot_id)
                    bot_file = os.path.join(bot_folder, "bot.py")
                    
                    if start_bot_process(bot_id, bot_file):
                        update_bot_status(bot_id, "running")
                        save_bot_to_db(bot_id, bot_name, user_id, bot_file, github_path, "running", duration_type, days)
                        trigger_auto_deploy()
                        
                        remove_pending_payment(user_id)
                        
                        # إشعار للمالك
                        bot.send_message(
                            ADMIN_ID,
                            f"⭐ دفع نجوم - تفعيل بوت\n"
                            f"المستخدم: {user_id}\n"
                            f"البوت: {bot_id}\n"
                            f"المبلغ: {amount} نجوم\n"
                            f"المدة: {duration_type}\n"
                            f"المتبقي: {amount - stars_needed} نجوم"
                        )
                        
                        bot.reply_to(
                            message,
                            f"✅ تم تشغيل البوت {bot_id} بنجاح!\n"
                            f"📅 المدة: {duration_type}\n"
                            f"⭐ تم خصم {stars_needed} نجوم"
                        )
                    else:
                        bot.reply_to(message, "❌ فشل في تشغيل البوت")
                else:
                    bot.reply_to(message, "❌ البوت غير موجود")
        else:
            # المبلغ غير كافٍ
            bot.reply_to(
                message,
                f"⚠️ المبلغ غير كافٍ!\n"
                f"المطلوب: {stars_needed} نجوم\n"
                f"المرسل: {amount} نجوم"
            )
    else:
        # دفع بدون طلب مسبق - اشتراك عادي
        if amount >= 600:
            days = 30
            sub_type = "شهر"
        elif amount >= 50:
            days = 7
            sub_type = "أسبوع"
        elif amount >= 10:
            days = 1
            sub_type = "يوم"
        else:
            bot.reply_to(message, "⚠️ المبلغ غير كافٍ للاشتراك.")
            return
        
        add_user_subscription(user_id, days, sub_type)
        
        # إشعار للمالك
        bot.send_message(
            ADMIN_ID,
            f"⭐ دفع نجوم - اشتراك عادي\n"
            f"المستخدم: {user_id}\n"
            f"المبلغ: {amount} نجوم\n"
            f"الباقة: {sub_type}"
        )
        
        bot.reply_to(
            message,
            f"✅ تم تفعيل اشتراك {sub_type} بنجاح!\n"
            f"📅 المدة: {days} يوم\n"
            f"⭐ تم خصم {amount} نجوم"
        )

# ==================== معالجة استرجاع ZIP ====================
def process_restore_zip(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if not message.document:
        bot.reply_to(message, "❌ يرجى إرسال ملف ZIP.", reply_markup=back_to_admin())
        return
    
    if not message.document.file_name.endswith('.zip'):
        bot.reply_to(message, "❌ يرجى إرسال ملف ZIP.", reply_markup=back_to_admin())
        return
    
    try:
        # تحميل الملف
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        zip_path = os.path.join(TEMP_PATH, "restore_temp.zip")
        with open(zip_path, "wb") as f:
            f.write(downloaded_file)
        
        # استرجاع البيانات
        status_msg = bot.reply_to(message, "⏳ جاري استرجاع البيانات...")
        
        if restore_from_backup(zip_path):
            bot.edit_message_text(
                "✅ تم استرجاع جميع البيانات بنجاح!\n"
                "🔄 تم إعادة تشغيل البوتات.",
                status_msg.chat.id,
                status_msg.message_id,
                reply_markup=back_to_admin()
            )
        else:
            bot.edit_message_text(
                "❌ فشل في استرجاع البيانات.",
                status_msg.chat.id,
                status_msg.message_id,
                reply_markup=back_to_admin()
            )
        
        # تنظيف
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}", reply_markup=back_to_admin())

# ============================================================
# دوال المعالجة الإضافية
# ============================================================
def process_ban_user(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ الصيغة: ايدي المستخدم سبب الحظر", reply_markup=back_to_admin())
            return
        
        target_id = int(parts[0])
        reason = parts[1]
        
        if ban_user(target_id, reason):
            bot.reply_to(message, f"✅ تم حظر المستخدم {target_id}\n📌 السبب: {reason}", reply_markup=back_to_admin())
            try:
                bot.send_message(target_id, f"⛔ تم حظرك من البوت\n📌 السبب: {reason}")
            except:
                pass
        else:
            bot.reply_to(message, "❌ فشل في حظر المستخدم", reply_markup=back_to_admin())
    except:
        bot.reply_to(message, "❌ ايدي غير صحيح", reply_markup=back_to_admin())

def process_unban_user(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        target_id = int(message.text.strip())
        
        if unban_user(target_id):
            bot.reply_to(message, f"✅ تم إلغاء حظر المستخدم {target_id}", reply_markup=back_to_admin())
            try:
                bot.send_message(target_id, "🎉 تم إلغاء الحظر عنك")
            except:
                pass
        else:
            bot.reply_to(message, "❌ فشل في إلغاء حظر المستخدم", reply_markup=back_to_admin())
    except:
        bot.reply_to(message, "❌ ايدي غير صحيح", reply_markup=back_to_admin())

def process_add_admin(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        target_id = int(message.text.strip())
        
        if target_id in bot_data.get("admins", []):
            bot.reply_to(message, "⚠️ المستخدم بالفعل ادمن", reply_markup=back_to_admin())
            return
        
        bot_data["admins"].append(target_id)
        save_all()
        
        bot.reply_to(message, f"✅ تم رفع المستخدم {target_id} ادمن", reply_markup=back_to_admin())
        try:
            bot.send_message(target_id, "✅ تم رفعك ادمن في البوت")
        except:
            pass
    except:
        bot.reply_to(message, "❌ ايدي غير صحيح", reply_markup=back_to_admin())

def process_remove_admin(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        target_id = int(message.text.strip())
        
        if target_id == ADMIN_ID:
            bot.reply_to(message, "⚠️ لا يمكن حذف المالك", reply_markup=back_to_admin())
            return
        
        if target_id not in bot_data.get("admins", []):
            bot.reply_to(message, "⚠️ المستخدم ليس ادمن", reply_markup=back_to_admin())
            return
        
        bot_data["admins"].remove(target_id)
        save_all()
        
        bot.reply_to(message, f"✅ تم حذف ادمنية المستخدم {target_id}", reply_markup=back_to_admin())
        try:
            bot.send_message(target_id, "❌ تم سحب الادمنية منك")
        except:
            pass
    except:
        bot.reply_to(message, "❌ ايدي غير صحيح", reply_markup=back_to_admin())

def process_add_subscription(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ الصيغة: ايدي المستخدم عدد الأيام", reply_markup=back_to_admin())
            return
        
        target_id = int(parts[0])
        days = int(parts[1])
        
        sub_type = "شهر" if days == 30 else "أسبوع" if days == 7 else "يوم" if days == 1 else f"{days} يوم"
        
        if add_user_subscription(target_id, days, sub_type):
            bot.reply_to(message, f"✅ تم إضافة اشتراك للمستخدم {target_id}\n📅 المدة: {days} يوم", reply_markup=back_to_admin())
            try:
                bot.send_message(target_id, f"🎉 تم تفعيل اشتراكك لمدة {days} يوم")
            except:
                pass
        else:
            bot.reply_to(message, "❌ فشل في إضافة الاشتراك", reply_markup=back_to_admin())
    except:
        bot.reply_to(message, "❌ بيانات غير صحيحة", reply_markup=back_to_admin())

def process_remove_subscription(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        target_id = int(message.text.strip())
        
        if remove_user_subscription(target_id):
            bot.reply_to(message, f"✅ تم إزالة اشتراك المستخدم {target_id}", reply_markup=back_to_admin())
            try:
                bot.send_message(target_id, "❌ تم إزالة اشتراكك")
            except:
                pass
        else:
            bot.reply_to(message, "❌ فشل في إزالة الاشتراك", reply_markup=back_to_admin())
    except:
        bot.reply_to(message, "❌ ايدي غير صحيح", reply_markup=back_to_admin())

def process_restart_bot(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    bot_id = message.text.strip()
    if bot_id not in bots_manager.get("bots", {}):
        bot.reply_to(message, "❌ البوت غير موجود.", reply_markup=back_to_admin())
        return
    
    stop_bot_process(bot_id)
    time.sleep(2)
    
    if bot_id in bots_manager.get("bots", {}):
        bot_file = os.path.join(BOTS_PATH, bots_manager["bots"][bot_id]["file"])
        if os.path.exists(bot_file):
            if start_bot_process(bot_id, bot_file):
                bot.reply_to(message, f"✅ تم إعادة تشغيل البوت {bot_id} بنجاح.", reply_markup=back_to_admin())
                trigger_auto_deploy()
            else:
                bot.reply_to(message, f"❌ فشل في إعادة تشغيل البوت {bot_id}.", reply_markup=back_to_admin())
        else:
            bot.reply_to(message, f"❌ ملف البوت {bot_id} غير موجود.", reply_markup=back_to_admin())

def process_stop_bot(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    bot_id = message.text.strip()
    if bot_id not in bots_manager.get("bots", {}):
        bot.reply_to(message, "❌ البوت غير موجود.", reply_markup=back_to_admin())
        return
    
    if stop_bot_process(bot_id):
        bot.reply_to(message, f"✅ تم إيقاف البوت {bot_id} بنجاح.", reply_markup=back_to_admin())
        trigger_auto_deploy()
    else:
        bot.reply_to(message, f"❌ فشل في إيقاف البوت {bot_id}.", reply_markup=back_to_admin())

def process_delete_bot(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    bot_id = message.text.strip()
    if bot_id not in bots_manager.get("bots", {}):
        bot.reply_to(message, "❌ البوت غير موجود.", reply_markup=back_to_admin())
        return
    
    stop_bot_process(bot_id)
    
    if bot_id in bots_manager.get("bots", {}):
        bot_file = os.path.join(BOTS_PATH, bots_manager["bots"][bot_id]["file"])
        
        if os.path.exists(bot_file):
            os.remove(bot_file)
        
        github_path = get_bot_github_path(bot_id)
        if github_path:
            delete_bot_from_github(bot_id, github_path)
        
        bot_folder = os.path.join(BOTS_PATH, bot_id)
        if os.path.exists(bot_folder):
            shutil.rmtree(bot_folder)
        
        del bots_manager["bots"][bot_id]
        if bot_id in bots_manager.get("logs", {}):
            del bots_manager["logs"][bot_id]
        if bot_id in bots_manager.get("processes", {}):
            del bots_manager["processes"][bot_id]
        
        delete_bot_from_db(bot_id)
        
        save_all()
        trigger_auto_deploy()
        
        bot.reply_to(message, f"✅ تم حذف البوت {bot_id} بنجاح.", reply_markup=back_to_admin())

def process_show_bot_logs(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    bot_id = message.text.strip()
    if bot_id not in bots_manager.get("bots", {}):
        bot.reply_to(message, "❌ البوت غير موجود.", reply_markup=back_to_admin())
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM bot_access_logs WHERE bot_id = ? ORDER BY created_at DESC LIMIT 20", (bot_id,))
        logs = c.fetchall()
        conn.close()
        
        if not logs:
            text = f"📋 لا توجد سجلات للبوت {bot_id}"
        else:
            text = f"📋 <b>سجلات البوت {bot_id}:</b>\n\n"
            for log in logs:
                text += f"🕐 {log[3][:16]}\n"
                text += f"📌 {log[2]}\n"
                text += f"👤 {log[1]}\n\n"
        
        bot.reply_to(message, text, parse_mode="HTML", reply_markup=back_to_admin())
    except:
        bot.reply_to(message, "❌ خطأ في عرض السجلات", reply_markup=back_to_admin())

def show_user_bots(message, user_id):
    user_bots = []
    for bot_id, data in bots_manager.get("bots", {}).items():
        if data.get("user_id") == user_id:
            user_bots.append((bot_id, data))
    
    if not user_bots:
        bot.reply_to(message, "📭 لا يوجد لديك بوتات.", reply_markup=back_button())
        return
    
    text = "<b>🤖 بوتاتي:</b>\n\n"
    for bot_id, data in user_bots:
        status = "🟢 شغال" if bot_id in bots_manager.get("running", []) else "🔴 متوقف"
        remaining = get_bot_remaining_days(bot_id)
        github_path = get_bot_github_path(bot_id) or "غير موجود"
        text += f"🆔 <code>{bot_id}</code>\n"
        text += f"📝 {data.get('name', 'غير معروف')}\n"
        text += f"📊 {status}\n"
        text += f"📅 {remaining}\n"
        text += f"📁 {github_path}\n\n"
    
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=back_button())

# ==================== التوجيه ====================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/') and m.chat.type == 'private')
def forward_to_admin(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        return
    if bot_data.get("tawgeh") == "on":
        try:
            forward = bot.forward_message(ADMIN_ID, user_id, message.message_id)
            app_data["twasol"][str(forward.message_id)] = user_id
            save_data("app.json", app_data)
        except:
            pass

# ============================================================
# تشغيل البوت
# ============================================================
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 جاري تشغيل بوت استضافة البوتات...")
    logger.info(f"👑 المطور: {DEVELOPER}")
    logger.info(f"📢 قناة المطور: {CHANNEL}")
    logger.info(f"📢 قناة البوت: {BOT_CHANNEL}")
    logger.info("=" * 60)
    
    bot.remove_webhook()
    
    # تشغيل مراقبة البوتات
    monitor_thread = threading.Thread(target=monitor_bots, daemon=True)
    monitor_thread.start()
    logger.info("✅ تم تشغيل مراقبة البوتات")
    
    # تشغيل النسخ الاحتياطي التلقائي
    backup_thread = threading.Thread(target=auto_backup, daemon=True)
    backup_thread.start()
    logger.info("✅ تم تشغيل النسخ الاحتياطي التلقائي (كل 24 ساعة)")
    
    # إعادة تشغيل البوتات
    for bot_id in bots_manager.get("running", []):
        if bot_id in bots_manager.get("bots", {}):
            bot_file = os.path.join(BOTS_PATH, bots_manager["bots"][bot_id]["file"])
            if os.path.exists(bot_file):
                start_bot_process(bot_id, bot_file)
                logger.info(f"✅ تم إعادة تشغيل البوت {bot_id}")
    
    logger.info("✅ تم تشغيل البوت بنجاح!")
    logger.info("📱 البوت يعمل الآن...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")