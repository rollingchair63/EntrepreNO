"""
End-to-end validation test for the EntrepreNO system.
This validates the complete flow from profile input to spam detection.
"""

from spam_detector import analyze_linkedin_profile
from linkedin_client import parse_profile_manually


def validate_end_to_end():
    """Validate the complete system flow."""
    print("=" * 70)
    print("END-TO-END VALIDATION TEST")
    print("=" * 70)
    
    test_cases = [
        {
            'name': 'High Spam Score Test',
            'input': """Rick Money
💰💰 CEO & Founder | Financial Freedom Expert | DM Me To Learn! 🚀
123 connections
I quit my 9-5! Multiple income streams! Ask me how you can too!""",
            'expected_min_score': 80,
            'expected_verdict_type': 'SPAM'
        },
        {
            'name': 'Low Spam Score Test',
            'input': """Alice Johnson
Senior Software Engineer at Google | Python, Go, Kubernetes
847 connections
Building scalable distributed systems and ML applications.""",
            'expected_max_score': 20,
            'expected_verdict_type': 'LEGITIMATE'
        },
        {
            'name': 'Medium Spam Score Test',
            'input': """Bob Entrepreneur
Entrepreneur | Startup Advisor | Angel Investor
2500 connections
Helping early-stage companies grow and scale.""",
            'expected_min_score': 10,
            'expected_max_score': 30,
            'expected_verdict_type': 'MINOR'
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"Test Case {i}: {test['name']}")
        print('=' * 70)
        
        # Parse the profile
        profile_data = parse_profile_manually(test['input'])
        
        # Analyze it
        result = analyze_linkedin_profile(profile_data)
        
        # Display results
        print(f"\nInput:")
        print(test['input'])
        print(f"\nParsed Profile:")
        print(f"  Name: {profile_data.get('name')}")
        print(f"  Headline: {profile_data.get('headline')}")
        print(f"  Connections: {profile_data.get('connections')}")
        
        print(f"\nAnalysis Result:")
        print(f"  Score: {result['score']}%")
        print(f"  Verdict: {result['verdict']}")
        
        # Validate expectations
        passed = True
        
        if 'expected_min_score' in test:
            if result['score'] < test['expected_min_score']:
                print(f"\n  ❌ FAILED: Score {result['score']}% is below expected minimum {test['expected_min_score']}%")
                passed = False
                all_passed = False
        
        if 'expected_max_score' in test:
            if result['score'] > test['expected_max_score']:
                print(f"\n  ❌ FAILED: Score {result['score']}% is above expected maximum {test['expected_max_score']}%")
                passed = False
                all_passed = False
        
        if passed:
            print(f"\n  ✅ PASSED: Score within expected range")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL VALIDATION TESTS PASSED")
    else:
        print("❌ SOME VALIDATION TESTS FAILED")
    print("=" * 70)
    
    return all_passed


def validate_edge_cases():
    """Validate edge cases and error handling."""
    print("\n\n" + "=" * 70)
    print("EDGE CASE VALIDATION")
    print("=" * 70)
    
    edge_cases = [
        {
            'name': 'Empty Profile',
            'data': {'name': '', 'headline': '', 'summary': '', 'connections': 0}
        },
        {
            'name': 'Only Name',
            'data': {'name': 'John Doe', 'headline': '', 'summary': '', 'connections': 0}
        },
        {
            'name': 'Only Headline',
            'data': {'name': '', 'headline': 'Software Engineer at Google', 'summary': '', 'connections': 0}
        },
        {
            'name': 'Very Long Headline',
            'data': {
                'name': 'Test User',
                'headline': 'CEO ' * 50,  # Very long headline
                'summary': '',
                'connections': 500
            }
        },
        {
            'name': 'Special Characters',
            'data': {
                'name': 'José García',
                'headline': 'Software Engineer @ Tech™ | AI/ML Expert 💻',
                'summary': 'Building stuff 🚀',
                'connections': 300
            }
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(edge_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"Edge Case {i}: {test['name']}")
        print('=' * 70)
        
        try:
            result = analyze_linkedin_profile(test['data'])
            print(f"  Score: {result['score']}%")
            print(f"  Verdict: {result['verdict']}")
            print(f"  Reasons: {len(result['reasons'])} reason(s)")
            print("  ✅ PASSED: No errors")
        except Exception as e:
            print(f"  ❌ FAILED: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL EDGE CASE TESTS PASSED")
    else:
        print("❌ SOME EDGE CASE TESTS FAILED")
    print("=" * 70)
    
    return all_passed


def main():
    """Run all validation tests."""
    print("\n" + "=" * 70)
    print("ENTREPRENO SYSTEM VALIDATION")
    print("=" * 70)
    
    result1 = validate_end_to_end()
    result2 = validate_edge_cases()
    
    print("\n\n" + "=" * 70)
    print("FINAL VALIDATION RESULT")
    print("=" * 70)
    
    if result1 and result2:
        print("\n✅ ALL VALIDATION TESTS PASSED")
        print("\nThe EntrepreNO system is working correctly!")
        print("The bot is ready to detect spammy LinkedIn entrepreneurs.")
        return 0
    else:
        print("\n❌ SOME VALIDATION TESTS FAILED")
        print("\nPlease review the failures above.")
        return 1


if __name__ == '__main__':
    exit(main())
