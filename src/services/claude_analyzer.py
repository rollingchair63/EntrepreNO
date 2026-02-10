"""
Claude-powered LinkedIn profile analyzer.
Uses the Anthropic API with web search to research a person
and determine if they're a spammy entrepreneur.
"""

import os
import logging
import anthropic
import asyncio
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
    user_message = f"""Research this person and tell me if their LinkedIn connection request is spam:

Name: {name}
{f"Additional info from email: {extra_info}" if extra_info else ""}

Instructions:
1. Search for their LinkedIn profile using web search
2. If found, analyze their headline, about section, and recent activity
3. If NOT found, use the "Additional info from email" above (their headline/job title from the connection request)
4. Vague headlines like "Entrepreneur | Empowering others" are RED FLAGS even without the full profile
5. Make a decisive verdict - avoid UNCLEAR unless truly ambiguous

Remember: Respond ONLY in the exact format specified in your system prompt."""

    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
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

            # Extract text from ALL content blocks
            raw_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    raw_text += block.text
                # Log tool use for debugging
                elif block.type == "tool_use":
                    logger.info(f"Claude used tool: {block.name}")

            # If we got no text response, something went wrong
            if not raw_text:
                logger.warning(f"No text response from Claude for {name}, response: {response}")
                return _error_response(name, "Claude did not return a text response")

            logger.info(f"Raw Claude response for {name}: '{raw_text}'")
            return _parse_claude_response(raw_text, name)

        except anthropic.RateLimitError:
            if attempt < 2:
                wait = 15 * (attempt + 1)
                logger.info(f"Rate limited for {name}, retrying in {wait}s (attempt {attempt + 1}/3)...")
                await asyncio.sleep(wait)
            else:
                logger.error(f"Rate limit hit 3 times for {name}, giving up")
                return _error_response(name, "Rate limit reached, try again in a moment")

        except anthropic.APIConnectionError:
            logger.error("Anthropic API connection error")
            return _error_response(name, "Could not connect to Claude API")

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

    import re

    # Extract each field using regex so multiline values are captured
    patterns = {
        "verdict": r"VERDICT:\s*(.+?)(?=\n[A-Z ]+:|$)",
        "score":   r"SCORE:\s*(\d+)",
        "headline": r"HEADLINE:\s*(.+?)(?=\n[A-Z ]+:|$)",
        "reason":  r"REASON:\s*(.+?)(?=\n[A-Z ]+:|$)",
        "red_flags": r"RED FLAGS:\s*(.+?)(?=\n[A-Z ]+:|$)",
        "green_flags": r"GREEN FLAGS:\s*(.+?)(?=\n[A-Z ]+:|$)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if field == "score":
                try:
                    result["score"] = int(value)
                except ValueError:
                    pass
            elif field in ("red_flags", "green_flags"):
                result[field] = [f.strip() for f in value.split(",") if f.strip() and f.strip().lower() != "none"]
            else:
                result[field] = value

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