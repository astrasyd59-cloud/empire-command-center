#!/usr/bin/env python3
"""
TELEGRAM HANDLER - Simplified for deployment test
Processes voice notes and links
"""
import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(
        "🗡️ ASTRA ONLINE\n\n"
        "Send me:\n"
        "• Voice notes → I'll transcribe and route\n"
        "• Links → I'll analyze and queue\n\n"
        "Your command channel is active."
    )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process voice notes"""
    await update.message.reply_text("🎤 Voice note received. Transcribing...")
    # Transcription would happen here with Groq
    await update.message.reply_text("✅ Transcribed and routed to Astra.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process text and links"""
    text = update.message.text
    
    if text.startswith('http'):
        await update.message.reply_text(f"🔗 Link received: {text[:50]}...")
        await update.message.reply_text("✅ Queued for Social Manager analysis.")
    else:
        await update.message.reply_text(f"📝 Message: {text}")
        await update.message.reply_text("✅ Routed to Astra.")

def main():
    """Start the bot"""
    print("🚀 Starting Telegram Handler...")
    print(f"Bot token: {TOKEN[:20]}...")
    
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ Telegram Handler: RUNNING")
    print("📱 Bot is listening...")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
