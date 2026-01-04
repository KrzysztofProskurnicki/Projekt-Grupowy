import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QListWidget, 
                             QListWidgetItem, QFrame, QPushButton, QScrollArea,
                             QSpacerItem, QSizePolicy, QStackedWidget)
from detail_view import DetailView
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QIcon

# --- KONFIGURACJA STYLU (QSS) ---
# Kolory i style wyciągnięte bezpośrednio z Twojego pliku JSON
STYLESHEET = """
QMainWindow {
    background-color: #1c1c1e;
}

/* Sidebar */
#Sidebar {
    background-color: #1c1c1e;
    border-right: 1px solid #38383a;
    min-width: 300px;
    max-width: 300px;
}

#AppTitle {
    font-size: 20px;
    font-weight: 600;
    color: #f5f5f7;
    padding: 16px;
    border-bottom: 1px solid #38383a;
}

/* Sidebar Buttons */
QPushButton.nav-btn {
    text-align: left;
    background-color: transparent;
    color: #f5f5f7;
    border-radius: 10px;
    padding: 10px 14px;
    border: none;
    font-size: 20px;
}

QPushButton.nav-btn:checked {
    background-color: #0a84ff;
    color: white;
}

/* Badge (licznik) */
QLabel.badge {
    color: #98989d;
    font-size: 20px;
}
QPushButton.nav-btn:checked + QLabel.badge {
    color: white; /* Badge biały gdy aktywny */
}

/* Content Area */
QLineEdit {
    background-color: #2c2c2e;
    color: #f5f5f7;
    border-radius: 6px;
    padding: 10px;
    padding-left: 12px;
    border: none;
    font-size: 16px;
}

#SearchContainer {
    padding: 12px;
    border-bottom: 1px solid #38383a;
    background-color: #1c1c1e;
}

QListWidget {
    background-color: #1c1c1e;
    border: none;
    outline: none;
}

QListWidget::item {
    border-bottom: 1px solid #2c2c2e;
    padding: 0px;
}

QListWidget::item:selected {
    background-color: #2c2c2e;
}

/* Scrollbar styling for dark mode */
QScrollBar:vertical {
    border: none;
    background: #1c1c1e;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #38383a;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

class NavButtonWidget(QWidget):
    """
    Niestandardowy widget dla przycisków menu bocznego (Ikona + Tekst + Spacer + Licznik)
    """
    def __init__(self, text, icon_char, count, is_active=False):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)
        
        self.btn = QPushButton(f" {icon_char}   {text}")
        self.btn.setProperty("class", "nav-btn")
        self.btn.setCheckable(True)
        self.btn.setChecked(is_active)
        self.btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Prosta emulacja ikon za pomocą znaków unicode
        
        self.badge = QLabel(str(count))
        self.badge.setProperty("class", "badge")
        if is_active:
            self.badge.setStyleSheet("color: white;") # Nadpisanie stylu dla aktywnego

        # Stackowanie buttona i badge'a (Button jest tłem)
        # W PyQt prościej zrobić Layout poziomy z przyciskiem, który wypełnia wszystko
        # Tutaj dla uproszczenia układamy layout
        
        layout.addWidget(self.btn)
        
        # Badge "pływa" po prawej stronie wewnątrz layoutu przycisku w bardziej zaawansowanych UI,
        # tutaj zrobimy prosto: Button | Badge
        
        # Aby uzyskać efekt "Badge wewnątrz przycisku", trzeba by subclassować paintEvent.
        # Zrobimy prościej: Ustawimy Layout na przycisku.
        
        self.btn_layout = QHBoxLayout(self.btn)
        self.btn_layout.setContentsMargins(10, 0, 10, 0)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.badge)
        
        self.setLayout(layout)

class PasswordItemWidget(QWidget):
    """
    Niestandardowy widget dla pojedynczego wiersza na liście haseł.
    Odwzorowuje strukturę: Ikona | (Tytuł + Podtytuł)
    """
    def __init__(self, title, subtitle, color="#2c2c2e", letter="A"):
        super().__init__()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 1. Ikona (Favicon)
        self.icon_label = QLabel(letter)
        self.icon_label.setFixedSize(50, 50)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            background-color: {color};
            color: #f5f5f7;
            border-radius: 10px;
            font-size: 30px;
            font-weight: bold;
        """)
        
        # 2. Tekst (Tytuł i Podtytuł)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: #f5f5f7; font-size: 30px; font-weight: 550;")
        
        self.subtitle_lbl = QLabel(subtitle)
        self.subtitle_lbl.setStyleSheet("color: #98989d; font-size: 20px;")
        
        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.subtitle_lbl)
        text_layout.addStretch()
        
        layout.addWidget(self.icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Manager UI")
        self.resize(1000, 700)
        
        # Główny widget kontenera
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Główny układ poziomy (Sidebar | Content)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- SIDEBAR (Lewa strona) ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Sidebar Header
        app_title = QLabel("Passwords")
        app_title.setObjectName("AppTitle")
        sidebar_layout.addWidget(app_title)
        
        # Navigation
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(4)
        
        # Przyciski nawigacji (Symulacja ikon Unicode)
        # Klucz = 🔑, Gwiazdka = ⭐, Tarcza = 🛡️
        btn_all = NavButtonWidget("All Passwords", "🔑", 12, is_active=True)
        btn_fav = NavButtonWidget("Favorites", "⭐", 3)
        btn_sec = NavButtonWidget("Security Recommendations", "🛡️", 2)
        
        nav_layout.addWidget(btn_all)
        nav_layout.addWidget(btn_fav)
        nav_layout.addWidget(btn_sec)
        nav_layout.addStretch() # Wypchnij do góry
        
        sidebar_layout.addWidget(nav_container)
        
        # --- CONTENT AREA (Prawa strona) ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Search Header
        self.page_list = QWidget() # Strona z listą
        list_layout = QVBoxLayout(self.page_list)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)
        
        search_container = QFrame()
        search_container.setObjectName("SearchContainer")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(12, 12, 12, 12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search")
        search_layout.addWidget(self.search_input)
        
        list_layout.addWidget(search_container)
        
        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.open_detail_view) # Connect click event
        list_layout.addWidget(self.list_widget)

        # STACKED WIDGET
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.page_list) # Index 0
        
        # Detail Page
        self.page_detail = DetailView(self.show_list) # Index 1
        self.stacked_widget.addWidget(self.page_detail)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Dodawanie danych (zgodnie ze zdjęciem)
        # Store data in a way we can retrieve it later, e.g. use item data or just lookup
        # For simplicity, we'll store it in the item itself via setData() or just use the widgets text
        # But QListWidget items don't hold the data directly if we use setItemWidget. 
        # We need a mapping or store data in user roles.
        
        data = [
            ("GitHub", "john.doe@email.com", "#24292e", "G"),
            ("Gmail", "john.doe@gmail.com", "#db4437", "G"),
            ("Netflix", "john.doe@email.com", "#e50914", "N"),
            ("Amazon", "johndoe@email.com", "#232f3e", "A"),
            ("Spotify", "john.doe@email.com", "#1db954", "S"),
            ("LinkedIn", "john.doe", "#0077b5", "L"),
            ("Dropbox", "john.doe@email.com", "#0061ff", "D"),
            ("Twitter", "@johndoe", "#1da1f2", "T"),
            ("Apple ID", "john.doe@icloud.com", "#555555", "A"),
            ("PayPal", "john.doe@email.com", "#003087", "P"),
            ("Microsoft", "john.doe@outlook.com", "#00a4ef", "M"),
            ("Adobe", "john.doe@email.com", "#ff0000", "A"),
            ("Facebook", "john.doe@email.com", "#1877f2", "F"),
            ("Instagram", "john.doe@email.com", "#e4405f", "I"),
            ("TikTok", "john.doe@email.com", "#ff0000", "T"),
            ("WhatsApp", "john.doe@email.com", "#25d366", "W"),
            ("Telegram", "john.doe@email.com", "#0088cc", "T"),
            ("Slack", "john.doe@email.com", "#3aaf85", "S"),
            ("Discord", "john.doe@email.com", "#5865f2", "D"),
            ("Twitch", "john.doe@email.com", "#6441a5", "T"),
            
        ]
        
        for name, email, color, letter in data:
            self.add_list_item(name, email, color, letter)
            
        # Składanie całości
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_area)

    def add_list_item(self, title, subtitle, color, letter):
        # Tworzymy pusty element listy
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(QSize(0, 100)) # Wysokość wiersza
        
        # Tworzymy nasz customowy widget
        widget = PasswordItemWidget(title, subtitle, color, letter)
        
        # Wstawiamy widget w miejsce elementu listy
        self.list_widget.setItemWidget(item, widget)
        
        # Store data in item for retrieval
        item.setData(Qt.UserRole, (title, subtitle, color, letter))

    def open_detail_view(self, item):
        data = item.data(Qt.UserRole)
        if data:
            title, subtitle, color, letter = data
            self.page_detail.update_data(title, subtitle, color, letter)
            self.stacked_widget.setCurrentIndex(1)
            
    def show_list(self):
        self.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ustawienie fontu na systemowy sans-serif
    font = QFont("Segoe UI", 14) if sys.platform == "win32" else QFont("Helvetica Neue", 14)
    app.setFont(font)
    
    # Aplikowanie stylów
    app.setStyleSheet(STYLESHEET)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())