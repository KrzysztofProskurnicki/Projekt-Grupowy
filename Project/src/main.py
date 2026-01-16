import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QListWidget, 
                             QListWidgetItem, QFrame, QPushButton, QScrollArea,
                             QSpacerItem, QSizePolicy, QStackedWidget,
                             QInputDialog, QMessageBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QProgressBar)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QIcon

# Import refactored modules
from styles import *
from login_dialog import LoginDialog
from sidebar import Sidebar
from security_dashboard import SecurityView
from detail_view import DetailView

# Data file paths
DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/passwords.json')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../config/config.json')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Manager UI")
        self.resize(1100, 700)
        self.setMinimumSize(1100, 700)
        
        # Główny widget kontenera
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Główny układ poziomy (Sidebar | Content)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- SIDEBAR (Lewa strona) ---
        self.sidebar = Sidebar()
        self.sidebar.nav_clicked.connect(self.handle_nav_click)
        
        # --- CONTENT (Prawa strona) ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked Widget do przełączania widoków
        self.stacked_widget = QStackedWidget()
        
        # Widok listy haseł (główny widok)
        self.page_list = QWidget()
        list_layout = QVBoxLayout(self.page_list)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)
        
        # Search & Actions Header
        header_widget = QWidget()
        header_widget.setStyleSheet(f"background-color: {DARK_BG}; border-bottom: 1px solid #38383a;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Search Bar
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search passwords...")
        search_input.setFixedWidth(300)
        search_input.textChanged.connect(self.filter_list)
        header_layout.addWidget(search_input)
        
        header_layout.addStretch()
        
        # Add Button
        add_btn = QPushButton(" + New Item ")
        add_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: #0a84ff;"
            "    color: white;"
            "    border: none;"
            "    border-radius: 6px;"
            "    padding: 8px 16px;"
            "    font-weight: 600;"
            "}"
            "QPushButton:hover { background-color: #0077ea; }"
        )
        add_btn.clicked.connect(self.add_new_item)
        header_layout.addWidget(add_btn)
        
        list_layout.addWidget(header_widget)
        
        # Password List
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.itemClicked.connect(self.open_detail_view)
        list_layout.addWidget(self.list_widget)
        
        self.stacked_widget.addWidget(self.page_list) # Index 0
        
        # Detail Page - pass favorite callback for persistence
        self.page_detail = DetailView(self.show_list, self.toggle_favorite)
        self.stacked_widget.addWidget(self.page_detail) # Index 1
        
        # Security Dashboard Page
        self.page_security = SecurityView(self.show_list, self.navigate_to_detail)
        self.stacked_widget.addWidget(self.page_security) # Index 2
        
        # Placeholders for new pages
        self.page_vault = QLabel("Vault View (Coming Soon)")
        self.page_vault.setAlignment(Qt.AlignCenter)
        self.page_vault.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 20px;")
        self.stacked_widget.addWidget(self.page_vault) # Index 3
        
        self.page_settings = QLabel("Settings View (Coming Soon)")
        self.page_settings.setAlignment(Qt.AlignCenter)
        self.page_settings.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 20px;")
        self.stacked_widget.addWidget(self.page_settings) # Index 4
        
        self.page_profile = QLabel("Profile View (Coming Soon)")
        self.page_profile.setAlignment(Qt.AlignCenter)
        self.page_profile.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 20px;")
        self.stacked_widget.addWidget(self.page_profile) # Index 5
        
        content_layout.addWidget(self.stacked_widget)
        
        # Load data from JSON file
        self.passwords_data = self.load_data()
        self.current_filter = 'all'
        
        # Initial load
        self.refresh_list()
        self.update_badges()
            
        # Składanie całości
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_area)
    
    def load_data(self):
        """Load password data from JSON file."""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save_data(self):
        """Save password data to JSON file."""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.passwords_data, f, indent=4, ensure_ascii=False)
            
    def update_badges(self):
        """Update sidebar badges."""
        total = len(self.passwords_data)
        favorites = sum(1 for p in self.passwords_data if p.get('favorite', False))
        security_issues = sum(1 for p in self.passwords_data if p.get('weak_password', False))
        
        self.sidebar.update_badge(0, total)
        self.sidebar.update_badge(1, favorites)
        self.sidebar.update_badge(2, security_issues)
    
    def refresh_list(self):
        """Refresh the password list based on current filter."""
        self.list_widget.clear()
        
        for entry in self.passwords_data:
            # Apply filter
            if self.current_filter == 'favorites' and not entry.get('favorite', False):
                continue
            if self.current_filter == 'security' and not entry.get('weak_password', False):
                continue
            
            self.add_list_item(
                entry['name'],
                entry['email'],
                entry['color'],
                entry['name'][0],
                entry.get('favorite', False)
            )
            
    def filter_list(self, text):
        """Filter list by search text."""
        text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            # Retrieve data from item
            data = item.data(Qt.UserRole)
            if data:
                title = data[0].lower()
                subtitle = data[1].lower()
                item.setHidden(text not in title and text not in subtitle)

    def add_list_item(self, title, subtitle, color, letter, favorite=False):
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
                background-color: {CARD_BG};
                border-radius: 12px;
            }}
            QFrame#cardFrame:hover {{
                background-color: #3a3a3c;
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
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {TEXT_PRIMARY}; border: none; background: transparent;")
        
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet(f"font-size: 14px; color: {TEXT_SECONDARY}; border: none; background: transparent;")
        
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
        chevron.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 24px; font-weight: bold; background: transparent; border: none;")
        hbox.addWidget(chevron)
        
        # Add Card to Container
        container_layout.addWidget(card_frame)
        
        item.setSizeHint(container_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, container_widget)
        
        # Store data for detail view
        item.setData(Qt.UserRole, (title, subtitle, color, letter, favorite))
            
    def open_detail_view(self, item):
        data = item.data(Qt.UserRole)
        if data:
            title, subtitle, color, letter, favorite = data
            self.navigate_to_detail(title, subtitle, color, letter, favorite)
            
    def navigate_to_detail(self, title, subtitle, color, letter, favorite):
        """Navigate to detail view with provided data."""
        self.page_detail.update_data(title, subtitle, color, letter, favorite)
        self.stacked_widget.setCurrentIndex(1)
            
    def show_list(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def handle_nav_click(self, index):
        """Handle navigation button click from sidebar."""
        # Index based switch
        if index == 0:
            self.current_filter = 'all'
            self.refresh_list()
            self.stacked_widget.setCurrentIndex(0)
        elif index == 1:
            self.current_filter = 'favorites'
            self.refresh_list()
            self.stacked_widget.setCurrentIndex(0)
        elif index == 2:
            # Security Dashboard
            self.current_filter = 'security' # also filter list behind scenes maybe?
            self.page_security.update_stats(self.passwords_data)
            self.stacked_widget.setCurrentIndex(2)
        elif index == 3: # Vault
            self.stacked_widget.setCurrentIndex(3)
        elif index == 4: # Settings
            self.stacked_widget.setCurrentIndex(4)
        elif index == 5: # Profile
            self.stacked_widget.setCurrentIndex(5)
    
    def toggle_favorite(self, name, is_favorite):
        """Toggle favorite status for a password and save to file."""
        for entry in self.passwords_data:
            if entry['name'] == name:
                entry['favorite'] = is_favorite
                break
        self.save_data()
        self.update_badges()
        
    def add_new_item(self):
        """Add new password item (Demo)."""
        name, ok = QInputDialog.getText(self, "New Password", "Account Name:")
        if ok and name:
            new_entry = {
                "name": name,
                "email": "username@example.com",
                "color": "#ff9f0a",
                "weak_password": True, 
                "favorite": False
            }
            self.passwords_data.append(new_entry)
            self.save_data()
            self.refresh_list()
            self.update_badges()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ustawienie fontu na systemowy sans-serif
    font = QFont("Segoe UI", 14) if sys.platform == "win32" else QFont("Helvetica Neue", 14)
    app.setFont(font)
    
    # Aplikowanie stylów
    app.setStyleSheet(STYLESHEET)
    
    # Login Dialog
    login = LoginDialog()
    login.show()
    
    # Wait for login
    app.exec_()
    
    if login.authenticated:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())