import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from Project.baza_v1 import db_manager
from Project.baza_v1.generator import generate_strong_password
from detail_view import DetailView
from login_dialog import LoginDialog
from security_dashboard import SecurityView
from sidebar import Sidebar
from styles import *


class PasswordEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New password")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {DARK_BG}; color: {TEXT_PRIMARY}; }}
            QLabel {{ color: {TEXT_PRIMARY}; }}
            QLineEdit, QTextEdit {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid #48484a;
                border-radius: 6px;
                padding: 8px;
            }}
            QPushButton {{
                background-color: #3a3a3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{ background-color: #48484a; }}
            QPushButton#primary {{ background-color: {COLOR_BLUE}; }}
        """)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.title_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.url_input = QLineEdit()
        self.notes_input = QTextEdit()
        self.notes_input.setFixedHeight(80)

        password_row = QHBoxLayout()
        password_row.addWidget(self.password_input)
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self.generate_password)
        password_row.addWidget(generate_btn)

        form.addRow("Service", self.title_input)
        form.addRow("Login", self.username_input)
        form.addRow("Password", password_row)
        form.addRow("Website", self.url_input)
        form.addRow("Notes", self.notes_input)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

    def generate_password(self):
        self.password_input.setText(generate_strong_password())

    def accept(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Missing service", "Enter service name.")
            return
        if not self.password_input.text():
            QMessageBox.warning(self, "Missing password", "Enter or generate password.")
            return
        super().accept()

    def data(self):
        return {
            "title": self.title_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "url": self.url_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip(),
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Manager")
        self.resize(1100, 700)
        self.setMinimumSize(1100, 700)
        self.passwords_data = []
        self.current_filter = "all"

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = Sidebar()
        self.sidebar.nav_clicked.connect(self.handle_nav_click)

        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        self.page_list = self.create_list_page()
        self.stacked_widget.addWidget(self.page_list)

        self.page_detail = DetailView(
            self.show_list,
            self.toggle_favorite,
            db_manager.login,
        )
        self.stacked_widget.addWidget(self.page_detail)

        self.page_security = SecurityView(self.show_list, self.navigate_to_detail)
        self.stacked_widget.addWidget(self.page_security)

        self.page_vault = QLabel("Vault jest przechowywana w Project/data/sejfy.db")
        self.page_vault.setAlignment(Qt.AlignCenter)
        self.page_vault.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 20px;")
        self.stacked_widget.addWidget(self.page_vault)

        self.page_settings = QLabel("Settings View (Coming Soon)")
        self.page_settings.setAlignment(Qt.AlignCenter)
        self.page_settings.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 20px;")
        self.stacked_widget.addWidget(self.page_settings)

        self.page_profile = QLabel("Profile View (Coming Soon)")
        self.page_profile.setAlignment(Qt.AlignCenter)
        self.page_profile.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 20px;")
        self.stacked_widget.addWidget(self.page_profile)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_area)

        self.reload_data()
        self.refresh_list()
        self.update_badges()

    def create_list_page(self):
        page = QWidget()
        list_layout = QVBoxLayout(page)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setStyleSheet(f"background-color: {DARK_BG}; border-bottom: 1px solid #38383a;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 20, 20, 20)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search passwords...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_list)
        header_layout.addWidget(self.search_input)
        header_layout.addStretch()

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

        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.itemClicked.connect(self.open_detail_view)
        list_layout.addWidget(self.list_widget)
        return page

    def reload_data(self):
        self.passwords_data = db_manager.get_all_passwords()

    def entry_by_id(self, entry_id):
        return next((entry for entry in self.passwords_data if entry["id"] == entry_id), None)

    def update_badges(self):
        total = len(self.passwords_data)
        favorites = sum(1 for p in self.passwords_data if p.get("favorite", False))
        security_issues = sum(1 for p in self.passwords_data if p.get("weak_password", False))

        self.sidebar.update_badge(0, total)
        self.sidebar.update_badge(1, favorites)
        self.sidebar.update_badge(2, security_issues)

    def refresh_list(self):
        self.list_widget.clear()
        for entry in self.passwords_data:
            if self.current_filter == "favorites" and not entry.get("favorite", False):
                continue
            if self.current_filter == "security" and not entry.get("weak_password", False):
                continue
            self.add_list_item(entry)
        self.filter_list(self.search_input.text())

    def filter_list(self, text):
        text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            entry_id = item.data(Qt.UserRole)
            entry = self.entry_by_id(entry_id)
            if entry:
                title = entry["name"].lower()
                subtitle = entry["email"].lower()
                item.setHidden(text not in title and text not in subtitle)

    def add_list_item(self, entry):
        item = QListWidgetItem()

        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 5, 0, 5)
        container_layout.setSpacing(0)

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

        hbox = QHBoxLayout(card_frame)
        hbox.setContentsMargins(15, 10, 15, 10)
        hbox.setSpacing(15)

        icon_lbl = QLabel(entry["letter"])
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background-color: {entry["color"]};
            color: white;
            border-radius: 24px;
            font-weight: bold;
            font-size: 22px;
            border: none;
        """)
        hbox.addWidget(icon_lbl)

        text_container = QWidget()
        vbox = QVBoxLayout(text_container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.setAlignment(Qt.AlignVCenter)

        title_lbl = QLabel(entry["name"])
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {TEXT_PRIMARY}; border: none; background: transparent;")
        subtitle_lbl = QLabel(entry["email"])
        subtitle_lbl.setStyleSheet(f"font-size: 14px; color: {TEXT_SECONDARY}; border: none; background: transparent;")

        vbox.addWidget(title_lbl)
        vbox.addWidget(subtitle_lbl)
        hbox.addWidget(text_container)
        hbox.addStretch()

        if entry.get("favorite"):
            fav_lbl = QLabel("Star")
            fav_lbl.setStyleSheet("font-size: 12px; color: #ffd60a; background: transparent; border: none;")
            hbox.addWidget(fav_lbl)

        chevron = QLabel(">")
        chevron.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 24px; font-weight: bold; background: transparent; border: none;")
        hbox.addWidget(chevron)

        container_layout.addWidget(card_frame)
        item.setSizeHint(container_widget.sizeHint())
        item.setData(Qt.UserRole, entry["id"])
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, container_widget)

    def open_detail_view(self, item):
        self.navigate_to_detail(item.data(Qt.UserRole))

    def navigate_to_detail(self, entry_id):
        entry = self.entry_by_id(entry_id)
        if not entry:
            return
        self.page_detail.update_data(entry)
        self.stacked_widget.setCurrentIndex(1)

    def show_list(self):
        self.reload_data()
        self.refresh_list()
        self.update_badges()
        self.stacked_widget.setCurrentIndex(0)

    def handle_nav_click(self, index):
        self.reload_data()
        if index == 0:
            self.current_filter = "all"
            self.refresh_list()
            self.stacked_widget.setCurrentIndex(0)
        elif index == 1:
            self.current_filter = "favorites"
            self.refresh_list()
            self.stacked_widget.setCurrentIndex(0)
        elif index == 2:
            self.current_filter = "security"
            self.page_security.update_stats(self.passwords_data)
            self.stacked_widget.setCurrentIndex(2)
        elif index == 3:
            self.stacked_widget.setCurrentIndex(3)
        elif index == 4:
            self.stacked_widget.setCurrentIndex(4)
        elif index == 5:
            self.stacked_widget.setCurrentIndex(5)
        self.update_badges()

    def toggle_favorite(self, entry_id, is_favorite):
        db_manager.update_favorite(entry_id, is_favorite)
        self.reload_data()
        self.refresh_list()
        self.update_badges()

    def add_new_item(self):
        dialog = PasswordEntryDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        data = dialog.data()
        try:
            db_manager.add_password(
                data["title"],
                data["username"],
                data["password"],
                data["url"],
                data["notes"],
            )
        except Exception as exc:
            QMessageBox.critical(self, "Save failed", str(exc))
            return

        self.reload_data()
        self.refresh_list()
        self.update_badges()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 14) if sys.platform == "win32" else QFont("Helvetica Neue", 14)
    app.setFont(font)
    app.setStyleSheet(STYLESHEET)

    login = LoginDialog()
    if login.exec_() == QDialog.Accepted and login.authenticated:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
