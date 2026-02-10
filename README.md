# EntrepreNO 🚫👔

A Telegram bot that sniffs out spammy entrepreneurs before you accept their LinkedIn request! 

Tired of connection requests from "entrepreneurs" promising financial freedom, passive income, and secret money-making systems? EntrepreNO analyzes LinkedIn profiles and gives you a confidence score on whether that person is likely a spammy entrepreneur or legitimate professional.

## Features ✨

- 🔍 **Profile Analysis**: Analyzes LinkedIn profile information for spam indicators
- 📊 **Spam Confidence Score**: Provides a 0-100% spam likelihood rating
- 🎯 **Detailed Breakdown**: Lists specific reasons and red flags detected
- 🤖 **Easy to Use**: Simple Telegram bot interface - just paste profile info
- 💡 **Smart Detection**: Identifies common patterns in spam profiles:
  - Suspicious keywords (passive income, financial freedom, etc.)
  - Red flag phrases (DM me, ask me how, etc.)
  - Excessive emojis and all-caps text
  - Suspicious connection counts
  - Income claims and get-rich-quick language

## Setup 🛠️

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/botfather))

### Installation

1. Clone this repository:
```bash
git clone https://github.com/rollingchair63/EntrepreNO.git
cd EntrepreNO
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Edit `.env` and add your Telegram Bot Token:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Getting a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided by BotFather
5. Paste it in your `.env` file

## Usage 🚀

### Starting the Bot

Run the bot with:
```bash
python bot.py
```

The bot will start and wait for messages on Telegram.

### Using the Bot

1. Start a chat with your bot on Telegram
2. Send `/start` to see the welcome message
3. Copy a LinkedIn profile's information:
   - Name
   - Headline (the title/description under their name)
   - Number of connections (optional)
   - About/Summary section (optional)
4. Paste it into the chat
5. Get instant spam analysis!

### Example Profile Format

```
John Entrepreneur
💰 CEO & Founder | Helping You Achieve Financial Freedom | DM Me 🚀
500+ connections
I quit my 9-5 and now make 6 figures from home! Ask me how!
```

### Bot Commands

- `/start` - Show welcome message
- `/help` - Get detailed usage instructions
- `/analyze` - Start profile analysis
- `/example` - See example analyses of spam vs. legitimate profiles

## How It Works 🧠

EntrepreNO uses a sophisticated scoring system to detect spam profiles:

1. **Keyword Analysis**: Scans for common spam keywords (entrepreneur, passive income, etc.)
2. **Red Flag Detection**: Looks for suspicious phrases (DM me, ask me how, etc.)
3. **Pattern Recognition**: Identifies excessive emojis, all-caps text, and other spam patterns
4. **Connection Analysis**: Flags suspicious connection counts
5. **Claim Verification**: Detects income claims and get-rich-quick language

Each indicator adds to the spam score, with a final verdict:
- **0-20%**: ✅ Probably Legitimate
- **20-40%**: 😐 Somewhat Suspicious
- **40-60%**: 🤔 Suspicious
- **60-80%**: ⚠️ Likely Spam
- **80-100%**: 🚨 Highly Likely Spam

## Project Structure 📁

```
EntrepreNO/
├── bot.py                 # Main Telegram bot application
├── spam_detector.py       # Spam detection algorithm
├── linkedin_client.py     # LinkedIn integration (placeholder)
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment configuration
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Future Enhancements 🔮

- [ ] LinkedIn API integration for automatic request retrieval
- [ ] Machine learning model for improved detection
- [ ] Database to track analyzed profiles
- [ ] User feedback system to improve accuracy
- [ ] Support for analyzing multiple profiles at once
- [ ] Web dashboard for statistics

## Contributing 🤝

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve spam detection patterns

## Disclaimer ⚠️

This tool provides automated analysis based on common spam patterns. It should be used as a guide, not as the sole decision-making factor. Always use your own judgment when accepting LinkedIn connections.

## License 📄

This project is open source and available for personal and educational use.

## Contact 📧

For questions or suggestions, please open an issue on GitHub.

---

**Made with ❤️ to fight LinkedIn spam**
