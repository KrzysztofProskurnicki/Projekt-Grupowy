"""Serwis bezpieczeństwa - logika analizy i oceniania bezpieczeństwa"""

from typing import List, Dict, Any
import zxcvbn


class SecurityService:
    """Udostępnia analize bezpieczeństwa haseł"""
    
    @staticmethod
    def calculate_security_score(passwords: List[Dict[str, Any]]) -> int:
        """Oblicza ogólny wynik bezpieczeństwa na podstawie siły haseł

        Zwraca:
            Wynik bezpieczeństwa od 0 do 100
        """
        total = len(passwords)
        if total == 0:
            return 0
        
        weak = sum(1 for p in passwords if p.get('weak_password', False))
        strong = total - weak
        
        # Wzór wyniku: bazuje na udziale silnych haseł i słabych haseł
        score = int(max(0, min(100, (strong / total * 100) - (weak * 5))))
        return score
    
    @staticmethod
    def get_crack_time(password: str) -> str:
        """Pobierz szacowany czas złamania hasła przy użyciu zxcvbn.
        
        Argumenty:
            password: Hasło do analizy
            
        Zwraca:
            Czytelne dla człowieka oszacowanie czasu złamania
        """
        try:
            result = zxcvbn.zxcvbn(password)
            return result['crack_times_display']['offline_slow_hashing_1e4_per_second']
        except:
            return "Unknown"
    
    @staticmethod
    def analyze_password_strength(password: str) -> Dict[str, Any]:
        """Przeanalizuj siłę hasła przy użyciu zxcvbn.
        
        Argumenty:
            password: Hasło do analizy
            
        Zwraca:
            Słownik z wynikami analizy (score, feedback, crack_time)
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
        """Pobierz zbiorcze statystyki bezpieczeństwa.
        
        Argumenty:
            passwords: Lista słowników haseł
            
        Zwraca:
            Słownik z licznikami total, weak, strong i favorites
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
