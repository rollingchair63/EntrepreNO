"""
EntrepreNO Bot — detects spammy LinkedIn connection requests.

Flow:
    /check → reads Gmail for LinkedIn connection emails
           → Claude searches each person on LinkedIn
           → returns verdict: spam or legit
"""

import os
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

# Track users waiting for URL after failed name search
user_waiting_for = {}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to EntrepreNO Bot!\n\n"
        "I check your LinkedIn connection requests and tell you if they're spammy.\n\n"
        "Commands:\n"
        "/check — scan latest connection requests from Gmail\n"
        "/lookup [name or URL] — research someone\n"
        "/help — how to use"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 How to use:\n\n"
        "Option 1 — Auto:\n"
        "  /check\n"
        "  Reads your Gmail for LinkedIn\n"
        "  connection request emails and\n"
        "  scores each person.\n\n"
        "Option 2 — Manual:\n"
        "  /lookup John Doe\n"
        "  /lookup https://linkedin.com/in/...\n"
        "  Research by name or URL.\n"
        "  If name fails, I'll ask for URL.\n\n"
        "First time setup:\n"
        "  Run: python -m src.services.gmail_service\n"
        "  to authorize Gmail access."
    )


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


async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Smart lookup - accepts either a name or LinkedIn URL.
    If name search fails, asks for URL.
    """
    if not context.args:
        await update.message.reply_text(
            "Usage: /lookup [name or URL]\n\n"
            "Examples:\n"
            "• /lookup John Doe\n"
            "• /lookup https://www.linkedin.com/in/john-doe"
        )
        return

    input_text = " ".join(context.args)
    user_id = update.effective_user.id
    
    # Clear any previous waiting state
    if user_id in user_waiting_for:
        del user_waiting_for[user_id]
    
    # Check if it's a URL
    if "linkedin.com/in/" in input_text:
        await lookup_by_url(update, input_text)
    else:
        await lookup_by_name(update, input_text, user_id)


async def lookup_by_url(update, url):
    """Analyze a LinkedIn profile by URL."""
    msg = await update.message.reply_text(f"🔎 Fetching profile...")

    try:
        result = await analyze_profile_url(url)
        response = format_analysis_message(result)
        await msg.edit_text(response)
    except Exception as e:
        logger.error(f"URL lookup error: {e}")
        await msg.edit_text(
            f"❌ Could not fetch profile.\n\n"
            f"LinkedIn may be blocking access.\n"
            f"Error: {str(e)[:150]}"
        )


async def lookup_by_name(update, name, user_id):
    """Analyze by searching for the name. If fails, ask for URL."""
    msg = await update.message.reply_text(f"🔎 Searching for {name}...")

    try:
        result = await analyze_person(name)
        
        # Check if search failed - multiple indicators
        verdict_unclear = result["verdict"] in ("UNCLEAR", "ERROR")
        not_found_phrases = ["not found", "could not locate", "cannot locate", "unable to locate", "unable to find"]
        not_found = any(phrase in result["reason"].lower() for phrase in not_found_phrases)
        
        if (verdict_unclear and not_found) or result["score"] == -1:
            # Search failed - ask for URL
            user_waiting_for[user_id] = name
            await msg.edit_text(
                f"⚠️ Could not find reliable info for {name}.\n\n"
                f"📎 Please send their LinkedIn profile URL\n"
                f"(Just paste the URL, or /cancel to stop)"
            )
        else:
            # Got results - show them
            response = format_analysis_message(result)
            await msg.edit_text(response)
            
    except Exception as e:
        logger.error(f"Name lookup error: {e}")
        user_waiting_for[user_id] = name
        await msg.edit_text(
            f"❌ Search failed for {name}.\n\n"
            f"Error: {str(e)[:100]}\n\n"
            f"📎 Please send their LinkedIn URL\n"
            f"(or /cancel to stop)"
        )


async def handle_url_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL sent after failed name search."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Check if user is waiting for a URL
    if user_id not in user_waiting_for:
        return  # Let other handlers deal with it
    
    name = user_waiting_for[user_id]
    
    # Check if it's a LinkedIn URL
    if "linkedin.com/in/" in text:
        del user_waiting_for[user_id]
        await update.message.reply_text(f"✅ Got it! Analyzing {name}'s profile...")
        await lookup_by_url(update, text)
    else:
        await update.message.reply_text(
            "❌ That doesn't look like a LinkedIn URL.\n\n"
            "Please send a URL like:\n"
            "https://www.linkedin.com/in/username\n\n"
            "Or /cancel to stop"
        )


async def cancel_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel waiting for URL."""
    user_id = update.effective_user.id
    if user_id in user_waiting_for:
        del user_waiting_for[user_id]
        await update.message.reply_text("✅ Cancelled.")
    else:
        await update.message.reply_text("Nothing to cancel.")


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plain text messages as manual name lookups."""
    text = update.message.text.strip()

    # If it looks like a name (2-4 words, title case) treat it as a lookup
    words = text.split()
    if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
        user_id = update.effective_user.id
        msg = await update.message.reply_text(f"🔎 Researching {text}...")
        
        try:
            result = await analyze_person(text)
            
            # Check if search failed
            verdict_unclear = result["verdict"] in ("UNCLEAR", "ERROR")
            not_found = any(phrase in result["reason"].lower() 
                           for phrase in ["not found", "could not locate", "cannot locate", "unable to locate"])
            
            if (verdict_unclear and not_found) or result["score"] == -1:
                user_waiting_for[user_id] = text
                await msg.edit_text(
                    f"⚠️ Could not find {text}.\n\n"
                    f"📎 Send their LinkedIn URL\n"
                    f"(or /cancel to stop)"
                )
            else:
                response = format_analysis_message(result)
                await msg.edit_text(response)
                
        except Exception as e:
            await msg.edit_text(f"❌ Could not analyze {text}: {str(e)[:100]}")
    else:
        await update.message.reply_text(
            "Not sure what to do with that.\n\n"
            "Try:\n"
            "• /check — scan Gmail\n"
            "• /lookup John Doe — research someone\n"
            "• Just type a name like: John Doe"
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

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_gmail))
    application.add_handler(CommandHandler("lookup", lookup))
    application.add_handler(CommandHandler("cancel", cancel_lookup))
    
    # Handle URLs sent after failed lookup (must be before unknown_message)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(r'linkedin\.com/in/'),
        handle_url_reply
    ))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    logger.info("EntrepreNO Bot running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
