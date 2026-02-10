"""
Test script for LinkedIn profile parsing.
"""

from linkedin_client import parse_profile_manually


def test_parsing():
    """Test profile parsing from various formats."""
    print("=" * 60)
    print("TESTING PROFILE PARSING")
    print("=" * 60)
    
    # Test 1: Full profile with all fields
    profile_text1 = """John Doe
CEO at StartupXYZ | Entrepreneur | Investor
500+ connections
I help people achieve financial freedom and build passive income streams."""
    
    result1 = parse_profile_manually(profile_text1)
    print("\nTest 1: Full Profile")
    print(f"Input:\n{profile_text1}")
    print(f"\nParsed:")
    print(f"  Name: {result1['name']}")
    print(f"  Headline: {result1['headline']}")
    print(f"  Connections: {result1['connections']}")
    print(f"  Summary: {result1['summary']}")
    
    # Test 2: Just name and headline
    profile_text2 = """Sarah Johnson
Software Engineer at Google | Python, ML, AI"""
    
    result2 = parse_profile_manually(profile_text2)
    print("\n" + "-" * 60)
    print("Test 2: Name and Headline Only")
    print(f"Input:\n{profile_text2}")
    print(f"\nParsed:")
    print(f"  Name: {result2['name']}")
    print(f"  Headline: {result2['headline']}")
    print(f"  Connections: {result2['connections']}")
    
    # Test 3: With emoji in headline
    profile_text3 = """Rick Success
💰 CEO & Founder | Helping You Achieve Financial Freedom 🚀
1234 connections
Changed my life! Ask me how!"""
    
    result3 = parse_profile_manually(profile_text3)
    print("\n" + "-" * 60)
    print("Test 3: With Emojis")
    print(f"Input:\n{profile_text3}")
    print(f"\nParsed:")
    print(f"  Name: {result3['name']}")
    print(f"  Headline: {result3['headline']}")
    print(f"  Connections: {result3['connections']}")
    print(f"  Summary: {result3['summary']}")
    
    # Test 4: Just headline (single line)
    profile_text4 = "Entrepreneur | Passive Income Expert | DM Me"
    
    result4 = parse_profile_manually(profile_text4)
    print("\n" + "-" * 60)
    print("Test 4: Headline Only")
    print(f"Input:\n{profile_text4}")
    print(f"\nParsed:")
    print(f"  Name: {result4['name']}")
    print(f"  Headline: {result4['headline']}")
    
    # Test 5: With "500+" format
    profile_text5 = """Alice Chen
Product Manager at Amazon
500+ connections"""
    
    result5 = parse_profile_manually(profile_text5)
    print("\n" + "-" * 60)
    print("Test 5: 500+ Format")
    print(f"Input:\n{profile_text5}")
    print(f"\nParsed:")
    print(f"  Name: {result5['name']}")
    print(f"  Headline: {result5['headline']}")
    print(f"  Connections: {result5['connections']}")


if __name__ == '__main__':
    test_parsing()
    print("\n" + "=" * 60)
    print("PARSING TESTS COMPLETED")
    print("=" * 60)
