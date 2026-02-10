"""
Simple demonstration of the spam detection system.
This runs automatically without user input.
"""

from spam_detector import analyze_linkedin_profile
from linkedin_client import create_sample_profile


def print_analysis(title, profile_data, result):
    """Print analysis results in a formatted way."""
    score = result['score']
    verdict = result['verdict']
    reasons = result['reasons']
    
    # Create progress bar
    filled = int(score / 10)
    bar = '█' * filled + '░' * (10 - filled)
    
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)
    
    if profile_data.get('name'):
        print(f"\n👤 Name: {profile_data['name']}")
    if profile_data.get('headline'):
        print(f"💼 Headline: {profile_data['headline']}")
    if profile_data.get('connections'):
        print(f"🔗 Connections: {profile_data['connections']}")
    
    print(f"\n📊 Spam Score: {score}%")
    print(f"[{bar}] {score}%\n")
    print(f"{verdict}\n")
    print("📋 Reasons:")
    for reason in reasons:
        print(f"  • {reason}")


def main():
    """Run demonstrations."""
    print("\n" + "=" * 70)
    print(" " * 20 + "EntrepreNO Demo")
    print(" " * 15 + "LinkedIn Spam Detection")
    print("=" * 70)
    
    # Spam examples
    print("\n" + "🔴" * 35)
    print("SPAM PROFILES - High Risk Connection Requests")
    print("🔴" * 35)
    
    spam1 = create_sample_profile(
        name="Rick Money",
        headline="💰💰 Entrepreneur | CEO | Financial Freedom Coach | DM Me! 🚀",
        connections=156,
        summary="I quit my 9-5! Multiple income streams! Ask me how!"
    )
    result1 = analyze_linkedin_profile(spam1)
    print_analysis("Example 1: Classic MLM/Financial Freedom Pitch", spam1, result1)
    
    spam2 = create_sample_profile(
        name="John Crypto",
        headline="FOREX TRADER | CRYPTO INVESTOR | MAKE MONEY ONLINE 💎",
        connections=89,
        summary="Trading changed my life. DM for my proven strategy."
    )
    result2 = analyze_linkedin_profile(spam2)
    print_analysis("Example 2: Crypto/Forex Scammer", spam2, result2)
    
    spam3 = create_sample_profile(
        name="Sarah Success",
        headline="Life Coach | Passive Income Expert | Network Marketing Pro 🌟",
        connections=2456,
        summary="Proven system for success. Limited spots available!"
    )
    result3 = analyze_linkedin_profile(spam3)
    print_analysis("Example 3: Network Marketing/MLM", spam3, result3)
    
    # Legitimate examples
    print("\n\n" + "🟢" * 35)
    print("LEGITIMATE PROFILES - Safe to Connect")
    print("🟢" * 35)
    
    legit1 = create_sample_profile(
        name="Alice Johnson",
        headline="Senior Software Engineer at Google | Python, Go, Kubernetes",
        connections=847,
        summary="Building scalable systems and ML applications."
    )
    result4 = analyze_linkedin_profile(legit1)
    print_analysis("Example 4: Software Engineer", legit1, result4)
    
    legit2 = create_sample_profile(
        name="Bob Smith",
        headline="Product Manager at Microsoft | B2B SaaS | Growth Strategy",
        connections=1523,
        summary="Experienced PM focused on data-driven product decisions."
    )
    result5 = analyze_linkedin_profile(legit2)
    print_analysis("Example 5: Product Manager", legit2, result5)
    
    # Borderline case
    print("\n\n" + "🟡" * 35)
    print("BORDERLINE CASES - Use Caution")
    print("🟡" * 35)
    
    border1 = create_sample_profile(
        name="Maria Garcia",
        headline="Founder & CEO at TechStartup | Series A | Building AI Solutions",
        connections=945,
        summary="Building innovative healthcare AI. Ex-Amazon, Stanford PhD."
    )
    result6 = analyze_linkedin_profile(border1)
    print_analysis("Example 6: Legitimate Startup Founder", border1, result6)
    
    border2 = create_sample_profile(
        name="Chris Lee",
        headline="Entrepreneur | Startup Advisor | Angel Investor",
        connections=3421,
        summary="Helping early-stage startups grow. Former VP at Facebook."
    )
    result7 = analyze_linkedin_profile(border2)
    print_analysis("Example 7: Professional Entrepreneur/Investor", border2, result7)
    
    # Summary
    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
The EntrepreNO bot analyzes LinkedIn profiles for spam indicators:

✅ WHAT IT DETECTS:
  • Suspicious keywords (passive income, financial freedom, etc.)
  • Red flag phrases (DM me, ask me how, etc.)
  • Excessive emojis and all-caps text
  • Low connection counts for claimed titles
  • Income-related claims and get-rich-quick language

📊 SCORING SYSTEM:
  • 0-20%: Probably Legitimate
  • 20-40%: Somewhat Suspicious  
  • 40-60%: Suspicious - Be Careful
  • 60-80%: Likely Spam
  • 80-100%: Highly Likely Spam

💡 NOTE: This is a tool to assist your judgment, not replace it.
    Always review profiles yourself before making decisions.

🤖 USE THE TELEGRAM BOT:
    Set up the bot with your Telegram token and start analyzing
    LinkedIn connection requests right from Telegram!
    """)
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
