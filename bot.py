"""
Telegram bot for detecting spammy LinkedIn entrepreneurs.
"""

import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from spam_detector import analyze_linkedin_profile
from linkedin_client import parse_profile_manually, create_sample_profile

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Command Handlers

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message."""
    await update.message.reply_text(
        "👋 Welcome to EntrepreNO Bot!\n\n"
        "Send me LinkedIn profile info and I'll detect if it's spammy.\n\n"
        "Commands:\n"
        "/help - How to use\n"
        "/example - See examples"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help."""
    await update.message.reply_text(
        "📖 How to use:\n\n"
        "1. Copy LinkedIn profile info:\n"
        "   • Name\n"
        "   • Headline\n"
        "   • Connections (optional)\n\n"
        "2. Paste it here\n\n"
        "3. Get spam analysis!\n\n"
        "Example:\n"
        "John Doe\n"
        "CEO at StartupXYZ | Entrepreneur\n"
        "500+ connections"
    )


async def example(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show example analyses."""
    # Spam example
    spam = create_sample_profile(
        name="Rick Success",
        headline="💰 CEO | Financial Freedom | DM Me To Learn How I Made $10K/Month 🚀",
        connections=156,
        summary="Changed my life and quit my 9-5! Limited spots available!"
    )
    spam_result = analyze_linkedin_profile(spam)
    
    # Legit example
    legit = create_sample_profile(
        name="Sarah Johnson",
        headline="Software Engineer at Google | Python, ML, AI",
        connections=847,
        summary="Passionate about building scalable systems."
    )
    legit_result = analyze_linkedin_profile(legit)
    
    message = (
        f"🔴 SPAM ({spam_result['score']}%)\n"
        f"{spam['headline']}\n"
        f"→ {spam_result['verdict']}\n\n"
        f"🟢 LEGIT ({legit_result['score']}%)\n"
        f"{legit['headline']}\n"
        f"→ {legit_result['verdict']}"
    )
    
    await update.message.reply_text(message)

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """End message."""
    await update.message.reply_text(
        "👋 Thanks for using EntrepreNO Bot!\n"
        "Feel free to reach out if you have any questions."
    )

async def analyze_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze LinkedIn profile from message."""
    text = update.message.text
    
    # Show analyzing message
    msg = await update.message.reply_text("🔍 Analyzing...")
    
    try:
        # Parse profile
        profile = parse_profile_manually(text)
        
        if not profile['name'] and not profile['headline']:
            await msg.edit_text(
                "❌ Couldn't parse profile.\n\n"
                "Send it like this:\n"
                "Name\n"
                "Headline\n"
                "Connections (optional)"
            )
            return
        
        # Analyze
        result = analyze_linkedin_profile(profile)
        
        # Format response
        score = result['score']
        filled = int(score / 10)
        bar = '█' * filled + '░' * (10 - filled)
        
        response = "🎯 Analysis\n" + "━" * 20 + "\n\n"
        
        if profile.get('name'):
            response += f"👤 {profile['name']}\n"
        if profile.get('headline'):
            response += f"💼 {profile['headline']}\n"
        if profile.get('connections'):
            response += f"🔗 {profile['connections']}\n"
        
        response += f"\n📊 Spam Score: {score}%\n{bar}\n\n{result['verdict']}\n\n"
        
        for reason in result['reasons']:
            response += f"• {reason}\n"
        
        # Add recommendation
        if score >= 60:
            response += "\n⚠️ High spam risk - consider declining"
        elif score >= 40:
            response += "\n💭 Some red flags - review carefully"
        else:
            response += "\n✅ Looks relatively normal"
        
        await msg.edit_text(response)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text("❌ Error analyzing profile. Try /help")


def main():
    """Run the bot."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file!")
        return
    
    # Create application
    app = Application.builder().token(token).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("example", example))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_profile))
    
    # Run
    logger.info("Starting EntrepreNO Bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()