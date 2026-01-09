from db_manager import initialize_database, login, add_password, get_all_passwords
from generator import generate_strong_password
import os
import time


def main():

    if not os.path.exists("sejfy.db"):
        print("--- PIERWSZE URUCHOMIENIE ---")
        mp = input("Podaj nowe hasło główne: ")
        initialize_database(mp)

    print("\n--- LOGOWANIE ---")
    while True:
        mp_input = input("Podaj hasło główne: ")

        if login(mp_input):
            print("Zalogowano!")

            while True:
                print("\n1. Dodaj wpis (wpisz własne hasło)")
                print("2. Dodaj wpis (GENERUJ silne hasło)")
                print("3. Pokaż hasła")
                print("4. Wyjdź")
                choice = input("Wybór: ")

                if choice == "1":
                    t = input("Serwis: ")
                    u = input("Login: ")
                    p = input("Hasło: ")
                    add_password(t, u, p)

                elif choice == "2":
                    t = input("Serwis: ")
                    u = input("Login: ")
                    # Generowanie hasła
                    p = generate_strong_password(length=20)
                    print(f"-> Wygenerowano hasło: {p}")
                    add_password(t, u, p)

                elif choice == "3":
                    passwords = get_all_passwords()
                    if not passwords:
                        print("Brak haseł.")
                    for item in passwords:
                        print(item)

                elif choice == "4":
                    return
                else:
                    print("Nieznana opcja.")
            break
        else:
            print("Błędne hasło! Czekam 3 sekundy...")
            time.sleep(3)


if __name__ == "__main__":
    main()