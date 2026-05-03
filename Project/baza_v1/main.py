import time

try:
    from . import db_manager
    from .generator import generate_strong_password
except ImportError:
    import db_manager
    from generator import generate_strong_password
'''
Plik jest zbedny przy uruchamianiu wlasciwej aplikacji w src. Sluzy jedynie do
sprawdzenia poprawnosci dzialania bazy
'''

def main():
    if not db_manager.vault_exists():
        print("--- PIERWSZE URUCHOMIENIE ---")
        master_password = input("Podaj nowe haslo glowne: ")
        db_manager.initialize_database(master_password)

    print("\n--- LOGOWANIE ---")
    while True:
        master_password = input("Podaj haslo glowne: ")
        if db_manager.login(master_password):
            break

        print("Bledne haslo. Czekam 3 sekundy...")
        time.sleep(3)

    print("Zalogowano.")
    while True:
        print("\n1. Dodaj wpis")
        print("2. Dodaj wpis z wygenerowanym haslem")
        print("3. Pokaz hasla")
        print("4. Wyjdz")
        choice = input("Wybor: ")

        if choice == "1":
            add_entry(generate=False)
        elif choice == "2":
            add_entry(generate=True)
        elif choice == "3":
            show_entries()
        elif choice == "4":
            return
        else:
            print("Nieznana opcja.")


def add_entry(generate=False):
    title = input("Serwis: ")
    username = input("Login: ")
    password = generate_strong_password() if generate else input("Haslo: ")
    url = input("Strona URL (opcjonalnie): ")
    notes = input("Notatki (opcjonalnie): ")

    if generate:
        print(f"Wygenerowano haslo: {password}")

    db_manager.add_password(title, username, password, url, notes)
    print("Dodano wpis.")


def show_entries():
    entries = db_manager.get_all_passwords()
    if not entries:
        print("Brak hasel.")
        return

    for entry in entries:
        print(f"{entry['name']} | Login: {entry['username']} | Haslo: {entry['password']} | URL: {entry['url']}")


if __name__ == "__main__":
    main()
