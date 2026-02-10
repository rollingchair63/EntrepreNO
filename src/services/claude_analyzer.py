"""
Claude-powered LinkedIn profile analyzer.
Uses the Anthropic API with web search to research a person
and determine if they're a spammy entrepreneur.
"""

import os
import logging
import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an assistant that helps determine whether a LinkedIn connection request 
is from a spammy entrepreneur or a legitimate professional.

When given a person's name, you will:
1. Search for their LinkedIn profile
2. Look at their headline, bio, job history, and any posts
3. Identify red flags like: MLM/network marketing, "financial freedom", "DM me", 
   passive income claims, life/business coaching with no real credentials,
   cryptocurrency/forex trading, dropshipping, "quit my 9-5" type messaging,
   excessive emojis, vague titles like "CEO | Entrepreneur | Visionary"
4. Also look for green flags: real job title at a real company, technical skills,
   education, specific accomplishments

Respond in this exact format:
VERDICT: [SPAM / LIKELY SPAM / UNCLEAR / LIKELY LEGIT / LEGIT]
SCORE: [0-100 where 100 is definitely spam]
HEADLINE: [their headline if found, or "Not found"]
REASON: [2-3 sentences explaining your verdict]
RED FLAGS: [comma separated list, or "None"]
GREEN FLAGS: [comma separated list, or "None"]

Be direct and concise. Do not add anything outside this format."""


async def analyze_person(name: str, extra_info: str = None) -> dict:
    """
    Research a person on LinkedIn via Claude web search and return analysis.

    Args:
        name: Person's full name from the LinkedIn email
        extra_info: Any extra context from the email (e.g. their company)

    Returns:
        dict with keys: verdict, score, headline, reason, red_flags, green_flags, raw
    """
    search_query = f"{name} LinkedIn profile"
    if extra_info:
        search_query += f" {extra_info}"

    user_message = f"""Research this person and tell me if their LinkedIn connection request is spam:

Name: {name}
{f"Additional info: {extra_info}" if extra_info else ""}

Search for their LinkedIn profile and analyze it."""

    try:
        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                }
            ],
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Extract text from response
        raw_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                raw_text += block.text

        return _parse_claude_response(raw_text, name)

    except anthropic.APIConnectionError:
        logger.error("Anthropic API connection error")
        return _error_response(name, "Could not connect to Claude API")
    except anthropic.RateLimitError:
        logger.error("Anthropic rate limit hit")
        return _error_response(name, "Rate limit reached, try again in a moment")
    except Exception as e:
        logger.error(f"Claude analysis error for {name}: {e}")
        return _error_response(name, str(e)[:100])


def _parse_claude_response(text: str, name: str) -> dict:
    """Parse Claude's structured response into a dict."""
    result = {
        "name": name,
        "verdict": "UNCLEAR",
        "score": 50,
        "headline": "Not found",
        "reason": "Could not parse response",
        "red_flags": [],
        "green_flags": [],
        "raw": text,
    }

    if not text:
        return result

    lines = text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("VERDICT:"):
            result["verdict"] = line.replace("VERDICT:", "").strip()
        elif line.startswith("SCORE:"):
            try:
                result["score"] = int(line.replace("SCORE:", "").strip())
            except ValueError:
                pass
        elif line.startswith("HEADLINE:"):
            result["headline"] = line.replace("HEADLINE:", "").strip()
        elif line.startswith("REASON:"):
            result["reason"] = line.replace("REASON:", "").strip()
        elif line.startswith("RED FLAGS:"):
            flags = line.replace("RED FLAGS:", "").strip()
            result["red_flags"] = [f.strip() for f in flags.split(",") if f.strip() and f.strip() != "None"]
        elif line.startswith("GREEN FLAGS:"):
            flags = line.replace("GREEN FLAGS:", "").strip()
            result["green_flags"] = [f.strip() for f in flags.split(",") if f.strip() and f.strip() != "None"]

    return result


def _error_response(name: str, error: str) -> dict:
    return {
        "name": name,
        "verdict": "ERROR",
        "score": -1,
        "headline": "Not found",
        "reason": f"Analysis failed: {error}",
        "red_flags": [],
        "green_flags": [],
        "raw": "",
    }


def format_analysis_message(result: dict) -> str:
    """Format a Claude analysis result into a Telegram message."""
    score = result["score"]
    verdict = result["verdict"]
    name = result["name"]

    # Emoji based on verdict
    if verdict in ("SPAM", "LIKELY SPAM"):
        verdict_emoji = "🔴"
    elif verdict == "UNCLEAR":
        verdict_emoji = "🟡"
    elif verdict in ("LEGIT", "LIKELY LEGIT"):
        verdict_emoji = "🟢"
    else:
        verdict_emoji = "⚪"

    # Progress bar
    if score >= 0:
        filled = int(score / 10)
        bar = "█" * filled + "░" * (10 - filled)
        score_line = f"📊 Spam Score: {score}%\n{bar}\n"
    else:
        score_line = ""

    msg = f"{verdict_emoji} {name}\n"
    msg += "━" * 22 + "\n\n"

    if result["headline"] and result["headline"] != "Not found":
        msg += f"💼 {result['headline']}\n\n"

    msg += score_line + "\n"
    msg += f"{verdict_emoji} {verdict}\n"
    msg += f"{result['reason']}\n"

    if result["red_flags"]:
        msg += f"\n🚩 Red flags:\n"
        for flag in result["red_flags"]:
            msg += f"  • {flag}\n"

    if result["green_flags"]:
        msg += f"\n✅ Green flags:\n"
        for flag in result["green_flags"]:
            msg += f"  • {flag}\n"

    # Recommendation
    if verdict in ("SPAM", "LIKELY SPAM"):
        msg += "\n⚠️ Recommend: Decline"
    elif verdict == "UNCLEAR":
        msg += "\n💭 Recommend: Review manually"
    elif verdict in ("LEGIT", "LIKELY LEGIT"):
        msg += "\n✅ Recommend: Safe to accept"

    return msg