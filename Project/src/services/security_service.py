"""Serwis bezpieczeństwa - logika analizy i oceniania bezpieczeństwa"""

from typing import List, Dict, Any
import zxcvbn

from services.polish_dictionary import POLISH_WORD_LIST


def _entry_level(p: Dict[str, Any]) -> str:
    """Zwraca poziom siły wpisu ('weak', 'medium', 'strong')."""
    return p.get('strength', 'weak')


class SecurityService:
    """Udostępnia analize bezpieczeństwa haseł"""

    @staticmethod
    def evaluate_password(password: str) -> Dict[str, Any]:
        """Oceń pojedyncze hasło: poziom, score 0-100, słownikowość, czas złamania.

        Słownikowość: zxcvbn dopasowuje fragmenty do słowników (popularne
        hasła, słowa angielskie, imiona, wzorce l33t). Hasło uznajemy za
        słownikowe, gdy dopasowania słownikowe pokrywają >= 50% jego długości.
        Score bazuje na guesses_log10 (rzędy wielkości liczby prób), ze
        zniżką za słownikowość.
        """
        if not password:
            return {'level': 'weak', 'score': 0, 'dictionary': False,
                    'crack_time': 'instant'}
        try:
            # Przekazanie dodatkowego słownika do zxcvbn
            result = zxcvbn.zxcvbn(password, user_inputs=POLISH_WORD_LIST)
        except Exception:
            return {'level': 'weak', 'score': 0, 'dictionary': False,
                    'crack_time': 'Unknown'}

        dict_chars = sum(
            len(m.get('token', ''))
            for m in result.get('sequence', [])
            if m.get('pattern') == 'dictionary'
        )
        dictionary = (dict_chars / len(password)) >= 0.5

        # guesses_log10 ~12 odpowiada praktycznie nielamalnemu hasłu
        score = int(round(float(result['guesses_log10']) * 9))
        if dictionary:
            score -= 25
        score = max(0, min(100, score))

        if score >= 65:
            level = 'strong'
        elif score >= 35:
            level = 'medium'
        else:
            level = 'weak'

        return {
            'level': level,
            'score': score,
            'dictionary': dictionary,
            'crack_time': result['crack_times_display']['offline_slow_hashing_1e4_per_second'],
        }

    @staticmethod
    def calculate_security_score(passwords: List[Dict[str, Any]]) -> int:
        """Oblicza ogólny wynik bezpieczeństwa (0-100).

        Średnia ze score poszczególnych haseł; dla wpisów bez score
        (stare dane) przyjmuje 80 dla silnych, 50 dla średnich, 15 dla słabych.
        """
        total = len(passwords)
        if total == 0:
            return 0

        fallback = {'strong': 80, 'medium': 50, 'weak': 15}
        acc = 0
        for p in passwords:
            score = p.get('pw_score')
            if score is None:
                score = fallback[_entry_level(p)]
            acc += score
        return int(round(acc / total))
    
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
        levels = [_entry_level(p) for p in passwords]
        weak = levels.count('weak')
        medium = levels.count('medium')
        strong = levels.count('strong')
        favorites = sum(1 for p in passwords if p.get('favorite', False))

        return {
            'total': total,
            'weak': weak,
            'medium': medium,
            'strong': strong,
            'favorites': favorites
        }
