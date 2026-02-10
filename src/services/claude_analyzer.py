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

SYSTEM_PROMPT = """You are an assistant that determines whether a LinkedIn connection request 
is from a spammy entrepreneur or a legitimate professional.

STRICT OUTPUT RULES:
- REASON must be 2–3 sentences total
- Each sentence must be under 25 words
- Do NOT add examples, disclaimers, or extra context
- Do NOT repeat the same idea twice
- If information is missing, state it once and move on

When given a person's name, you will:
1. Search for their LinkedIn profile
2. Analyze headline, bio, job history, and posts
3. Identify red and green flags

Respond in this exact format ONLY:
VERDICT: [SPAM / LIKELY SPAM / UNCLEAR / LIKELY LEGIT / LEGIT]
SCORE: [0-100 where 100 is definitely spam]
HEADLINE: [their headline if found, or "Not found"]
REASON: [2–3 short sentences only]
RED FLAGS: [comma separated list, or "None"]
GREEN FLAGS: [comma separated list, or "None"]

No extra text. No markdown. No commentary.
"""


async def analyze_person(name: str, extra_info: str = None) -> dict:
    """
    Research a person on LinkedIn via Claude web search and return analysis.

    Args:
        name: Person's full name
        extra_info: Optional headline/job title (only from emails)

    Returns:
        dict with keys: verdict, score, headline, reason, red_flags, green_flags, raw
    """
    
    # Build prompt based on whether this is from email or manual lookup
    if extra_info and extra_info.lower() != "none":
        headline_context = f"\nHeadline from email: {extra_info}"
        fallback_instruction = f"""
- If you can't find their full profile, analyze their headline: "{extra_info}"
- Look for MLM terms, "financial freedom", vague titles, excessive emojis"""
    else:
        headline_context = ""
        fallback_instruction = """
- If you can't find ANY profile after searching, that itself is suspicious"""

    user_message = f"""Search for and analyze this person's LinkedIn profile:

Name: {name}{headline_context}

CRITICAL INSTRUCTIONS:
1. Search: "{name}" LinkedIn
2. When you get results, LOOK AT THE URLS - find linkedin.com/in/ links
3. The first few results will likely be their profile - examine them
4. Extract their headline, about section, and current job from what you see
5. If you see partial info in search snippets, use that for analysis

WHAT TO LOOK FOR:
Red flags: MLM/network marketing, "financial freedom", "passive income", life/business coaching with no credentials, crypto/forex trading, dropshipping, "quit my 9-5", excessive emojis, vague titles like "CEO | Entrepreneur | Visionary"
Green flags: Real job at real company, technical skills, specific accomplishments, education credentials
{fallback_instruction}

IMPORTANT: Even if you only see their headline in search results, analyze it! Don't say "profile not found" if you can see ANY information about them.

Respond in the exact format from your system prompt."""

    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=420,  # Increased for longer analysis
                system=SYSTEM_PROMPT,
                stop_sequences=["GREEN FLAGS:"],
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
            tool_used = False
            for block in response.content:
                if hasattr(block, "text"):
                    raw_text += block.text
                elif block.type in ("tool_use", "server_tool_use"):
                    tool_used = True
                    logger.info(f"Claude used tool: {block.name}")

            logger.info(f"Analyzed {name}: searches={tool_used}, got_text={bool(raw_text)}")
            
            if raw_text:
                return _parse_claude_response(raw_text, name)

            logger.warning(f"No text response for {name}")
            return _error_response(name, "No analysis returned")

        except anthropic.RateLimitError:
            if attempt < 2:
                wait = 15 * (attempt + 1)
                logger.info(f"Rate limited, retrying in {wait}s...")
                await asyncio.sleep(wait)
            else:
                return _error_response(name, "Rate limit reached")

        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return _error_response(name, str(e)[:100])

    return _error_response(name, "Max retries exceeded")

async def analyze_profile_url(url: str) -> dict:
    """
    Fetch and analyze a LinkedIn profile directly from URL.

    Args:
        url: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username)

    Returns:
        dict with keys: verdict, score, headline, reason, red_flags, green_flags, raw
    """
    
    # Extract name from URL for the result
    name_part = url.split("/in/")[-1].split("?")[0].strip("/").replace("-", " ")
    name = name_part.title() if name_part else "Unknown"
    
    user_message = f"""Search for and analyze this LinkedIn profile:

URL: {url}

INSTRUCTIONS:
1. Use web_search to find information about this person
2. Search for: "{name}" LinkedIn
3. Also search the exact URL to see what's publicly available
4. Analyze whatever information you find

Red flags: MLM/network marketing, "financial freedom", "passive income", life/business coaching with no credentials, crypto/forex trading, dropshipping, "quit my 9-5", excessive emojis, vague titles like "CEO | Entrepreneur | Visionary"
Green flags: Real job at real company, technical skills, specific accomplishments, education credentials

Respond in the exact format from your system prompt."""

    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                system=SYSTEM_PROMPT,
                stop_sequences=["GREEN FLAGS:"],
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

            logger.info(f"Analyzed profile URL: {url}")
            
            if raw_text:
                return _parse_claude_response(raw_text, name)

            return _error_response(name, "No analysis returned")

        except anthropic.RateLimitError:
            if attempt < 2:
                wait = 15 * (attempt + 1)
                await asyncio.sleep(wait)
            else:
                return _error_response(name, "Rate limit reached")

        except Exception as e:
            logger.error(f"Profile URL analysis error: {e}")
            return _error_response(name, str(e)[:100])

    return _error_response(name, "Max retries exceeded")

        
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

    # Extract each field using regex - more careful parsing
    patterns = {
        "verdict": r"VERDICT:\s*(.+?)(?=\n|$)",
        "score":   r"SCORE:\s*(\d+)",
        "headline": r"HEADLINE:\s*(.+?)(?=\nVERDICT:|SCORE:|REASON:|RED FLAGS:|GREEN FLAGS:|$)",
        "reason":  r"REASON:\s*(.+?)(?=\nVERDICT:|SCORE:|HEADLINE:|RED FLAGS:|GREEN FLAGS:|$)",
        "red_flags": r"RED FLAGS:\s*(.+?)(?=\nVERDICT:|SCORE:|HEADLINE:|REASON:|GREEN FLAGS:|$)",
        "green_flags": r"GREEN FLAGS:\s*(.+?)(?=\nVERDICT:|SCORE:|HEADLINE:|REASON:|RED FLAGS:|$)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            
            # Clean up the value
            value = re.sub(r'\*\*', '', value)  # Remove markdown bold
            value = re.sub(r'\n\s*-\s*', ', ', value)  # Convert bullet lists to commas
            value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            value = value.strip()
            
            if field == "score":
                try:
                    result["score"] = int(value)
                except ValueError:
                    pass
            elif field in ("red_flags", "green_flags"):
                # Split by comma and clean each item
                flags = [f.strip() for f in value.split(",") if f.strip()]
                # Remove "None" entries
                flags = [f for f in flags if f.lower() != "none"]
                # Limit to reasonable length
                flags = [f[:100] for f in flags]  # Max 100 chars per flag
                result[field] = flags[:5]  # Max 5 flags
            else:
                # Limit reason and headline length
                if field == "reason":
                    sentences = re.split(r'(?<=[.!?])\s+', value)
                    value = " ".join(sentences[:3])  # hard cap at 3 sentences
                elif field == "headline":
                    sentences = re.split(r'(?<=[.!?])\s+', value)
                    value = " ".join(sentences[:3])  # hard cap at 3 sentences
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
        score_line = f"📊 Spam Score: {score}%\n{bar}"
    else:
        score_line = ""

    msg = f"{verdict_emoji} *{name}*\n"
    msg += "━" * 22 + "\n"

    if result["headline"] and result["headline"] != "Not found":
        # Limit headline display
        headline = result['headline'][:150]
        msg += f"💼 {headline}\n\n"

    if score_line:
        msg += f"{score_line}\n\n"
    
    msg += f"{verdict_emoji} *{verdict}*\n"
    
    # Limit reason length
    reason = result['reason'][:250]
    msg += f"{reason}\n"

    # Show flags only if they exist and are reasonable
    if result["red_flags"] and len(result["red_flags"]) > 0:
        msg += f"\n🚩 *Red flags:*\n"
        for flag in result["red_flags"][:3]:  # Max 3 flags
            flag_text = flag[:80]  # Max 80 chars per flag
            msg += f"  • {flag_text}\n"

    if result["green_flags"] and len(result["green_flags"]) > 0:
        msg += f"\n✅ *Green flags:*\n"
        for flag in result["green_flags"][:3]:  # Max 3 flags
            flag_text = flag[:80]
            msg += f"  • {flag_text}\n"

    # Recommendation
    if verdict in ("SPAM", "LIKELY SPAM"):
        msg += "\n⚠️ *Recommend:* Decline"
    elif verdict == "UNCLEAR":
        msg += "\n💭 *Recommend:* Review manually"
    elif verdict in ("LEGIT", "LIKELY LEGIT"):
        msg += "\n✅ *Recommend:* Safe to accept"

    return msg