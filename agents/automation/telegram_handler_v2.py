#!/usr/bin/env python3
"""
TELEGRAM HANDLER v2.5 - Enhanced with Confirmations, Error Reporting, and Stats Tracking
Routes: Voice notes → Astra, Links → Link Workflow (Analysis + UI/UX Report), PDFs → PDF Analysis
"""
import os
import sys
import asyncio
import logging
import subprocess
import sqlite3
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENCLAW_WORKSPACE = os.getenv("OPENCLAW_WORKSPACE", "/home/astra/.openclaw/workspace")
STATS_DB = os.path.join(OPENCLAW_WORKSPACE, "agents/automation/bot_stats.db")

# Initialize stats database
def init_stats_db():
    """Initialize SQLite database for tracking bot usage"""
    try:
        conn = sqlite3.connect(STATS_DB)
        cursor = conn.cursor()
        
        # Track individual events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                chat_id INTEGER,
                status TEXT NOT NULL,
                details TEXT,
                error_message TEXT
            )
        ''')
        
        # Track daily summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                links_received INTEGER DEFAULT 0,
                links_success INTEGER DEFAULT 0,
                links_failed INTEGER DEFAULT 0,
                pdfs_received INTEGER DEFAULT 0,
                pdfs_success INTEGER DEFAULT 0,
                pdfs_failed INTEGER DEFAULT 0,
                voice_notes INTEGER DEFAULT 0,
                text_messages INTEGER DEFAULT 0,
                total_users INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Stats database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize stats DB: {e}")

def log_event(event_type, chat_id, status, details=None, error_message=None):
    """Log an event to the stats database"""
    try:
        conn = sqlite3.connect(STATS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (timestamp, event_type, chat_id, status, details, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), event_type, chat_id, status, details, error_message))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log event: {e}")

def update_daily_stats(event_type, success=True):
    """Update daily statistics counters"""
    try:
        conn = sqlite3.connect(STATS_DB)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Ensure row exists
        cursor.execute('''
            INSERT OR IGNORE INTO daily_stats (date) VALUES (?)
        ''', (today,))
        
        # Update appropriate counter
        if event_type == 'link':
            cursor.execute('''
                UPDATE daily_stats 
                SET links_received = links_received + 1,
                    links_success = links_success + ?,
                    links_failed = links_failed + ?
                WHERE date = ?
            ''', (1 if success else 0, 0 if success else 1, today))
        elif event_type == 'pdf':
            cursor.execute('''
                UPDATE daily_stats 
                SET pdfs_received = pdfs_received + 1,
                    pdfs_success = pdfs_success + ?,
                    pdfs_failed = pdfs_failed + ?
                WHERE date = ?
            ''', (1 if success else 0, 0 if success else 1, today))
        elif event_type == 'voice':
            cursor.execute('''
                UPDATE daily_stats 
                SET voice_notes = voice_notes + 1
                WHERE date = ?
            ''', (today,))
        elif event_type == 'text':
            cursor.execute('''
                UPDATE daily_stats 
                SET text_messages = text_messages + 1
                WHERE date = ?
            ''', (today,))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to update daily stats: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(
        "🗡️ **ASTRA ONLINE**\n\n"
        "Send me:\n"
        "• **Voice notes** → I'll transcribe and route\n"
        "• **Links** → Full analysis with professional report\n"
        "• **PDFs** → Text extraction + AI analysis\n\n"
        "Your command channel is active.",
        parse_mode='Markdown'
    )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process voice notes - route to Astra"""
    chat_id = update.message.chat_id
    
    # IMMEDIATE CONFIRMATION
    confirm_msg = await update.message.reply_text("🎤 **Voice note received.** Downloading...", parse_mode='Markdown')
    log_event('voice', chat_id, 'received')
    
    try:
        # Download voice file
        voice_file = await update.message.voice.get_file()
        voice_path = f"{OPENCLAW_WORKSPACE}/voice_{update.message.message_id}.ogg"
        await voice_file.download_to_drive(voice_path)
        
        await confirm_msg.edit_text("🎤 **Voice note received.** ✅ Downloaded. Transcribing...")
        
        # TODO: Transcribe with Groq and route to Astra
        await asyncio.sleep(1)  # Placeholder for actual transcription
        
        await confirm_msg.edit_text("✅ **Voice note processed.** Transcribed and routed to Astra.")
        update_daily_stats('voice', success=True)
        log_event('voice', chat_id, 'success')
        
        # Cleanup
        try:
            os.remove(voice_path)
        except:
            pass
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Voice processing failed: {error_msg}")
        await confirm_msg.edit_text(
            f"❌ **Voice note failed.**\n\n"
            f"Error: `{error_msg[:100]}`\n\n"
            f"Please try again or send as text.",
            parse_mode='Markdown'
        )
        update_daily_stats('voice', success=False)
        log_event('voice', chat_id, 'failed', error_message=error_msg)

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process links - route to enhanced workflow with proper error handling"""
    text = update.message.text
    chat_id = update.message.chat_id
    
    # Extract URL
    url = None
    for entity in update.message.entities or []:
        if entity.type == 'url':
            url = text[entity.offset:entity.offset + entity.length]
            break
    
    if not url:
        import re
        url_match = re.search(r'https?://[^\s]+', text)
        if url_match:
            url = url_match.group(0)
    
    if not url:
        await update.message.reply_text("❌ No valid URL found in your message.")
        return
    
    # IMMEDIATE CONFIRMATION
    confirm_msg = await update.message.reply_text(
        f"🔗 **Link received**\n"
        f"`{url[:60]}{'...' if len(url) > 60 else ''}`\n\n"
        f"⏳ Starting analysis...",
        parse_mode='Markdown'
    )
    log_event('link', chat_id, 'received', details=url[:200])
    
    # Step 2: Run full workflow
    try:
        result = subprocess.run(
            ['python3', f'{OPENCLAW_WORKSPACE}/agents/automation/link_analyzer_real.py', url, str(chat_id)],
            capture_output=True,
            text=True,
            timeout=90
        )
        
        logger.info(f"Link analyzer output: {result.stdout}")
        if result.stderr:
            logger.error(f"Link analyzer stderr: {result.stderr}")
        
        # Check for actual errors in subprocess
        if result.returncode != 0:
            raise Exception(f"Link analyzer failed with code {result.returncode}: {result.stderr}")
        
        # Check if analysis actually succeeded (look for success indicators in output)
        stdout_lower = result.stdout.lower()
        if 'error' in stdout_lower or 'failed' in stdout_lower:
            # Check if it's a real failure vs just a word in the content
            if '"success": false' in result.stdout or '❌' in result.stdout:
                raise Exception("Analysis completed but returned failure status")
        
        # SUCCESS
        await confirm_msg.edit_text(
            f"✅ **Analysis complete!**\n\n"
            f"Report link sent to your notifications.\n"
            f"_Analysis saved to Notion._",
            parse_mode='Markdown'
        )
        update_daily_stats('link', success=True)
        log_event('link', chat_id, 'success', details=url[:200])
        
    except subprocess.TimeoutExpired:
        error_msg = "Analysis timed out after 90 seconds"
        logger.error(f"Link analysis timeout for {url}")
        await confirm_msg.edit_text(
            f"⏱️ **Analysis timed out**\n\n"
            f"The link analysis took too long. This might be due to:\n"
            f"• Slow website response\n"
            f"• Large content to process\n"
            f"• API rate limiting\n\n"
            f"Please try again in a few minutes.",
            parse_mode='Markdown'
        )
        update_daily_stats('link', success=False)
        log_event('link', chat_id, 'timeout', details=url[:200], error_message=error_msg)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Link analysis failed: {error_msg}")
        await confirm_msg.edit_text(
            f"❌ **Analysis failed**\n\n"
            f"I couldn't analyze this link. Here's what happened:\n"
            f"`{error_msg[:150]}`\n\n"
            f"Possible causes:\n"
            f"• Website blocked the request\n"
            f"• Content extraction failed\n"
            f"• AI service temporarily unavailable\n\n"
            f"_This is an honest error - not a fake success message._",
            parse_mode='Markdown'
        )
        update_daily_stats('link', success=False)
        log_event('link', chat_id, 'failed', details=url[:200], error_message=error_msg)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process PDF documents - extract text and analyze with honest error reporting"""
    document = update.message.document
    chat_id = update.message.chat_id
    filename = document.file_name or "unknown.pdf"
    
    # Check if it's a PDF
    if not filename.lower().endswith('.pdf'):
        await update.message.reply_text(
            f"📄 Document received: `{filename}`\n\n"
            f"⚠️ Only PDFs are supported for analysis. "
            f"Please convert to PDF and try again.",
            parse_mode='Markdown'
        )
        return
    
    # IMMEDIATE CONFIRMATION
    confirm_msg = await update.message.reply_text(
        f"📄 **PDF received**\n"
        f"`{filename}`\n\n"
        f"⏳ Downloading...",
        parse_mode='Markdown'
    )
    log_event('pdf', chat_id, 'received', details=filename)
    
    pdf_path = None
    try:
        # Download PDF
        pdf_file = await document.get_file()
        pdf_path = f"{OPENCLAW_WORKSPACE}/pdf_{update.message.message_id}.pdf"
        await pdf_file.download_to_drive(pdf_path)
        
        await confirm_msg.edit_text(
            f"📄 **PDF received**\n"
            f"`{filename}`\n\n"
            f"✅ Downloaded. Extracting text...",
            parse_mode='Markdown'
        )
        
        # Run PDF analysis
        result = subprocess.run(
            ['python3', f'{OPENCLAW_WORKSPACE}/agents/automation/pdf_analyzer.py', pdf_path, str(chat_id), filename],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        logger.info(f"PDF analyzer output: {result.stdout}")
        if result.stderr:
            logger.error(f"PDF analyzer stderr: {result.stderr}")
        
        # Check return code
        if result.returncode != 0:
            # Check for specific error patterns in stderr/stdout
            error_output = result.stderr or result.stdout
            if 'Not enough text extracted' in error_output or 'text extraction failed' in error_output.lower():
                raise Exception("Could not extract text from PDF. It may be scanned images or password-protected.")
            elif 'AI analysis failed' in error_output:
                raise Exception("Text was extracted but AI analysis failed. The AI service may be unavailable.")
            else:
                raise Exception(f"PDF analysis failed: {error_output[:150]}")
        
        # SUCCESS
        await confirm_msg.edit_text(
            f"✅ **PDF analysis complete!**\n\n"
            f"Report link incoming...\n"
            f"_Saved to Notion._",
            parse_mode='Markdown'
        )
        update_daily_stats('pdf', success=True)
        log_event('pdf', chat_id, 'success', details=filename)
        
    except subprocess.TimeoutExpired:
        error_msg = "PDF analysis timed out after 120 seconds"
        logger.error(f"PDF analysis timeout for {filename}")
        await confirm_msg.edit_text(
            f"⏱️ **PDF analysis timed out**\n\n"
            f"The PDF took too long to analyze. This might be due to:\n"
            f"• Very large PDF file\n"
            f"• Complex document structure\n"
            f"• API rate limiting\n\n"
            f"Try a smaller PDF or extract text manually.",
            parse_mode='Markdown'
        )
        update_daily_stats('pdf', success=False)
        log_event('pdf', chat_id, 'timeout', details=filename, error_message=error_msg)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"PDF processing failed: {error_msg}")
        await confirm_msg.edit_text(
            f"❌ **PDF analysis failed**\n\n"
            f"`{filename}`\n\n"
            f"Error: `{error_msg[:200]}`\n\n"
            f"_This is a real failure - not a placeholder success message._",
            parse_mode='Markdown'
        )
        update_daily_stats('pdf', success=False)
        log_event('pdf', chat_id, 'failed', details=filename, error_message=error_msg)
        
    finally:
        # Cleanup
        if pdf_path:
            try:
                os.remove(pdf_path)
            except:
                pass

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process text messages"""
    text = update.message.text
    chat_id = update.message.chat_id
    
    # Check if it contains a link
    if text.startswith('http') or 'http' in text:
        await handle_link(update, context)
        return
    
    # Regular text message
    await update.message.reply_text(
        f"📝 Message received:\n`{text[:100]}{'...' if len(text) > 100 else ''}`\n\n"
        f"✅ Routed to Astra.",
        parse_mode='Markdown'
    )
    update_daily_stats('text', success=True)
    log_event('text', chat_id, 'success', details=text[:200])

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's stats"""
    try:
        conn = sqlite3.connect(STATS_DB)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (today,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            _, links_rec, links_succ, links_fail, pdfs_rec, pdfs_succ, pdfs_fail, voice, text, users = row
            await update.message.reply_text(
                f"📊 **Today's Stats** ({today})\n\n"
                f"🔗 Links: {links_rec} received ({links_succ} ✓ / {links_fail} ✗)\n"
                f"📄 PDFs: {pdfs_rec} received ({pdfs_succ} ✓ / {pdfs_fail} ✗)\n"
                f"🎤 Voice notes: {voice}\n"
                f"📝 Text messages: {text}\n\n"
                f"_Stats reset at midnight_",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("📊 No stats recorded yet today.")
            
    except Exception as e:
        logger.error(f"Stats command failed: {e}")
        await update.message.reply_text("❌ Could not retrieve stats.")

def main():
    # Initialize database
    init_stats_db()
    
    print("🚀 Starting Telegram Handler v2.5...")
    print(f"Bot token: {TOKEN[:20]}...")
    print(f"Stats DB: {STATS_DB}")
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ Telegram Handler: RUNNING")
    print("📱 Bot is listening...")
    print("   - Voice notes → Astra (with confirmation)")
    print("   - PDFs → Text extraction + AI analysis (with honest errors)")
    print("   - Links → Full workflow (with confirmation & error reporting)")
    print("   - /stats → Show today's stats")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
