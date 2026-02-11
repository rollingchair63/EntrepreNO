"""
EntrepreNO Bot — detects spammy LinkedIn connection requests.

Flow:
    /check → reads Gmail for LinkedIn connection emails
           → Claude searches each person on LinkedIn
           → returns verdict: spam or legit
"""

import os
import sys
import logging
from dotenv import load_dotenv
import asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.services.gmail_service import fetch_connection_requests
from src.services.claude_analyzer import analyze_person, format_analysis_message

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cache for analysis results to prevent inconsistent verdicts
# Key: person name (lowercase), Value: analysis result dict
analysis_cache = {}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to EntrepreNO Bot!\n\n"
        "I check your LinkedIn connection requests and tell you if they're spammy.\n\n"
        "Use /check to scan your Gmail for connection requests."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 How to use:\n\n"
        "Use /check to scan your Gmail for LinkedIn connection requests.\n"
        "I'll analyze each person and tell you if they're spammy.\n\n"
        "First time setup:\n"
        "Run: `python -m src.services.gmail_service`\n"
        "to authorize Gmail access.",
        parse_mode="Markdown"
    )


async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /end command to shutdown the bot."""
    await update.message.reply_text(
        "🛑 Shutting down bot...\nGoodbye! 👋"
    )
    
    # Stop the application gracefully
    application = context.application
    
    # Schedule shutdown after message is sent
    import asyncio
    async def delayed_shutdown():
        await asyncio.sleep(1)  # Give time for message to send
        await application.stop()
        await application.shutdown()
        # Force exit - kills all threads including health check
        import sys
        sys.exit(0)
    
    asyncio.create_task(delayed_shutdown())


async def check_gmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch LinkedIn connection request emails and analyze each person."""
    msg = await update.message.reply_text("📬 Checking Gmail...")

    try:
        requests = fetch_connection_requests(max_results=10)
    except FileNotFoundError:
        await msg.edit_text(
            "❌ Gmail not authorized yet.\n\n"
            "Run this once in your terminal:\n"
            "`python -m src.services.gmail_service`"
        )
        return
    except Exception as e:
        logger.error(f"Gmail fetch error: {e}")
        await msg.edit_text(f"❌ Gmail error: {str(e)[:200]}")
        return

    if not requests:
        await msg.edit_text(
            "📭 No new LinkedIn connection request emails found.\n\n"
            "Make sure LinkedIn email notifications are enabled."
        )
        return

    await msg.edit_text(f"🔍 Found {len(requests)} request(s). Researching each one...")

    for i, req in enumerate(requests, 1):
        name = req["name"]
        extra = req.get("extra_info")
        cache_key = name.lower()

        person_msg = await update.message.reply_text(f"🔎 Researching {name}...")

        try:
            # Check cache first
            if cache_key in analysis_cache:
                logger.info(f"Using cached result for {name}")
                result = analysis_cache[cache_key]
            else:
                # Analyze and cache
                result = await analyze_person(name, extra)
                analysis_cache[cache_key] = result
                logger.info(f"Cached new result for {name}")
            
            response = format_analysis_message(result)
            await person_msg.edit_text(response, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Analysis error for {name}: {e}")
            await person_msg.edit_text(f"❌ Could not analyze {name}: {str(e)[:100]}")

        await asyncio.sleep(15)


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirect users who send anything other than commands."""
    await update.message.reply_text(
        "⚠️ Bot is not running or I only respond to commands.\n\n"
        "To start the bot:\n"
        "1. Open terminal/VSCode\n"
        "2. Activate venv: `source venv/bin/activate` (Mac/Linux)\n"
        "   or `venv\\Scripts\\activate` (Windows)\n"
        "3. Run: `python bot.py`\n\n"
        "Once running, available commands:\n"
        "/check — scan Gmail for connection requests\n"
        "/help — show instructions\n"
        "/end — shutdown bot",
        parse_mode="Markdown"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in .env!")
        return

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        logger.error("ANTHROPIC_API_KEY not set in .env!")
        return

    # Health check server for Render
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class HealthCheck(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running")
        def log_message(self, format, *args):
            pass

    def run_health_server():
        port = int(os.getenv("PORT", 10000))
        server = HTTPServer(("0.0.0.0", port), HealthCheck)
        logger.info(f"Health check on port {port}")
        server.serve_forever()

    threading.Thread(target=run_health_server, daemon=True).start()

    # Build bot
    application = Application.builder().token(token).build()

    # Command handlers only - no text handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_gmail))
    application.add_handler(CommandHandler("end", end_command))
    
    # Catch-all for any non-command text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))

    # Set bot commands menu (appears at bottom of Telegram chat)
    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands([
            ("start", "Start the bot"),
            ("check", "Scan Gmail for LinkedIn requests"),
            ("help", "Show instructions"),
            ("end", "Shutdown the bot"),
        ])
    
    application.post_init = post_init

    logger.info("EntrepreNO Bot running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()