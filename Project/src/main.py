"""Główne okno aplikacji - menedżera haseł"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout,  QLabel, QLineEdit, QListWidget, 
                             QListWidgetItem, QPushButton, QStackedWidget,
                             QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QEvent, QSize
from PyQt5.QtGui import QFont, QIcon

from styles import *
import styles
from config import *
from constants import *
from login_dialog import LoginDialog
from sidebar import Sidebar
from security_dashboard import SecurityView
from detail_view import DetailView
from services.password_service import PasswordService
from services.authentication_service import AuthenticationService
from services.migration import migrate_if_needed
from services.settings_service import SettingsService
from add_password_view import AddPasswordModal
from profile_view import ProfileView
from settings_view import SettingsView
from widgets.icons import tinted_pixmap, app_icon



class MainWindow(QMainWindow):
    """Główne okno aplikacji."""
    
    logout_signal = pyqtSignal()
    
    def __init__(self, username: str):
        """Inicjalizuj główne okno dla zalogowanego użytkownika.
        
        Args:
            username: Nazwa zalogowanego użytkownika.
        """
        super().__init__()
        self._username = username
        
        # Ustawienia okna
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        styles.apply_titlebar_theme(self)
        
        # Inicjalizuj serwisy w zakresie użytkownika
        self.password_service = PasswordService(username)
        self.settings_service = SettingsService()
        self.current_filter = FILTER_ALL
        
        # Skonfiguruj timer automatycznej blokady
        self.auto_lock_timer = QTimer(self)
        self.auto_lock_timer.timeout.connect(self._on_auto_lock)
        self._update_auto_lock_timer()
        
        # Zainstaluj filtr zdarzeń śledz?ący aktywność użytkownika dla automatycznej blokady
        QApplication.instance().installEventFilter(self)
        
        # Skonfiguruj automatyczne czyszczenie schowka
        self.clipboard_clear_timer = QTimer(self)
        self.clipboard_clear_timer.setSingleShot(True)
        self.clipboard_clear_timer.timeout.connect(self._clear_clipboard)
        QApplication.clipboard().dataChanged.connect(self._on_clipboard_changed)
        
        # Główny kontener
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout główny (Sidebar | Treść)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- SIDEBAR (lewa strona) ---
        self.sidebar = Sidebar(username=username)
        self.sidebar.nav_clicked.connect(self.handle_nav_click)
        self.sidebar.logout_clicked.connect(self._on_logout)
        
        # --- CONTENT (prawa strona) ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # QStackedWidget do przełączania widoków
        self.stacked_widget = QStackedWidget()
        
        # Widok listy haseł + panel szczegółów (dwukolumnowy, wg wzorca Vault)
        self.selected_name = None
        self.page_list = QWidget()
        list_page_layout = QHBoxLayout(self.page_list)
        list_page_layout.setContentsMargins(0, 0, 0, 0)
        list_page_layout.setSpacing(0)

        # --- Lewa kolumna: tytuł + Add + szukajka + lista wpisów ---
        self.list_column = QWidget()
        self.list_column.setObjectName("listColumn")
        self.list_column.setFixedWidth(360)
        column_layout = QVBoxLayout(self.list_column)
        column_layout.setContentsMargins(0, 0, 0, 0)
        column_layout.setSpacing(0)

        self.header_widget = QWidget()
        self.header_widget.setObjectName("listHeader")
        header_layout = QVBoxLayout(self.header_widget)
        header_layout.setContentsMargins(16, 20, 16, 12)
        header_layout.setSpacing(14)

        title_row = QHBoxLayout()
        self.list_title = QLabel("All Passwords")
        title_row.addWidget(self.list_title)
        title_row.addStretch()

        # Przycisk dodawania
        self.add_btn = QPushButton("  Add")
        self.add_btn.setIcon(QIcon(tinted_pixmap("plus", "#ffffff", 15)))
        self.add_btn.setIconSize(QSize(15, 15))
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self.show_add_form)
        title_row.addWidget(self.add_btn)
        header_layout.addLayout(title_row)

        # Pasek wyszukiwania
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search vault...")
        self.search_input.textChanged.connect(self.filter_list)
        header_layout.addWidget(self.search_input)

        column_layout.addWidget(self.header_widget)

        # Pusty stan listy (np. brak ulubionych)
        self.empty_label = QLabel("")
        self.empty_label.setWordWrap(True)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.hide()
        column_layout.addWidget(self.empty_label)

        # Lista haseł
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.currentItemChanged.connect(self.on_current_item_changed)
        column_layout.addWidget(self.list_widget)

        list_page_layout.addWidget(self.list_column)

        # --- Prawa kolumna: panel szczegółów wpisu ---
        self.page_detail = DetailView(self.show_list, self.toggle_favorite,
                                      self.show_edit_form)
        list_page_layout.addWidget(self.page_detail, 1)

        self._apply_list_chrome()

        self.stacked_widget.addWidget(self.page_list)     # VIEW_INDEX_PASSWORD_LIST

        # Strona panelu bezpieczeństwa
        self.page_security = SecurityView(self.show_list, self.navigate_to_detail)
        self.stacked_widget.addWidget(self.page_security)  # VIEW_INDEX_SECURITY

        self.page_settings = SettingsView(self.settings_service)
        self.page_settings.settings_changed.connect(self._on_settings_changed)
        self.page_settings.theme_changed.connect(self._on_theme_changed)
        self.page_settings.accent_changed.connect(self._on_accent_changed)
        self.page_settings.font_size_changed.connect(self._on_font_size_changed)
        self.stacked_widget.addWidget(self.page_settings)  # VIEW_INDEX_SETTINGS

        self.page_profile = ProfileView(username, self.password_service)
        self.page_profile.account_deleted.connect(self._on_logout)
        self.stacked_widget.addWidget(self.page_profile)   # VIEW_INDEX_PROFILE

        content_layout.addWidget(self.stacked_widget)

        self.refresh_list()
        self.update_badges()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_area)

    
    def _on_logout(self):
        """Obsługa wylogowania: wyczyszczenie klucza sejfu, emisja sygnału i zamknięcie okna"""
        QApplication.instance().removeEventFilter(self)
        self.auto_lock_timer.stop()
        AuthenticationService().logout()
        self.logout_signal.emit()
        self.close()
        
    def _on_auto_lock(self):
        """Wywoływane po upływie timera automatycznej blokady"""
        print("Auto-locking vault due to inactivity.")
        self._on_logout()
        
    def _update_auto_lock_timer(self):
        """Zaktualizuj timer automatycznej blokady na podstawie ustawień"""
        minutes = self.settings_service.auto_lock_minutes
        if minutes > 0:
            self.auto_lock_timer.start(minutes * 60 * 1000)
        else:
            self.auto_lock_timer.stop()

    def eventFilter(self, obj, event):
        """Przechwytywanie zdarzenia, aby resetować timer automatycznej blokady przy aktywności użytkownika"""
        if event.type() in (QEvent.KeyPress, QEvent.MouseMove, QEvent.MouseButtonPress):
            if self.settings_service.auto_lock_minutes > 0:
                self.auto_lock_timer.start(self.settings_service.auto_lock_minutes * 60 * 1000)
        return super().eventFilter(obj, event)

    def _on_clipboard_changed(self):
        """Uruchom timer czyszczenia schowka, jeśli ustawienie jest włączone i schowek zawiera tekst"""
        seconds = self.settings_service.clipboard_clear_seconds
        if seconds > 0 and QApplication.clipboard().text():
            self.clipboard_clear_timer.start(seconds * 1000)

    def _clear_clipboard(self):
        QApplication.clipboard().clear()
        
    def _on_settings_changed(self, key, value):
        if key == 'auto_lock_minutes':
            self._update_auto_lock_timer()
            
    def _on_theme_changed(self, theme):
        styles.apply_theme(theme)
        app = QApplication.instance()
        app.setStyleSheet(styles.get_stylesheet(theme))
        styles.apply_titlebar_theme(self, theme)
        self._refresh_all_views()

    def _on_accent_changed(self, accent):
        styles.apply_accent(accent)
        app = QApplication.instance()
        app.setStyleSheet(styles.get_stylesheet(self.settings_service.theme))
        self._refresh_all_views()
        
    def _apply_list_chrome(self):
        """Ustaw style lewej kolumny listy (nagłówek, szukajka, lista, pusty stan)."""
        self.list_column.setStyleSheet(
            f"QWidget#listColumn {{ background-color: {styles.DARK_BG};"
            f" border-right: 1px solid {styles.HAIRLINE}; }}"
        )
        self.header_widget.setStyleSheet(
            "QWidget#listHeader { background: transparent; border: none; }"
        )
        self.list_title.setStyleSheet(
            f"font-size: {styles.font_px(21)}px; font-weight: bold; color: {styles.TEXT_PRIMARY};"
            " background: transparent; border: none;"
        )
        self.empty_label.setStyleSheet(
            f"color: {styles.TEXT_TERTIARY}; font-size: {styles.font_px(14)}px; padding: 40px 16px;"
            " background: transparent; border: none;"
        )
        self.add_btn.setStyleSheet(
            "QPushButton {"
            f"    background-color: {styles.COLOR_BLUE};"
            "    color: white;"
            "    border: none;"
            "    border-radius: 8px;"
            "    padding: 7px 14px;"
            f"    font-size: {styles.font_px(13)}px;"
            "    font-weight: 600;"
            "}"
            f"QPushButton:hover {{ background-color: {styles.COLOR_BLUE_HOVER}; }}"
        )
        # Wysokość szukajki skaluje się z fontem (sztywna ucina descendery)
        self.search_input.setFixedHeight(styles.font_px(38))
        # Ikona lupy w polu wyszukiwania (re-tint przy zmianie motywu)
        if getattr(self, "_search_action", None) is not None:
            self.search_input.removeAction(self._search_action)
        self._search_action = self.search_input.addAction(
            QIcon(tinted_pixmap("search", styles.TEXT_TERTIARY, 16)),
            QLineEdit.LeadingPosition,
        )
        # Zaznaczenie: tint akcentu + pasek z lewej (jak EntryRow we wzorcu)
        self.list_widget.setStyleSheet(f"""
            QListWidget {{ background: transparent; border: none; outline: none; }}
            QListWidget::item {{
                background: transparent; border: none;
                border-radius: 8px; margin: 1px 8px;
            }}
            QListWidget::item:hover {{ background-color: {styles.OVERLAY_HOVER}; }}
            QListWidget::item:selected {{
                background-color: {styles.ACCENT_TINT};
                border-left: 3px solid {styles.COLOR_BLUE};
            }}
        """)

    def _refresh_all_views(self):
        """Przebuduj interfejsy wszystkich widoków z bieżącym kolorem motywu"""
        self.sidebar.refresh_theme()
        self._apply_list_chrome()
        # Odśwież widok okna
        for view in (self.page_detail, self.page_security,
                     self.page_profile, self.page_settings):
            if hasattr(view, 'refresh_theme'):
                view.refresh_theme()
        # Przebuduj karty listy haseł
        self.refresh_list()
        
    def _on_font_size_changed(self, size):
        styles.set_font_size(size)
        app = QApplication.instance()
        # Rozmiar w pikselach, spójnie ze skalą QSS; bazowy rozmiar tekstu
        # i tak narzuca reguła QWidget w arkuszu stylów (setFont bywa
        # ignorowany przy aktywnym stylesheecie)
        font = app.font()
        font.setPixelSize(styles.font_px(14))
        app.setFont(font)
        app.setStyleSheet(styles.get_stylesheet(self.settings_service.theme))
        # Odrocz przebudowę widoków - sygnał przychodzi z suwaka, którego nie
        # wolno zniszczyć w trakcie obsługi jego własnego sygnału
        QTimer.singleShot(0, self._refresh_all_views)
    
    def load_data(self):
        return self.password_service.get_all_passwords()
    
    def save_data(self):
        self.password_service.save_passwords()
            
    def update_badges(self):
        """Zaktualizuj liczniki sidebara wartościami z serwisu"""
        self.sidebar.update_badge(NAV_INDEX_ALL_PASSWORDS, self.password_service.get_password_count())
        self.sidebar.update_badge(NAV_INDEX_FAVORITES, self.password_service.get_favorites_count())
        self.sidebar.update_badge(NAV_INDEX_SECURITY, self.password_service.get_weak_count())
    
    def refresh_list(self):
        """Odświeżanie listy haseł na podstawie bieżącego filtru"""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        if self.current_filter == FILTER_FAVORITES:
            passwords = self.password_service.get_favorites()
        elif self.current_filter == FILTER_SECURITY:
            passwords = self.password_service.get_weak_passwords()
        else:
            passwords = self.password_service.get_all_passwords()

        for entry in passwords:
            self.add_list_item(entry)
        self.list_widget.blockSignals(False)

        if not passwords:
            if self.current_filter == FILTER_FAVORITES:
                self.empty_label.setText(
                    "No favorites yet.\nTap the star on an entry to add it."
                )
            else:
                self.empty_label.setText(
                    "No passwords yet.\nClick Add to create your first entry."
                )
            self.empty_label.show()
            self.page_detail.show_empty()
            return

        self.empty_label.hide()
        # Przywróć zaznaczenie (lub wybierz pierwszy wpis) - aktualizuje panel
        row = 0
        for i in range(self.list_widget.count()):
            e = self.list_widget.item(i).data(Qt.UserRole)
            if e and e.get("name") == self.selected_name:
                row = i
                break
        self.list_widget.setCurrentRow(row)

    def filter_list(self, text):
        text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            entry = item.data(Qt.UserRole)
            if entry:
                title = entry.get("name", "").lower()
                subtitle = entry.get("email", "").lower()
                item.setHidden(text not in title and text not in subtitle)

    def add_list_item(self, entry):
        """Dodaj kompaktowy wiersz wpisu (EntryRow wg wzorca: awatar + nazwa/login + gwiazdka)."""
        title = entry.get("name", "")
        subtitle = entry.get("email", "")
        color = entry.get("color", "#333333")
        letter = (title[0].upper() if title else "?")
        favorite = bool(entry.get("favorite", False))
        item = QListWidgetItem()

        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent; border: none;")
        hbox = QHBoxLayout(row_widget)
        hbox.setContentsMargins(14, 10, 10, 10)
        hbox.setSpacing(12)

        # Kafelek z literą
        icon_lbl = QLabel(letter)
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 10px;
            font-weight: bold;
            font-size: {styles.font_px(16)}px;
            border: none;
        """)
        hbox.addWidget(icon_lbl)

        # Nazwa + login
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent; border: none;")
        vbox = QVBoxLayout(text_container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(2)
        vbox.setAlignment(Qt.AlignVCenter)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: {styles.font_px(15)}px; font-weight: 500; color: {styles.TEXT_PRIMARY}; border: none; background: transparent;")
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet(f"font-size: {styles.font_px(13)}px; color: {styles.TEXT_SECONDARY}; border: none; background: transparent;")
        vbox.addWidget(title_lbl)
        vbox.addWidget(subtitle_lbl)

        hbox.addWidget(text_container, 1)

        # Klikalna gwiazdka - dodaje/usuwa wpis z ulubionych bez wchodzenia w szczegóły.
        star_btn = QPushButton()
        star_btn.setFixedSize(28, 28)
        star_btn.setCursor(Qt.PointingHandCursor)
        star_btn.setIconSize(QSize(16, 16))
        star_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 6px; }"
            f"QPushButton:hover {{ background-color: {styles.HOVER_BG}; }}"
        )
        if favorite:
            star_btn.setIcon(QIcon(tinted_pixmap("star-filled", styles.COLOR_YELLOW, 16)))
            star_btn.setToolTip("Remove from favorites")
        else:
            star_btn.setIcon(QIcon(tinted_pixmap("star", styles.TEXT_TERTIARY, 16)))
            star_btn.setToolTip("Add to favorites")
        star_btn.clicked.connect(lambda checked, n=title: self.on_star_clicked(n))
        hbox.addWidget(star_btn)

        # Chevron (SVG)
        chevron = QLabel()
        chevron.setFixedSize(16, 16)
        chevron.setPixmap(tinted_pixmap("chevron-right", styles.TEXT_TERTIARY, 16))
        chevron.setStyleSheet("background: transparent; border: none;")
        hbox.addWidget(chevron)

        item.setSizeHint(row_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, row_widget)

        item.setData(Qt.UserRole, entry)

    def on_current_item_changed(self, current, previous):
        """Aktualizuj panel szczegółów po zmianie zaznaczenia na liście."""
        if current is None:
            return
        entry = current.data(Qt.UserRole)
        if entry:
            self.selected_name = entry.get("name")
            self.page_detail.update_data(entry)

    def navigate_to_detail(self, entry):
        """Przejdź do widoku listy i pokaż wpis w panelu szczegółów."""
        self.selected_name = entry.get("name")
        self.sidebar.handle_click(NAV_INDEX_ALL_PASSWORDS)

    def show_list(self):
        self.stacked_widget.setCurrentIndex(VIEW_INDEX_PASSWORD_LIST)
    
    def handle_nav_click(self, index):
        """Obsługa kliknięcia przycisku nawigacji w sidebarze"""
        if index == NAV_INDEX_ALL_PASSWORDS:
            self.current_filter = FILTER_ALL
            self.list_title.setText("All Passwords")
            self.add_btn.show()
            self.refresh_list()
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_PASSWORD_LIST)
        elif index == NAV_INDEX_FAVORITES:
            self.current_filter = FILTER_FAVORITES
            # Ulubione dodaje się tylko gwiazdką w "All Passwords" - tu bez dodawania
            self.list_title.setText("Favorites")
            self.add_btn.hide()
            self.refresh_list()
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_PASSWORD_LIST)
        elif index == NAV_INDEX_SECURITY:
            self.page_security.update_stats(self.password_service.get_all_passwords())
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_SECURITY)
        elif index == NAV_INDEX_SETTINGS:
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_SETTINGS)
        elif index == NAV_INDEX_PROFILE:
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_PROFILE)

    def toggle_favorite(self, name, is_favorite):
        """Przełączanie statusu ulubionego z panelu szczegółów"""
        self.password_service.toggle_favorite(name, is_favorite)
        self.update_badges()
        # Lista jest widoczna obok panelu - odśwież gwiazdki na wierszach
        self.refresh_list()

    def on_star_clicked(self, name):
        """Przełącz status ulubionego z wiersza na liście (All Passwords i Favorites)."""
        entry = next(
            (e for e in self.password_service.get_all_passwords() if e.get("name") == name),
            None,
        )
        if entry is None:
            return
        new_state = not bool(entry.get("favorite", False))
        self.password_service.toggle_favorite(name, new_state)
        self.update_badges()
        # Odśwież listę: w "Favorites" odznaczony wpis znika, gwiazdki i panel
        # szczegółów aktualizują się przez ponowne zaznaczenie wiersza
        self.refresh_list()

    def show_add_form(self):
        """Otwórz modal dodawania hasła (wyśrodkowana karta na przyciemnionym tle)."""
        names = [e.get("name") for e in self.password_service.get_all_passwords()]
        modal = AddPasswordModal(self, existing_names=names)
        modal.password_created.connect(self.on_password_created)
        modal.show()

    def show_edit_form(self, entry):
        """Otwórz modal edycji wskazanego wpisu."""
        if not entry:
            return
        names = [e.get("name") for e in self.password_service.get_all_passwords()]
        modal = AddPasswordModal(self, entry=entry, existing_names=names)
        modal.password_edited.connect(self.on_password_edited)
        modal.show()

    def on_password_created(self, password_data):
        self.password_service.add_password(password_data)
        self.selected_name = password_data.get("name")
        self.refresh_list()
        self.update_badges()

    def on_password_edited(self, original_name, password_data):
        self.password_service.update_password(original_name, password_data)
        self.selected_name = password_data.get("name")
        self.refresh_list()
        self.update_badges()


def run_app():
    """Uruchomienie aplikacj z pętlą logowania/wylogowania"""
    # Jednorazowa migracja ze starego jawnego users.json do szyfrowanego sejfu SQLite. Bezpieczna przy każdym starcie.
    migrate_if_needed()

    # Własny AppUserModelID - bez tego pasek zadań grupuje okno pod ikoną
    # interpretera Pythona zamiast ikony aplikacji
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PasswordManager.App")

    app = QApplication(sys.argv)
    app.setWindowIcon(app_icon())

    # Ustawienie fontu na systemowy sans-serif z configu
    # (rozmiar w pikselach - punkty zależą od DPI i rozjeżdżają się ze skalą QSS)
    from services.settings_service import SettingsService
    settings = SettingsService()
    font = QFont("Segoe UI") if sys.platform == "win32" else QFont("Helvetica Neue")
    font.setPixelSize(settings.font_size)
    app.setFont(font)

    # Aplikowanie stylów z configu (motyw + wybrany akcent + skala fontu)
    styles.set_font_size(settings.font_size)
    styles.apply_theme(settings.theme)
    styles.apply_accent(settings.accent)
    app.setStyleSheet(styles.get_stylesheet(settings.theme))
    
    while True:
        # Pokaż okno logowania
        login = LoginDialog()
        login.show()
        app.exec_()
        
        if not login.authenticated:
            # Użytkownik zamknoł okno logowania bez logowania
            break
        
        # Użytkownik uwierzytelniony
        username = login.logged_in_username
        window = MainWindow(username)
        window.show()

        logout_requested = [False]
        
        def on_logout():
            logout_requested[0] = True
            app.quit()
        
        window.logout_signal.connect(on_logout)
        app.exec_()
        
        if not logout_requested[0]:
            # Użytkownik zamknoł główne okno bez wylogowania - zakończ działanie aplikacji
            break

    
    sys.exit(0)


if __name__ == "__main__":
    run_app()