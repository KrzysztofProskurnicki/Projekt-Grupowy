"""
Prosty słownik popularnych polskich słów do wzmocnienia analizy zxcvbn.
W rzeczywistej aplikacji lista ta powinna być znacznie dłuższa i pochodzić
z analizy korpusów języka polskiego.
"""

# Lista popularnych polskich słów, imion, miejsc itp.
# Wszystkie słowa powinny być pisane małymi literami.
POLISH_WORD_LIST = [
    # Popularne słowa
    "haslo", "polska", "kotki","pies", "kocham", "sekret", "admin", "qwerty", "test",
    "system", "uzytkownik", "firma", "szkola", "komputer", "internet",
    "kwiat", "dom", "auto", "pilka", "wakacje", "milosc", "slonce",
    "wiosna", "lato", "jesien", "zima", "jeden", "dwa", "trzy", "cztery",
    "super", "bardzo", "tajne", "poufne", "moje", "twoje",

    # Popularne imiona męskie
    "jan", "piotr", "krzysztof", "andrzej", "tomasz", "pawel", "marcin",
    "michal", "stanislaw", "jakub", "adam", "lukasz", "grzegorz", "mateusz",

    # Popularne imiona żeńskie
    "anna", "katarzyna", "maria", "malgorzata", "agnieszka", "barbara",
    "ewa", "krystyna", "elzbieta", "joanna", "aleksandra", "magdalena",

    # Nazwy miast
    "warszawa", "krakow", "lodz", "wroclaw", "poznan", "gdansk", "szczecin",
    "bydgoszcz", "lublin", "katowice",

    # Inne
    "kochamcie", "ziomek", "skarbie", "sloneczko", "kwiatuszku", "myszko",
    "zabka", "kotek", "piesek", "serce", "buzi", "ziemia", "niebo", "koszmar", "misio",
    "króliczek"
]