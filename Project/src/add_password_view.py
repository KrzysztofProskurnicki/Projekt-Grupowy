"""Widok dodawania hasła"""

import styles
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QPushButton, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from styles import *
from services.password_generator import generate_strong_password


class AddPasswordView(QWidget):
    
    password_created = pyqtSignal(dict)
    back_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Zbuduj interfejs formularza dodawania hasła"""
        self.setStyleSheet(f"background-color: {styles.DARK_BG};")
        
        # Główny układ
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        # Pasek nagłówka
        header_widget = QWidget()
        header_widget.setStyleSheet(f"background-color: {styles.DARK_BG}; border-bottom: 1px solid {styles.BORDER_COLOR};")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(24, 16, 24, 16)
        
        # Przycisk powrotu
        back_btn = QPushButton("← Back")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {styles.COLOR_BLUE};
                border: none;
                font-size: 16px;
                font-weight: 600;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                color: #409cff;
            }}
        """)
        back_btn.clicked.connect(self._on_back)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()

        title_label = QLabel("Add New Password")
        title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {styles.TEXT_PRIMARY}; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()

        spacer = QWidget()
        spacer.setFixedWidth(80)
        header_layout.addWidget(spacer)
        
        outer_layout.addWidget(header_widget)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 30, 40, 30)
        form_layout.setSpacing(0)

        form_card = QFrame()
        form_card.setMaximumWidth(600)
        form_card.setStyleSheet(f"""
            background-color: {styles.CARD_BG};
            border-radius: 16px;
            border: 1px solid {styles.BORDER_COLOR};
        """)
        card_layout = QVBoxLayout(form_card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(20)
        
        # --- Pole strony ---
        website_label = QLabel("Website")
        website_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {styles.TEXT_SECONDARY}; background: transparent; border: none;")
        card_layout.addWidget(website_label)
        
        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("e.g. github.com")
        self.website_input.setStyleSheet(self._input_style())
        card_layout.addWidget(self.website_input)
        
        # --- Pole nazwy użytkownika ---
        username_label = QLabel("Username")
        username_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {styles.TEXT_SECONDARY}; background: transparent; border: none;")
        card_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g. john.doe@email.com")
        self.username_input.setStyleSheet(self._input_style())
        card_layout.addWidget(self.username_input)
        
        # --- Pole hasła ---
        password_label = QLabel("Password")
        password_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {styles.TEXT_SECONDARY}; background: transparent; border: none;")
        card_layout.addWidget(password_label)

        # Pole hasła i przycisk generowania w jednym wierszu
        password_row = QHBoxLayout()
        password_row.setSpacing(8)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self._input_style())
        password_row.addWidget(self.password_input)

        generate_btn = QPushButton("Generate")
        generate_btn.setCursor(Qt.PointingHandCursor)
        generate_btn.setToolTip("Generate a strong random password")
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.INPUT_BG};
                color: {styles.COLOR_BLUE};
                border: 1px solid {styles.BORDER_COLOR};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {styles.BORDER_COLOR};
            }}
            QPushButton:pressed {{
                background-color: {styles.CARD_BG};
            }}
        """)
        generate_btn.clicked.connect(self._on_generate)
        password_row.addWidget(generate_btn)

        card_layout.addLayout(password_row)
        
        # --- Pole notatek ---
        notes_label = QLabel("Notes")
        notes_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {styles.TEXT_SECONDARY}; background: transparent; border: none;")
        card_layout.addWidget(notes_label)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
        self.notes_input.setFixedHeight(100)
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {styles.INPUT_BG};
                color: {styles.TEXT_PRIMARY};
                border-radius: 8px;
                padding: 12px;
                border: 1px solid {styles.BORDER_COLOR};
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border: 1px solid {styles.COLOR_BLUE};
            }}
        """)
        card_layout.addWidget(self.notes_input)
        
        # Etykieta statusu
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ff453a; font-size: 14px; background: transparent; border: none;")
        self.status_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.status_label)
        
        card_layout.addSpacing(10)
        
        # --- Wiersz przycisków ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        # Przycisk powrotu
        form_back_btn = QPushButton("Back")
        form_back_btn.setCursor(Qt.PointingHandCursor)
        form_back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.INPUT_BG};
                color: {styles.TEXT_PRIMARY};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {styles.BORDER_COLOR};
            }}
            QPushButton:pressed {{
                background-color: {styles.CARD_BG};
            }}
        """)
        form_back_btn.clicked.connect(self._on_back)
        btn_layout.addWidget(form_back_btn)
        
        # Przycisk tworzenia
        create_btn = QPushButton("Create")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.COLOR_GREEN};
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #28b84c;
            }}
            QPushButton:pressed {{
                background-color: #1f9e3e;
            }}
        """)
        create_btn.clicked.connect(self._on_create)
        btn_layout.addWidget(create_btn)
        
        card_layout.addLayout(btn_layout)

        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(form_card)
        center_layout.addStretch()
        
        form_layout.addLayout(center_layout)
        form_layout.addStretch()
        
        outer_layout.addWidget(form_container)
    
    def _input_style(self) -> str:
        """Zwróć wspólny styl pól wejściowych"""
        return f"""
            QLineEdit {{
                background-color: {styles.INPUT_BG};
                color: {styles.TEXT_PRIMARY};
                border-radius: 8px;
                padding: 12px;
                border: 1px solid {styles.BORDER_COLOR};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {styles.COLOR_BLUE};
            }}
        """
    
    def refresh_theme(self):
        """Przebuduj cały interfejs, aby zastosować najnowsze kolory motywu"""
        for child in self.findChildren(QWidget):
            child.deleteLater()
        # Zainicjalizuj ponownie
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        self.init_ui()
    
    def _on_generate(self):
        """Wypełnij pole hasła nowo wygenerowanym silnym hasłem"""
        self.password_input.setText(generate_strong_password(length=20))
        self.password_input.setEchoMode(QLineEdit.Normal)

    def _on_back(self):
        self._clear_form()
        self.back_clicked.emit()
    
    def _on_create(self):
        """Zweryfikuj dane i utwórz nowy wpis hasła."""
        website = self.website_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        notes = self.notes_input.toPlainText().strip()
        
        # Zweryfikuj wymagane pola
        if not website:
            self.status_label.setText("Website is required")
            self.website_input.setFocus()
            return
        
        if not username:
            self.status_label.setText("Username is required")
            self.username_input.setFocus()
            return
        
        if not password:
            self.status_label.setText("Password is required")
            self.password_input.setFocus()
            return
        
        # Wyznacz kolor na podstawie pierwszej litery
        colors = ["#24292e", "#db4437", "#e50914", "#232f3e", "#1db954",
                  "#0077b5", "#0061ff", "#1da1f2", "#555555", "#003087",
                  "#00a4ef", "#ff0000", "#ff9f0a", "#bf5af2", "#30d158"]
        color = colors[hash(website) % len(colors)]
        
        # Zbuduj wpis hasła
        new_entry = {
            "name": website,
            "email": username,
            "password": password,
            "notes": notes,
            "color": color,
            "weak_password": len(password) < 8,
            "favorite": False
        }
        
        self.password_created.emit(new_entry)
        self._clear_form()
    
    def _clear_form(self):
        self.website_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.notes_input.clear()
        self.status_label.clear()
