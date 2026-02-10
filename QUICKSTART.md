# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Create Your Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` 
3. Follow the prompts to choose a name and username
4. Copy the bot token provided

### Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your bot token:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Step 4: Run the Bot

```bash
python bot.py
```

### Step 5: Test It Out!

1. Find your bot on Telegram
2. Send `/start` to begin
3. Try these test profiles:

**Spam Example:**
```
Rick Money
💰 CEO & Founder | Financial Freedom Coach | DM Me! 🚀
156 connections
I quit my 9-5! Ask me how!
```

**Legitimate Example:**
```
Alice Johnson
Senior Software Engineer at Google
847 connections
Building scalable ML systems
```

## 🎮 Try the Demo First

Want to see it in action without setting up Telegram? Run:

```bash
python simple_demo.py
```

This will show you example analyses of spam vs. legitimate profiles!

## 📱 Using the Bot

Once your bot is running:

1. Open Telegram and find your bot
2. Send `/start` to see the welcome message
3. Copy LinkedIn profile info (name, headline, connections, summary)
4. Paste it to the bot
5. Get instant spam analysis!

### Bot Commands

- `/start` - Welcome message
- `/help` - Detailed instructions
- `/example` - See example analyses
- `/analyze` - Start analysis

## 🔍 How to Get LinkedIn Profile Info

1. Go to the LinkedIn connection request
2. Click on the person's name to view their profile
3. Copy:
   - Their name
   - The headline (text right under their name)
   - Connection count (e.g., "500+ connections")
   - About section (optional)
4. Paste all of it into the bot

## 💡 Tips

- You can send just the headline if that's all you need to analyze
- The more information you provide, the more accurate the analysis
- The bot works best with English profiles
- Scores above 60% are usually spam

## 🛠️ Troubleshooting

**Bot not responding?**
- Check your bot token is correct in `.env`
- Make sure the bot is running (`python bot.py`)
- Check the console for error messages

**Can't find the bot on Telegram?**
- Search for the exact username you gave it
- Make sure you're searching in the right Telegram account

**Analysis seems off?**
- Remember it's a tool to assist, not replace your judgment
- Some legitimate entrepreneurs may score higher
- Consider the context of the profile

## 📊 Understanding Scores

- **0-20%**: ✅ Probably Legitimate
- **20-40%**: 😐 Minor Red Flags
- **40-60%**: 🤔 Be Careful
- **60-80%**: ⚠️ Likely Spam
- **80-100%**: 🚨 Highly Likely Spam

---

Need more help? Check the main [README.md](README.md) for full documentation!
