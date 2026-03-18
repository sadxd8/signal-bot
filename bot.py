import json
import os
import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= CONFIG =================
BOT_TOKEN = "8668500995:AAGKBDdW_QQYrQ0gN85__J1ICqGVWdxKc4E"

# 🔥 আপনার PHP API (password সহ হলে pass add করবেন)
SIGNAL_API = "https://sl-team.kesug.com/hacks/period.php"

PASSWORD = "jackhacks55"

ACCESS_FILE = "access_users.json"
CACHE_FILE = "last_signal_cache.json"

COOLDOWN = 15
last_request = {}
# =========================================


# ---------- ACCESS SYSTEM ----------
def load_access():
    if not os.path.exists(ACCESS_FILE):
        with open(ACCESS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(ACCESS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_access(users):
    with open(ACCESS_FILE, "w") as f:
        json.dump(users, f)


# ---------- CACHE ----------
def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return None


# ---------- SIGNAL FETCH ----------
def fetch_signal_once():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (TelegramBot)",
            "Accept": "*/*",
        }

        r = requests.get(
            SIGNAL_API,
            headers=headers,
            timeout=20,
            allow_redirects=True,
        )

        if r.status_code != 200:
            return None

        text = r.text.strip().lstrip("\ufeff")

        # ❌ HTML detect
        if not text or text.startswith("<"):
            return None

        data = json.loads(text)

        required = ["period", "signal", "real-time"]
        for k in required:
            if k not in data:
                return None

        return data

    except:
        return None


def get_signal():
    data = None

    # 🔁 retry 3 times
    for _ in range(3):
        data = fetch_signal_once()
        if data:
            save_cache(data)
            break

    # fallback cache
    if not data:
        cache = load_cache()
        if cache:
            data = cache
            note = "\n⚠️ Cached signal"
        else:
            return "⚠️ Server busy\n⏳ Try again later"
    else:
        note = ""

    return (
        "━━━━━━━━━━━━━━\n"
        "🔥 UNDERWORLD TRADER 🔥\n"
        "━━━━━━━━━━━━━━\n\n"
        f"🕒 Period: `{data['period']}`\n"
        f"📊 Signal: *{data['signal']}*\n"
        f"⏰ Time: `{data['real-time']}`"
        f"{note}"
    )


# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users = load_access()

    if user_id not in users:
        await update.message.reply_text(
            "🔐 *Access Locked*\n\n"
            "Use:\n`/password YOUR_PASSWORD`",
            parse_mode="Markdown"
        )
        return

    keyboard = [[InlineKeyboardButton("🔁 Get New Signal", callback_data="signal")]]

    await update.message.reply_text(
        get_signal(),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------- PASSWORD ----------
async def password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage:\n/password 12345")
        return

    user_id = update.effective_user.id
    users = load_access()

    if context.args[0] == PASSWORD:
        if user_id not in users:
            users.append(user_id)
            save_access(users)

        await update.message.reply_text("✅ Access Granted\n\nUse /start")
    else:
        await update.message.reply_text("❌ Wrong Password")


# ---------- BUTTON ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        await query.answer()
    except:
        pass

    users = load_access()

    if user_id not in users:
        await query.message.reply_text("🔐 Use /password first")
        return

    now = time.time()

    if user_id in last_request:
        if now - last_request[user_id] < COOLDOWN:
            wait = int(COOLDOWN - (now - last_request[user_id]))
            await query.message.reply_text(f"⏳ Wait {wait}s")
            return

    last_request[user_id] = now

    keyboard = [[InlineKeyboardButton("🔁 Get New Signal", callback_data="signal")]]

    await query.message.reply_text(
        get_signal(),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("password", password))
    app.add_handler(CallbackQueryHandler(buttons))

    print("🤖 Bot running on Render...")

    app.run_polling()


if __name__ == "__main__":
    main()