"""Security Service - Security analysis and scoring logic."""

from typing import List, Dict, Any
import zxcvbn


class SecurityService:
    """Provides security analysis for passwords."""
    
    @staticmethod
    def calculate_security_score(passwords: List[Dict[str, Any]]) -> int:
        """Calculate overall security score based on password strength.
        
        Args:
            passwords: List of password dictionaries.
            
        Returns:
            Security score from 0-100.
        """
        total = len(passwords)
        if total == 0:
            return 0
        
        weak = sum(1 for p in passwords if p.get('weak_password', False))
        strong = total - weak
        
        # Score formula: base on strong ratio, penalize weak passwords
        score = int(max(0, min(100, (strong / total * 100) - (weak * 5))))
        return score
    
    @staticmethod
    def get_crack_time(password: str) -> str:
        """Get estimated time to crack password using zxcvbn.
        
        Args:
            password: Password string to analyze.
            
        Returns:
            Human-readable crack time estimate.
        """
        try:
            result = zxcvbn.zxcvbn(password)
            return result['crack_times_display']['offline_slow_hashing_1e4_per_second']
        except:
            return "Unknown"
    
    @staticmethod
    def analyze_password_strength(password: str) -> Dict[str, Any]:
        """Analyze password strength using zxcvbn.
        
        Args:
            password: Password string to analyze.
            
        Returns:
            Dictionary with analysis results (score, feedback, crack_time).
        """
        try:
            result = zxcvbn.zxcvbn(password)
            return {
                'score': result['score'],  # 0-4
                'crack_time': result['crack_times_display']['offline_slow_hashing_1e4_per_second'],
                'feedback': result['feedback']
            }
        except:
            return {
                'score': 0,
                'crack_time': 'Unknown',
                'feedback': {}
            }
    
    @staticmethod
    def get_security_stats(passwords: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get comprehensive security statistics.
        
        Args:
            passwords: List of password dictionaries.
            
        Returns:
            Dictionary with total, weak, strong, and favorites counts.
        """
        total = len(passwords)
        weak = sum(1 for p in passwords if p.get('weak_password', False))
        strong = total - weak
        favorites = sum(1 for p in passwords if p.get('favorite', False))
        
        return {
            'total': total,
            'weak': weak,
            'strong': strong,
            'favorites': favorites
        }
