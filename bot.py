"""
Telegram bot for detecting spammy LinkedIn entrepreneurs.
"""

import os
import logging
from typing import Dict
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from spam_detector import analyze_linkedin_profile
from linkedin_client import parse_profile_manually, create_sample_profile


# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class EntrepreNOBot:
    """Telegram bot for analyzing LinkedIn profiles."""
    
    def __init__(self, token: str):
        """Initialize the bot with the given token."""
        self.token = token
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        welcome_message = (
            "👋 Welcome to EntrepreNO Bot!\n\n"
            "I help you detect spammy entrepreneurs before you accept their LinkedIn requests.\n\n"
            "🔍 How to use:\n"
            "1. Copy the LinkedIn profile information (name, headline, etc.)\n"
            "2. Send it to me as a message\n"
            "3. I'll analyze it and give you a spam confidence rating!\n\n"
            "📝 Commands:\n"
            "/start - Show this welcome message\n"
            "/help - Get help on how to use the bot\n"
            "/analyze - Analyze a LinkedIn profile\n"
            "/example - See example analyses\n\n"
            "Just paste the LinkedIn profile info to get started!"
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command."""
        help_message = (
            "📖 How to use EntrepreNO Bot:\n\n"
            "1️⃣ Go to LinkedIn and find a connection request\n"
            "2️⃣ Copy the person's information:\n"
            "   - Name\n"
            "   - Headline (the text under their name)\n"
            "   - Number of connections\n"
            "   - Summary/About section (optional)\n\n"
            "3️⃣ Paste it here in this format:\n"
            "```\n"
            "John Doe\n"
            "CEO at StartupXYZ | Entrepreneur | Investor\n"
            "500+ connections\n"
            "I help people achieve financial freedom...\n"
            "```\n\n"
            "4️⃣ I'll analyze it and tell you if it's spam!\n\n"
            "💡 Tip: You can send just the headline if that's all you have.\n\n"
            "Use /example to see some sample analyses."
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /analyze command."""
        message = (
            "📊 Ready to analyze!\n\n"
            "Please send me the LinkedIn profile information:\n"
            "- Name\n"
            "- Headline\n"
            "- Connections (optional)\n"
            "- Summary (optional)\n\n"
            "I'll analyze it for spam indicators!"
        )
        await update.message.reply_text(message)
    
    async def example_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /example command - show sample analyses."""
        # Example 1: Obvious spam
        spam_profile = create_sample_profile(
            name="Rick Success",
            headline="💰 CEO & Founder | Helping You Achieve Financial Freedom | DM Me To Learn How I Made $10K/Month 🚀",
            connections=156,
            summary="Changed my life and quit my 9-5! Now I help others do the same. Limited spots available!"
        )
        spam_result = analyze_linkedin_profile(spam_profile)
        
        example1 = (
            "🔴 Example 1: SPAM Profile\n\n"
            f"Name: {spam_profile['name']}\n"
            f"Headline: {spam_profile['headline']}\n"
            f"Connections: {spam_profile['connections']}\n\n"
            f"📊 Spam Score: {spam_result['score']}%\n"
            f"{spam_result['verdict']}\n\n"
            f"Reasons:\n"
        )
        for reason in spam_result['reasons']:
            example1 += f"• {reason}\n"
        
        # Example 2: Legitimate profile
        legit_profile = create_sample_profile(
            name="Sarah Johnson",
            headline="Software Engineer at Google | Python, ML, AI",
            connections=847,
            summary="Passionate about building scalable systems and machine learning applications."
        )
        legit_result = analyze_linkedin_profile(legit_profile)
        
        example2 = (
            "\n\n🟢 Example 2: LEGITIMATE Profile\n\n"
            f"Name: {legit_profile['name']}\n"
            f"Headline: {legit_profile['headline']}\n"
            f"Connections: {legit_profile['connections']}\n\n"
            f"📊 Spam Score: {legit_result['score']}%\n"
            f"{legit_result['verdict']}\n\n"
            f"Reasons:\n"
        )
        for reason in legit_result['reasons']:
            example2 += f"• {reason}\n"
        
        await update.message.reply_text(example1 + example2)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular text messages containing profile information."""
        text = update.message.text
        
        # Send "analyzing..." message
        analyzing_msg = await update.message.reply_text("🔍 Analyzing profile...")
        
        try:
            # Parse the profile information
            profile_data = parse_profile_manually(text)
            
            # If no meaningful data was parsed, provide guidance
            if not profile_data['name'] and not profile_data['headline']:
                await analyzing_msg.edit_text(
                    "❌ I couldn't parse the profile information.\n\n"
                    "Please send the profile in this format:\n"
                    "Name\n"
                    "Headline/Title\n"
                    "Number of connections (optional)\n"
                    "Summary (optional)\n\n"
                    "Or use /help for more information."
                )
                return
            
            # Analyze the profile
            result = analyze_linkedin_profile(profile_data)
            
            # Format the response
            response = self._format_analysis_result(profile_data, result)
            
            # Send the result
            await analyzing_msg.edit_text(response)
            
        except Exception as e:
            logger.error(f"Error analyzing profile: {e}")
            await analyzing_msg.edit_text(
                "❌ An error occurred while analyzing the profile.\n"
                "Please try again or use /help for guidance."
            )
    
    def _format_analysis_result(self, profile_data: Dict, result: Dict) -> str:
        """Format the analysis result into a readable message."""
        score = result['score']
        verdict = result['verdict']
        reasons = result['reasons']
        
        # Create progress bar for score
        filled = int(score / 10)
        bar = '█' * filled + '░' * (10 - filled)
        
        message = (
            "🎯 LinkedIn Profile Analysis\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        if profile_data.get('name'):
            message += f"👤 Name: {profile_data['name']}\n"
        if profile_data.get('headline'):
            message += f"💼 Headline: {profile_data['headline']}\n"
        if profile_data.get('connections'):
            message += f"🔗 Connections: {profile_data['connections']}\n"
        
        message += (
            f"\n📊 Spam Score: {score}%\n"
            f"{bar} {score}%\n\n"
            f"{verdict}\n\n"
            f"📋 Analysis Details:\n"
        )
        
        for reason in reasons:
            message += f"• {reason}\n"
        
        # Add recommendation
        if score >= 60:
            message += (
                "\n⚠️ Recommendation:\n"
                "This profile shows significant spam indicators. "
                "Consider declining this connection request."
            )
        elif score >= 40:
            message += (
                "\n💭 Recommendation:\n"
                "This profile has some suspicious elements. "
                "Review their profile carefully before accepting."
            )
        else:
            message += (
                "\n✅ Recommendation:\n"
                "This profile appears relatively normal. "
                "Use your judgment as always!"
            )
        
        return message
    
    def run(self) -> None:
        """Run the bot."""
        # Create the Application
        self.application = Application.builder().token(self.token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        self.application.add_handler(CommandHandler("example", self.example_command))
        
        # Add message handler for profile analysis
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # Start the bot
        logger.info("Starting EntrepreNO Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main function to run the bot."""
    # Get bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your bot token.")
        logger.error("See .env.example for reference.")
        return
    
    # Create and run the bot
    bot = EntrepreNOBot(token)
    bot.run()


if __name__ == '__main__':
    main()
