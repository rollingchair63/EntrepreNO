"""
Spam detection module for LinkedIn profiles.
Analyzes profile characteristics to determine spam likelihood.
"""

import re
from typing import Dict, List, Tuple


class SpamDetector:
    """Detects spammy entrepreneurs based on LinkedIn profile characteristics."""
    
    # Keywords commonly found in spam profiles
    SPAM_KEYWORDS = [
        'entrepreneur', 'ceo', 'founder', 'startup', 'coach', 'mentor',
        'passive income', 'financial freedom', 'make money', 'work from home',
        'business opportunity', 'network marketing', 'mlm', 'crypto',
        'forex', 'trading', 'investment opportunity', 'get rich',
        'life coach', 'mindset coach', 'success coach', 'millionaire',
        'six figure', '6 figure', 'seven figure', '7 figure',
        'dm me', 'link in bio', 'click link', 'limited spots',
        'free training', 'webinar', 'masterclass', 'scale your business',
        'real estate investor', 'day trader', 'drop shipping', 'dropshipping',
        'affiliate marketing', 'influencer', 'social media marketing',
        'smma', 'agency owner', 'ecommerce', 'e-commerce'
    ]
    
    # Red flag phrases
    RED_FLAGS = [
        'dm for details', 'message me to learn', 'ask me how',
        'changed my life', 'quit my 9-5', 'fired my boss',
        'be your own boss', 'time freedom', 'location freedom',
        'multiple income streams', 'residual income', 'recurring revenue',
        'proven system', 'turnkey solution', 'done for you'
    ]
    
    def __init__(self):
        self.spam_keywords = self.SPAM_KEYWORDS
        self.red_flags = self.RED_FLAGS
    
    def analyze_profile(self, profile_data: Dict) -> Tuple[int, List[str]]:
        """
        Analyze a LinkedIn profile and return spam confidence score.
        
        Args:
            profile_data: Dictionary containing profile information
                - name: str
                - headline: str
                - summary: str (optional)
                - connections: int (optional)
                - posts_count: int (optional)
                
        Returns:
            Tuple of (confidence_score: int 0-100, reasons: List[str])
        """
        score = 0
        reasons = []
        
        name = profile_data.get('name', '').lower()
        headline = profile_data.get('headline', '').lower()
        summary = profile_data.get('summary', '').lower()
        connections = profile_data.get('connections', 0)
        
        # Combine text fields for analysis
        full_text = f"{name} {headline} {summary}"
        
        # Check for spam keywords in headline (weighted higher) using word boundaries
        headline_spam_count = sum(
            1 for keyword in self.spam_keywords 
            if re.search(r'\b' + re.escape(keyword) + r'\b', headline, re.IGNORECASE)
        )
        if headline_spam_count >= 3:
            score += 30
            reasons.append(f"Multiple spam keywords in headline ({headline_spam_count} found)")
        elif headline_spam_count >= 1:
            score += 15
            reasons.append(f"Spam keywords in headline ({headline_spam_count} found)")
        
        # Check for red flag phrases using word boundaries
        red_flag_count = sum(
            1 for flag in self.red_flags 
            if re.search(r'\b' + re.escape(flag) + r'\b', full_text, re.IGNORECASE)
        )
        if red_flag_count > 0:
            score += red_flag_count * 15
            reasons.append(f"Red flag phrases detected ({red_flag_count} found)")
        
        # Check for excessive emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        emoji_count = len(emoji_pattern.findall(headline))
        if emoji_count >= 5:
            score += 20
            reasons.append(f"Excessive emojis in headline ({emoji_count} found)")
        elif emoji_count >= 3:
            score += 10
            reasons.append(f"Multiple emojis in headline ({emoji_count} found)")
        
        # Check for all caps (shouting)
        if headline and headline.isupper() and len(headline) > 10:
            score += 15
            reasons.append("Headline is all caps (shouting)")
        
        # Check for suspicious connection count
        if connections and connections > 0:
            if connections < 100:
                score += 10
                reasons.append(f"Low connection count ({connections})")
            elif connections > 5000:
                score += 5
                reasons.append(f"Very high connection count ({connections})")
        
        # Check for "CEO" or "Founder" with low connections
        if ('ceo' in headline or 'founder' in headline) and connections < 200:
            score += 15
            reasons.append("Claims CEO/Founder title with low connections")
        
        # Check for generic/fake-sounding names
        success_pattern = r'\b(success|wealth|money|cash|profit|income)\b'
        guru_pattern = r'\b(digital|online|virtual)\s+(entrepreneur|expert|guru)\b'
        
        if re.search(success_pattern, full_text, re.IGNORECASE):
            score += 10
            reasons.append("Money/success-related terms in name or profile")
        elif re.search(guru_pattern, full_text, re.IGNORECASE):
            score += 10
            reasons.append("Generic 'expert/guru' language detected")
        
        # Check for multiple income claims using word boundaries
        income_keywords = ['passive income', 'multiple income', 'residual income', 
                          'recurring revenue', 'six figure', 'seven figure', '6 figure', '7 figure']
        income_count = sum(
            1 for keyword in income_keywords 
            if re.search(r'\b' + re.escape(keyword) + r'\b', full_text, re.IGNORECASE)
        )
        if income_count >= 2:
            score += 20
            reasons.append("Multiple income-related claims")
        elif income_count >= 1:
            score += 10
            reasons.append("Income-related claims detected")
        
        # Cap the score at 100
        score = min(score, 100)
        
        # If no red flags found
        if score == 0:
            reasons.append("No obvious spam indicators detected")
        
        return score, reasons
    
    def get_verdict(self, score: int) -> str:
        """Get a human-readable verdict based on the spam score."""
        if score >= 80:
            return "🚨 HIGHLY LIKELY SPAM - Avoid at all costs!"
        elif score >= 60:
            return "⚠️ LIKELY SPAM - Proceed with extreme caution"
        elif score >= 40:
            return "🤔 SUSPICIOUS - Could be spam, be careful"
        elif score >= 20:
            return "😐 SOMEWHAT SUSPICIOUS - Minor red flags"
        else:
            return "✅ PROBABLY LEGITIMATE - Looks okay"


def analyze_linkedin_profile(profile_data: Dict) -> Dict:
    """
    Convenience function to analyze a LinkedIn profile.
    
    Args:
        profile_data: Dictionary with profile information
        
    Returns:
        Dictionary with analysis results
    """
    detector = SpamDetector()
    score, reasons = detector.analyze_profile(profile_data)
    verdict = detector.get_verdict(score)
    
    return {
        'score': score,
        'verdict': verdict,
        'reasons': reasons
    }
