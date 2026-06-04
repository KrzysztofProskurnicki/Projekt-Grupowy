"""Main application window - Password Manager."""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout,  QLabel, QLineEdit, QListWidget, 
                             QListWidgetItem, QPushButton, QStackedWidget,
                             QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QEvent
from PyQt5.QtGui import QFont


# Application modules
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
from widgets.password_item_widget import PasswordItemWidget
from add_password_view import AddPasswordView
from profile_view import ProfileView
from settings_view import SettingsView



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
        
        # Inicjalizuj serwisy (scoped to user)
        self.password_service = PasswordService(username)
        self.settings_service = SettingsService()
        self.current_filter = FILTER_ALL
        
        # Setup Auto-Lock Timer
        self.auto_lock_timer = QTimer(self)
        self.auto_lock_timer.timeout.connect(self._on_auto_lock)
        self._update_auto_lock_timer()
        
        # Install event filter to track user activity for Auto-Lock
        QApplication.instance().installEventFilter(self)
        
        # Setup Clipboard Auto-Clear
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
        
        # --- SIDEBAR (Left side) ---
        self.sidebar = Sidebar(username=username)
        self.sidebar.nav_clicked.connect(self.handle_nav_click)
        self.sidebar.logout_clicked.connect(self._on_logout)
        
        # --- CONTENT (Right side) ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked Widget for view switching
        self.stacked_widget = QStackedWidget()
        
        # Password list view (main view)
        self.page_list = QWidget()
        list_layout = QVBoxLayout(self.page_list)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)
        
        # Search & Actions Header
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet(f"background-color: {styles.DARK_BG}; border-bottom: 1px solid {styles.BORDER_COLOR};")
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Search Bar
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search passwords...")
        search_input.setFixedWidth(300)
        search_input.textChanged.connect(self.filter_list)
        header_layout.addWidget(search_input)
        
        header_layout.addStretch()
        
        # Add Button
        add_btn = QPushButton(" + Add ")
        add_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: #0a84ff;"
            "    color: white;"
            "    border: none;"
            "    border-radius: 6px;"
            "    padding: 8px 16px;"
            "    font-weight: 500;"
            "}"
            "QPushButton:hover { background-color: #0077ea; }"
        )
        add_btn.clicked.connect(self.show_add_form)
        header_layout.addWidget(add_btn)
        
        list_layout.addWidget(self.header_widget)
        
        # Password List
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.itemClicked.connect(self.open_detail_view)
        list_layout.addWidget(self.list_widget)
        
        self.stacked_widget.addWidget(self.page_list)  # Index 0
        
        # Detail Page
        self.page_detail = DetailView(self.show_list, self.toggle_favorite)
        self.stacked_widget.addWidget(self.page_detail)  # Index 1
        
        # Security Dashboard Page
        self.page_security = SecurityView(self.show_list, self.navigate_to_detail)
        self.stacked_widget.addWidget(self.page_security)  # Index 2
        
        # Placeholders for new pages
        self.page_vault = QLabel("Vault View (Coming Soon)")
        self.page_vault.setAlignment(Qt.AlignCenter)
        self.page_vault.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 20px;")
        self.stacked_widget.addWidget(self.page_vault)  # Index 3
        
        self.page_settings = SettingsView(self.settings_service)
        self.page_settings.settings_changed.connect(self._on_settings_changed)
        self.page_settings.theme_changed.connect(self._on_theme_changed)
        self.page_settings.font_size_changed.connect(self._on_font_size_changed)
        self.stacked_widget.addWidget(self.page_settings)  # Index 4
        
        self.page_profile = ProfileView(username, self.password_service)
        self.page_profile.account_deleted.connect(self._on_logout)
        self.stacked_widget.addWidget(self.page_profile)  # Index 5
        
        # Add Password Form Page
        self.page_add_password = AddPasswordView()
        self.page_add_password.password_created.connect(self.on_password_created)
        self.page_add_password.back_clicked.connect(self.show_list)
        self.stacked_widget.addWidget(self.page_add_password)  # Index 6
        
        content_layout.addWidget(self.stacked_widget)
        
        # Initial load
        self.refresh_list()
        self.update_badges()
            
        # Assembly
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_area)

    
    def _on_logout(self):
        """Handle logout - clear vault key, emit signal, close window."""
        QApplication.instance().removeEventFilter(self)
        self.auto_lock_timer.stop()
        AuthenticationService().logout()
        self.logout_signal.emit()
        self.close()
        
    def _on_auto_lock(self):
        """Triggered when auto-lock timer expires."""
        print("Auto-locking vault due to inactivity.")
        self._on_logout()
        
    def _update_auto_lock_timer(self):
        """Update auto-lock timer based on settings."""
        minutes = self.settings_service.auto_lock_minutes
        if minutes > 0:
            self.auto_lock_timer.start(minutes * 60 * 1000)
        else:
            self.auto_lock_timer.stop()

    def eventFilter(self, obj, event):
        """Intercept events to reset the auto-lock timer on user activity."""
        if event.type() in (QEvent.KeyPress, QEvent.MouseMove, QEvent.MouseButtonPress):
            if self.settings_service.auto_lock_minutes > 0:
                self.auto_lock_timer.start(self.settings_service.auto_lock_minutes * 60 * 1000)
        return super().eventFilter(obj, event)

    def _on_clipboard_changed(self):
        """Start clipboard clear timer if setting is enabled and clipboard has text."""
        seconds = self.settings_service.clipboard_clear_seconds
        if seconds > 0 and QApplication.clipboard().text():
            self.clipboard_clear_timer.start(seconds * 1000)

    def _clear_clipboard(self):
        """Clear the clipboard."""
        QApplication.clipboard().clear()
        
    def _on_settings_changed(self, key, value):
        if key == 'auto_lock_minutes':
            self._update_auto_lock_timer()
            
    def _on_theme_changed(self, theme):
        styles.apply_theme(theme)
        app = QApplication.instance()
        app.setStyleSheet(styles.get_stylesheet(theme))
        # Refresh all views
        self._refresh_all_views()
        
    def _refresh_all_views(self):
        """Rebuild all view UIs with current theme colors."""
        # Refresh the password list header
        self.header_widget.setStyleSheet(
            f"background-color: {styles.DARK_BG}; border-bottom: 1px solid {styles.BORDER_COLOR};"
        )
        # Refresh views that support it
        for view in (self.page_detail, self.page_security,
                     self.page_add_password, self.page_profile,
                     self.page_settings):
            if hasattr(view, 'refresh_theme'):
                view.refresh_theme()
        # Rebuild password list cards
        self.refresh_list()
        
    def _on_font_size_changed(self, size):
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(size)
        app.setFont(font)
    
    def load_data(self):
        """Load password data - delegated to service (deprecated)."""
        return self.password_service.get_all_passwords()
    
    def save_data(self):
        """Save password data - delegated to service (deprecated)."""
        self.password_service.save_passwords()
            
    def update_badges(self):
        """Update sidebar badges with counts from service."""
        self.sidebar.update_badge(NAV_INDEX_ALL_PASSWORDS, self.password_service.get_password_count())
        self.sidebar.update_badge(NAV_INDEX_FAVORITES, self.password_service.get_favorites_count())
        self.sidebar.update_badge(NAV_INDEX_SECURITY, self.password_service.get_weak_count())
    
    def refresh_list(self):
        """Refresh the password list based on current filter."""
        self.list_widget.clear()
        
        # Get passwords based on filter using service
        if self.current_filter == FILTER_FAVORITES:
            passwords = self.password_service.get_favorites()
        elif self.current_filter == FILTER_SECURITY:
            passwords = self.password_service.get_weak_passwords()
        else:
            passwords = self.password_service.get_all_passwords()
        
        for entry in passwords:
            self.add_list_item(entry)

    def filter_list(self, text):
        """Filter list by search text."""
        text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            entry = item.data(Qt.UserRole)
            if entry:
                title = entry.get("name", "").lower()
                subtitle = entry.get("email", "").lower()
                item.setHidden(text not in title and text not in subtitle)

    def add_list_item(self, entry):
        title = entry.get("name", "")
        subtitle = entry.get("email", "")
        color = entry.get("color", "#333333")
        letter = (title[0].upper() if title else "?")
        favorite = bool(entry.get("favorite", False))
        item = QListWidgetItem()
        
        # 1. Container Widget (Transparent, holds margins)
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 5, 0, 5) # Spacing between cards
        container_layout.setSpacing(0)
        
        # 2. Card Frame (Visible, holds content)
        card_frame = QFrame()
        card_frame.setMinimumHeight(80)
        card_frame.setObjectName("cardFrame")
        card_frame.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {styles.CARD_BG};
                border-radius: 12px;
            }}
            QFrame#cardFrame:hover {{
                background-color: {styles.HOVER_BG};
            }}
        """)
        
        # Content Layout inside Card
        hbox = QHBoxLayout(card_frame)
        hbox.setContentsMargins(15, 10, 15, 10)
        hbox.setSpacing(15)
        
        # Icon Circle
        icon_lbl = QLabel(letter)
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 24px;
            font-weight: bold;
            font-size: 22px;
            border: none;
        """)
        hbox.addWidget(icon_lbl)
        
        # Text Content
        text_container = QWidget()
        vbox = QVBoxLayout(text_container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.setAlignment(Qt.AlignVCenter)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 24px; font-weight: 600; color: {styles.TEXT_PRIMARY}; border: none; background: transparent;")
        
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet(f"font-size: 16px; color: {styles.TEXT_SECONDARY}; border: none; background: transparent;")
        
        vbox.addWidget(title_lbl)
        vbox.addWidget(subtitle_lbl)
        
        hbox.addWidget(text_container)
        hbox.addStretch()
        
        # Favorite Icon
        if favorite:
            fav_lbl = QLabel("⭐")
            fav_lbl.setStyleSheet("font-size: 16px; background: transparent; border: none;")
            hbox.addWidget(fav_lbl)
            
        # Chevron
        chevron = QLabel("›")
        chevron.setStyleSheet(f"color: {styles.TEXT_SECONDARY}; font-size: 24px; font-weight: bold; background: transparent; border: none;")
        hbox.addWidget(chevron)
        
        # Add Card to Container
        container_layout.addWidget(card_frame)
        
        item.setSizeHint(container_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, container_widget)
        
        # Store the full decrypted entry on the item so the detail view
        # can show actual password / notes / etc. without re-querying.
        item.setData(Qt.UserRole, entry)

    def open_detail_view(self, item):
        entry = item.data(Qt.UserRole)
        if entry:
            self.navigate_to_detail(entry)

    def navigate_to_detail(self, entry):
        """Navigate to detail view with the given decrypted entry dict."""
        self.page_detail.update_data(entry)
        self.stacked_widget.setCurrentIndex(VIEW_INDEX_DETAIL)
            
    def show_list(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def handle_nav_click(self, index):
        """Handle navigation button click from sidebar."""
        if index == NAV_INDEX_ALL_PASSWORDS:
            self.current_filter = FILTER_ALL
            self.refresh_list()
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_PASSWORD_LIST)
        elif index == NAV_INDEX_FAVORITES:
            self.current_filter = FILTER_FAVORITES
            self.refresh_list()
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_PASSWORD_LIST)
        elif index == NAV_INDEX_SECURITY:
            self.current_filter = FILTER_SECURITY
            self.page_security.update_stats(self.password_service.get_all_passwords())
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_SECURITY)
        elif index == NAV_INDEX_VAULT:
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_VAULT)
        elif index == NAV_INDEX_SETTINGS:
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_SETTINGS)
        elif index == NAV_INDEX_PROFILE:
            self.stacked_widget.setCurrentIndex(VIEW_INDEX_PROFILE)
    
    def toggle_favorite(self, name, is_favorite):
        """Toggle favorite status for a password using service."""
        self.password_service.toggle_favorite(name, is_favorite)
        self.update_badges()
        
    def show_add_form(self):
        """Show the add password form."""
        self.stacked_widget.setCurrentIndex(6)
    
    def on_password_created(self, password_data):
        """Handle new password created from form."""
        self.password_service.add_password(password_data)
        self.refresh_list()
        self.update_badges()
        self.show_list()


def run_app():
    """Run the application with login/logout loop."""
    # One-shot migration from the legacy plaintext users.json into the
    # encrypted SQLite vault. Safe to call on every launch (idempotent).
    migrate_if_needed()

    app = QApplication(sys.argv)

    # Ustawienie fontu na systemowy sans-serif z configu
    from services.settings_service import SettingsService
    settings = SettingsService()
    font = QFont("Segoe UI", settings.font_size) if sys.platform == "win32" else QFont("Helvetica Neue", settings.font_size)
    app.setFont(font)

    # Aplikowanie stylów z configu
    styles.apply_theme(settings.theme)
    app.setStyleSheet(styles.get_stylesheet(settings.theme))
    
    while True:
        # Show Login Dialog
        login = LoginDialog()
        login.show()
        app.exec_()
        
        if not login.authenticated:
            # User closed login window without logging in
            break
        
        # User authenticated - open main window
        username = login.logged_in_username
        window = MainWindow(username)
        window.show()
        
        # Track logout state
        logout_requested = [False]
        
        def on_logout():
            logout_requested[0] = True
            app.quit()
        
        window.logout_signal.connect(on_logout)
        app.exec_()
        
        if not logout_requested[0]:
            # User closed main window (not via logout) - exit app
            break
        
        # Logout was requested - loop back to login
    
    sys.exit(0)


if __name__ == "__main__":
    run_app()