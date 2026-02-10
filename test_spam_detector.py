"""
Test script for the spam detection system.
"""

from spam_detector import analyze_linkedin_profile
from linkedin_client import create_sample_profile


def test_spam_profiles():
    """Test with obvious spam profiles."""
    print("=" * 60)
    print("TESTING SPAM PROFILES")
    print("=" * 60)
    
    # Test 1: Very obvious spam
    profile1 = create_sample_profile(
        name="Rick Money",
        headline="💰💰 CEO | I Help You Make $10K/Month From Home | DM Me To Learn How 🚀🚀",
        connections=123,
        summary="I quit my 9-5 job and now I have financial freedom! Multiple income streams! Ask me how!"
    )
    
    result1 = analyze_linkedin_profile(profile1)
    print("\nTest 1: Very Obvious Spam")
    print(f"Name: {profile1['name']}")
    print(f"Headline: {profile1['headline']}")
    print(f"Score: {result1['score']}%")
    print(f"Verdict: {result1['verdict']}")
    print("Reasons:")
    for reason in result1['reasons']:
        print(f"  - {reason}")
    
    # Test 2: MLM/Network Marketing
    profile2 = create_sample_profile(
        name="Sarah Success",
        headline="Entrepreneur | Network Marketing Pro | Passive Income Expert | Life Coach",
        connections=2456,
        summary="Join my team and achieve time freedom! Proven system for success."
    )
    
    result2 = analyze_linkedin_profile(profile2)
    print("\n" + "-" * 60)
    print("Test 2: MLM/Network Marketing")
    print(f"Name: {profile2['name']}")
    print(f"Headline: {profile2['headline']}")
    print(f"Score: {result2['score']}%")
    print(f"Verdict: {result2['verdict']}")
    print("Reasons:")
    for reason in result2['reasons']:
        print(f"  - {reason}")
    
    # Test 3: Crypto/Forex scammer
    profile3 = create_sample_profile(
        name="John Trader",
        headline="FOREX TRADER | CRYPTO INVESTOR | MAKE MONEY ONLINE | 6 FIGURE INCOME",
        connections=89,
        summary="Trading forex changed my life. DM for details on my proven strategy."
    )
    
    result3 = analyze_linkedin_profile(profile3)
    print("\n" + "-" * 60)
    print("Test 3: Crypto/Forex Scammer")
    print(f"Name: {profile3['name']}")
    print(f"Headline: {profile3['headline']}")
    print(f"Score: {result3['score']}%")
    print(f"Verdict: {result3['verdict']}")
    print("Reasons:")
    for reason in result3['reasons']:
        print(f"  - {reason}")


def test_legitimate_profiles():
    """Test with legitimate profiles."""
    print("\n" + "=" * 60)
    print("TESTING LEGITIMATE PROFILES")
    print("=" * 60)
    
    # Test 4: Software Engineer
    profile4 = create_sample_profile(
        name="Alice Johnson",
        headline="Senior Software Engineer at Google | Python, Go, Kubernetes",
        connections=634,
        summary="Building scalable distributed systems. Interested in cloud computing and DevOps."
    )
    
    result4 = analyze_linkedin_profile(profile4)
    print("\nTest 4: Software Engineer")
    print(f"Name: {profile4['name']}")
    print(f"Headline: {profile4['headline']}")
    print(f"Score: {result4['score']}%")
    print(f"Verdict: {result4['verdict']}")
    print("Reasons:")
    for reason in result4['reasons']:
        print(f"  - {reason}")
    
    # Test 5: Marketing Manager
    profile5 = create_sample_profile(
        name="Bob Smith",
        headline="Marketing Manager at Microsoft | B2B SaaS | Growth Strategy",
        connections=1523,
        summary="Experienced marketing professional focused on data-driven growth strategies."
    )
    
    result5 = analyze_linkedin_profile(profile5)
    print("\n" + "-" * 60)
    print("Test 5: Marketing Manager")
    print(f"Name: {profile5['name']}")
    print(f"Headline: {profile5['headline']}")
    print(f"Score: {result5['score']}%")
    print(f"Verdict: {result5['verdict']}")
    print("Reasons:")
    for reason in result5['reasons']:
        print(f"  - {reason}")
    
    # Test 6: Actual entrepreneur (but not spammy)
    profile6 = create_sample_profile(
        name="Maria Garcia",
        headline="Founder & CEO at TechStartup | Series A | AI/ML",
        connections=945,
        summary="Building AI solutions for healthcare. Previously at Amazon and Stanford."
    )
    
    result6 = analyze_linkedin_profile(profile6)
    print("\n" + "-" * 60)
    print("Test 6: Legitimate Founder")
    print(f"Name: {profile6['name']}")
    print(f"Headline: {profile6['headline']}")
    print(f"Score: {result6['score']}%")
    print(f"Verdict: {result6['verdict']}")
    print("Reasons:")
    for reason in result6['reasons']:
        print(f"  - {reason}")


def test_edge_cases():
    """Test edge cases."""
    print("\n" + "=" * 60)
    print("TESTING EDGE CASES")
    print("=" * 60)
    
    # Test 7: Borderline case
    profile7 = create_sample_profile(
        name="Chris Lee",
        headline="Entrepreneur | Startup Advisor | Angel Investor",
        connections=3421,
        summary="Helping early-stage startups grow. Former VP at Facebook."
    )
    
    result7 = analyze_linkedin_profile(profile7)
    print("\nTest 7: Borderline Case (Legitimate Entrepreneur)")
    print(f"Name: {profile7['name']}")
    print(f"Headline: {profile7['headline']}")
    print(f"Score: {result7['score']}%")
    print(f"Verdict: {result7['verdict']}")
    print("Reasons:")
    for reason in result7['reasons']:
        print(f"  - {reason}")
    
    # Test 8: Empty profile
    profile8 = create_sample_profile(
        name="",
        headline="",
        connections=0,
        summary=""
    )
    
    result8 = analyze_linkedin_profile(profile8)
    print("\n" + "-" * 60)
    print("Test 8: Empty Profile")
    print(f"Score: {result8['score']}%")
    print(f"Verdict: {result8['verdict']}")
    print("Reasons:")
    for reason in result8['reasons']:
        print(f"  - {reason}")


if __name__ == '__main__':
    test_spam_profiles()
    test_legitimate_profiles()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
