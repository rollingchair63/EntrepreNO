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
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from src.services.gmail_service import fetch_connection_requests
from src.services.claude_analyzer import analyze_person, analyze_profile_url, format_analysis_message

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to EntrepreNO Bot!\n\n"
        "I check your LinkedIn connection requests and tell you if they're spammy.\n\n"
        "Commands:\n"
        "/check — scan latest connection requests from Gmail\n"
        "/end — shutdown the bot\n"
        "/help — how to use\n\n"
        "Quick tip: Just type a name like 'John Doe' to research someone!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 How to use:\n\n"
        "Option 1 — Auto scan:\n"
        "  /check\n"
        "  Reads your Gmail for LinkedIn\n"
        "  connection requests and scores\n"
        "  each person automatically.\n\n"
        "Option 2 — Manual lookup:\n"
        "  Just type: John Doe\n"
        "  Or paste a LinkedIn URL\n\n"
        "First time setup:\n"
        "  Run: python -m src.services.gmail_service\n"
        "  to authorize Gmail access."
    )


async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /end command to shutdown the bot."""
    await update.message.reply_text(
        "🛑 Shutting down bot...\nGoodbye! 👋"
    )
    
    # Stop the application gracefully
    application = context.application
    await application.stop()
    await application.shutdown()
    
    # Exit the Python process
    os._exit(0)


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

        person_msg = await update.message.reply_text(f"🔎 Researching {name}...")

        try:
            result = await analyze_person(name, extra)
            response = format_analysis_message(result)
            await person_msg.edit_text(response)
        except Exception as e:
            logger.error(f"Analysis error for {name}: {e}")
            await person_msg.edit_text(f"❌ Could not analyze {name}: {str(e)[:100]}")

        await asyncio.sleep(15)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plain text - detect names or LinkedIn URLs."""
    text = update.message.text.strip()
    
    # Check if it's a LinkedIn URL
    if "linkedin.com/in/" in text:
        msg = await update.message.reply_text("🔎 Fetching profile...")
        try:
            result = await analyze_profile_url(text)
            response = format_analysis_message(result)
            await msg.edit_text(response)
        except Exception as e:
            logger.error(f"URL lookup error: {e}")
            await msg.edit_text(
                f"❌ Could not fetch profile.\n\n"
                f"LinkedIn may be blocking access.\n"
                f"Error: {str(e)[:150]}"
            )
        return
    
    # Check if it looks like a name (2-4 words, title case)
    words = text.split()
    if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
        msg = await update.message.reply_text(f"🔎 Researching {text}...")
        try:
            result = await analyze_person(text)
            response = format_analysis_message(result)
            await msg.edit_text(response)
        except Exception as e:
            logger.error(f"Name lookup error: {e}")
            await msg.edit_text(f"❌ Could not analyze {text}: {str(e)[:100]}")
        return
    
    # Doesn't match any pattern
    await update.message.reply_text(
        "Not sure what to do with that.\n\n"
        "Try:\n"
        "• /check — scan Gmail\n"
        "• Type a name: John Doe\n"
        "• Paste a LinkedIn URL"
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

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_gmail))
    application.add_handler(CommandHandler("end", end_command))
    
    # Plain text handler for names and URLs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    logger.info("EntrepreNO Bot running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()