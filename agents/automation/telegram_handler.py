#!/usr/bin/env python3
"""
TELEGRAM HANDLER FOR OPENCLAW
Handles voice notes and link submissions from Dibs
Routes to Astra for processing and subagent distribution
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

# Dependencies: pip install python-telegram-bot groq python-dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENCLAW_WORKSPACE = Path(os.getenv("OPENCLAW_WORKSPACE", "~/.openclaw/workspace")).expanduser()

# Initialize clients
groq_client = Groq(api_key=GROQ_API_KEY)
telegram_app = None

# Astra's routing prompt
ASTRA_ROUTER_PROMPT = """You are Astra, Dibs' drill sergeant. Dibs just submitted something to you.

Your job: Analyze what he sent and decide:
1. Is this a voice note rambling? Extract actionable items.
2. Is this a link? Summarize and decide: route to Social Manager for deep analysis?
3. Is this trading/job/dating related? What subagent should handle this?

Respond in JSON format:
{
    "type": "voice_note" | "link" | "journal" | "question",
    "content_summary": "what did he actually say/ask?",
    "actionable_items": ["item1", "item2"],
    "route_to": "social_manager" | "trading_system" | "job_hunt" | "dating_coach" | "self",
    "next_action": "what you'll do with this",
    "message_to_dibs": "what you'll tell him in Telegram"
}
"""

# =============================================================================
# VOICE NOTE HANDLER
# =============================================================================

async def handle_voice_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles voice notes sent to the bot
    1. Download audio file
    2. Transcribe with Groq Whisper
    3. Send to Astra for routing
    4. Report back to Dibs
    """
    
    print(f"[{datetime.now()}] Voice note received from {update.effective_user.username}")
    
    await update.message.reply_text("🎤 Transcribing... one sec")
    
    try:
        # Download voice file
        file = await update.message.voice.get_file()
        voice_path = OPENCLAW_WORKSPACE / "temp" / f"voice_{int(datetime.now().timestamp())}.ogg"
        voice_path.parent.mkdir(parents=True, exist_ok=True)
        await file.download_to_drive(voice_path)
        
        # Transcribe with Groq Whisper
        print(f"  → Transcribing audio file...")
        with open(voice_path, 'rb') as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=(voice_path.name, audio_file, "audio/ogg"),
                model="whisper-large-v3-turbo",
            )
        
        transcript = transcription.text
        print(f"  → Transcript: {transcript[:100]}...")
        
        # Send to Astra for routing
        print(f"  → Routing to Astra...")
        routing_decision = await route_to_astra(
            content=transcript,
            content_type="voice_note",
            raw_data={
                "timestamp": datetime.now().isoformat(),
                "user": update.effective_user.username,
                "message_id": update.message.message_id
            }
        )
        
        # Log to Ledger
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "voice_note",
            "transcript": transcript,
            "routing_decision": routing_decision,
            "status": "processed"
        }
        await log_to_ledger(log_entry)
        
        # Report back to Dibs
        message = routing_decision.get("message_to_dibs", "Got it. Processing...")
        await update.message.reply_text(f"✅ {message}")
        
        # Clean up temp file
        voice_path.unlink()
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        await update.message.reply_text(f"❌ Error processing voice note: {str(e)}")

# =============================================================================
# LINK HANDLER
# =============================================================================

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles link submissions
    1. Extract link from message
    2. Send to Astra for routing
    3. If Social Manager needed, queue for processing
    4. Report back
    """
    
    # Extract link from message
    message_text = update.message.text
    links = [word for word in message_text.split() if word.startswith(('http://', 'https://', 'www.'))]
    
    if not links:
        await update.message.reply_text("📎 No link detected. Send it again?")
        return
    
    link = links[0]
    print(f"[{datetime.now()}] Link received: {link}")
    await update.message.reply_text("🔗 Analyzing link... checking Discord manager")
    
    try:
        # Route to Astra
        routing_decision = await route_to_astra(
            content=link,
            content_type="link",
            raw_data={
                "timestamp": datetime.now().isoformat(),
                "user": update.effective_user.username,
                "message_id": update.message.message_id
            }
        )
        
        # Log to Ledger
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "link_submission",
            "link": link,
            "routing_decision": routing_decision,
            "status": "queued"
        }
        await log_to_ledger(log_entry)
        
        # If Social Manager needed, queue it in Discord
        if routing_decision.get("route_to") == "social_manager":
            await queue_for_social_manager(link)
        
        # Report back
        message = routing_decision.get("message_to_dibs", "Link queued for analysis")
        await update.message.reply_text(f"✅ {message}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        await update.message.reply_text(f"❌ Error processing link: {str(e)}")

# =============================================================================
# VOICE COMMAND HANDLERS
# =============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "🗡️ **Astra Control Center**\n\n"
        "Send me:\n"
        "🎤 Voice notes → I'll transcribe and route\n"
        "🔗 Links → I'll analyze and queue for Social Manager\n"
        "📝 Text → I'll interpret as needed\n\n"
        "Let's go."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status check"""
    # Read memory files
    memory_file = OPENCLAW_WORKSPACE / "MEMORY.md"
    today_file = OPENCLAW_WORKSPACE / f"memory/{datetime.now().strftime('%Y-%m-%d')}.md"
    
    status_msg = "📊 **Status**\n\n"
    
    if memory_file.exists():
        with open(memory_file) as f:
            lines = f.readlines()[:5]
            status_msg += f"Recent memory:\n{''.join(lines)}\n\n"
    
    if today_file.exists():
        with open(today_file) as f:
            lines = f.readlines()[-3:]
            status_msg += f"Today's log:\n{''.join(lines)}"
    
    await update.message.reply_text(status_msg)

# =============================================================================
# ROUTING LOGIC
# =============================================================================

async def route_to_astra(content: str, content_type: str, raw_data: dict) -> dict:
    """
    Send content to Astra for routing decision
    Returns routing decision JSON
    """
    
    prompt = f"""{ASTRA_ROUTER_PROMPT}

Content type: {content_type}
Content: {content}
Raw data: {json.dumps(raw_data, indent=2)}

What should I do with this? Respond ONLY with valid JSON."""
    
    response = groq_client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    
    try:
        routing = json.loads(response.choices[0].message.content)
        return routing
    except json.JSONDecodeError:
        print(f"  ⚠️ Failed to parse Astra routing response")
        return {
            "type": content_type,
            "content_summary": content[:100],
            "route_to": "self",
            "message_to_dibs": "Got it. Processing..."
        }

async def queue_for_social_manager(link: str):
    """
    Queue link for Social Manager to analyze
    Writes to Discord queue or Notion for Beacon to pick up
    """
    
    queue_file = OPENCLAW_WORKSPACE / "discord" / "link_queue.json"
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    
    queue_entry = {
        "timestamp": datetime.now().isoformat(),
        "link": link,
        "status": "pending",
        "priority": "normal"
    }
    
    # Read existing queue
    if queue_file.exists():
        with open(queue_file) as f:
            queue = json.load(f)
    else:
        queue = []
    
    # Add new entry
    queue.append(queue_entry)
    
    # Write back
    with open(queue_file, 'w') as f:
        json.dump(queue, f, indent=2)
    
    print(f"  → Queued for Social Manager: {link}")

async def log_to_ledger(entry: dict):
    """
    Write entry to daily ledger file
    Ledger runs separately and aggregates these
    """
    
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = OPENCLAW_WORKSPACE / "memory" / f"{today}.md"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    log_line = f"\n[{datetime.now().isoformat()}] {entry.get('type', 'unknown')}: {entry.get('status', 'processed')}\n"
    
    with open(log_file, 'a') as f:
        f.write(log_line)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

async def main():
    """Start the Telegram bot"""
    
    global telegram_app
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    print(f"🤖 Starting Telegram handler...")
    print(f"   Workspace: {OPENCLAW_WORKSPACE}")
    print(f"   Bot token: {TELEGRAM_BOT_TOKEN[:20]}...")
    
    # Create application
    telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("status", status))
    telegram_app.add_handler(MessageHandler(filters.VOICE, handle_voice_note))
    telegram_app.add_handler(MessageHandler(filters.Regex(r'https?://|www\.'), handle_link))
    
    # Start bot
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    
    print("✅ Telegram handler running")
    print("   Waiting for voice notes and links...")
    
    # Keep running
    await asyncio.Event().wait()

# =============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down telegram handler...")
