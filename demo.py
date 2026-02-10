"""
Interactive demo script for the EntrepreNO spam detector.
Run this to test the spam detection without needing a Telegram bot.
"""

from src.services.spam_detector import analyze_linkedin_profile
from linkedin_client import parse_profile_manually


def print_analysis(profile_data, result):
    """Print analysis results in a formatted way."""
    score = result['score']
    verdict = result['verdict']
    reasons = result['reasons']
    
    # Create progress bar
    filled = int(score / 10)
    bar = '█' * filled + '░' * (10 - filled)
    
    print("\n" + "=" * 60)
    print("🎯 LINKEDIN PROFILE ANALYSIS")
    print("=" * 60)
    
    if profile_data.get('name'):
        print(f"\n👤 Name: {profile_data['name']}")
    if profile_data.get('headline'):
        print(f"💼 Headline: {profile_data['headline']}")
    if profile_data.get('connections'):
        print(f"🔗 Connections: {profile_data['connections']}")
    
    print(f"\n📊 Spam Score: {score}%")
    print(f"{bar} {score}%\n")
    print(f"{verdict}\n")
    print("📋 Analysis Details:")
    for reason in reasons:
        print(f"  • {reason}")
    
    # Recommendation
    if score >= 60:
        print("\n⚠️  RECOMMENDATION:")
        print("  This profile shows significant spam indicators.")
        print("  Consider declining this connection request.")
    elif score >= 40:
        print("\n💭 RECOMMENDATION:")
        print("  This profile has some suspicious elements.")
        print("  Review their profile carefully before accepting.")
    else:
        print("\n✅ RECOMMENDATION:")
        print("  This profile appears relatively normal.")
        print("  Use your judgment as always!")
    
    print("=" * 60)


def interactive_mode():
    """Run interactive mode where user can paste profiles."""
    print("\n" + "=" * 60)
    print("EntrepreNO - Interactive Spam Detection Demo")
    print("=" * 60)
    print("\nPaste a LinkedIn profile (name, headline, connections, summary)")
    print("Press Enter twice when done, or type 'quit' to exit\n")
    
    while True:
        lines = []
        print("\nEnter profile information (press Enter twice when done):")
        
        while True:
            line = input()
            if line.lower() == 'quit':
                print("\nGoodbye!")
                return
            if not line and lines:
                break
            if line:
                lines.append(line)
        
        profile_text = '\n'.join(lines)
        profile_data = parse_profile_manually(profile_text)
        
        if not profile_data['name'] and not profile_data['headline']:
            print("\n❌ Could not parse profile. Please try again.\n")
            continue
        
        result = analyze_linkedin_profile(profile_data)
        print_analysis(profile_data, result)
        
        print("\nAnalyze another profile? (y/n)")
        choice = input().lower()
        if choice != 'y':
            print("\nGoodbye!")
            break


def demo_mode():
    """Run demo mode with pre-defined examples."""
    print("\n" + "=" * 60)
    print("EntrepreNO - Spam Detection Demo")
    print("=" * 60)
    
    examples = [
        {
            'description': 'SPAM EXAMPLE #1: Classic MLM/Financial Freedom',
            'text': """Rick Money
💰💰 Entrepreneur | CEO | Helping You Achieve Financial Freedom | DM Me! 🚀
156 connections
I quit my 9-5 job and now make 6 figures from home! Multiple income streams! Limited spots available - ask me how!"""
        },
        {
            'description': 'SPAM EXAMPLE #2: Crypto/Forex Trader',
            'text': """John Crypto
FOREX TRADER | BITCOIN INVESTOR | MAKE MONEY ONLINE 💎
89 connections
Trading changed my life. Message me for my proven strategy. Get rich quick!"""
        },
        {
            'description': 'LEGITIMATE EXAMPLE #1: Software Engineer',
            'text': """Alice Johnson
Senior Software Engineer at Google | Python, Go, Kubernetes
847 connections
Passionate about building scalable systems and machine learning applications."""
        },
        {
            'description': 'LEGITIMATE EXAMPLE #2: Product Manager',
            'text': """Bob Smith
Product Manager at Microsoft | B2B SaaS | Growth Strategy
1523 connections
Experienced product professional focused on user-centered design and data-driven decisions."""
        },
        {
            'description': 'BORDERLINE EXAMPLE: Actual Founder',
            'text': """Maria Garcia
Founder & CEO at TechStartup | Series A | Building AI for Healthcare
945 connections
Building innovative AI solutions. Previously at Amazon and Stanford. Always happy to connect with fellow builders."""
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'*' * 60}")
        print(f"{example['description']}")
        print('*' * 60)
        
        profile_data = parse_profile_manually(example['text'])
        result = analyze_linkedin_profile(profile_data)
        print_analysis(profile_data, result)
        
        if i < len(examples):
            input("\nPress Enter for next example...")


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("   _____ _  _ _____ ___ ___ ___ ___ ___ _  _  ___  ")
    print("  | __| \\| |_   _| _ \\ __| _ \\ _ \\ __| \\| |/ _ \\ ")
    print("  | _|| .` | | | |   / _||  _/   / _|| .` | (_) |")
    print("  |___|_|\\_| |_| |_|_\\___|_| |_|_\\___|_|\\_|\\___/ ")
    print("=" * 60)
    print("LinkedIn Spam Detection System")
    print("=" * 60)
    
    print("\nSelect mode:")
    print("1. Demo Mode - See pre-defined examples")
    print("2. Interactive Mode - Test your own profiles")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        demo_mode()
    elif choice == '2':
        interactive_mode()
    else:
        print("\nGoodbye!")


if __name__ == '__main__':
    main()
