from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QClipboard, QGuiApplication

class DetailView(QWidget):
    def __init__(self, switch_back_callback):
        super().__init__()
        self.switch_back_callback = switch_back_callback
        
        # Główny layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)
        
        # --- TOP LAYER: Nawigacja (Back button) ---
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("< All Passwords")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0a84ff;
                font-size: 16px;
                border: none;
                text-align: left;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #409cff;
            }
        """)
        self.back_btn.clicked.connect(self.switch_back_callback)
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        
        self.main_layout.addLayout(top_bar)
        
        # --- HEADER LAYER: Ikona + Tytuł + Gwiazdka ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        # Ikona główna
        self.icon_label = QLabel("G")
        self.icon_label.setFixedSize(80, 80)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            background-color: #333;
            color: #f5f5f7;
            border-radius: 20px;
            font-size: 40px;
            font-weight: bold;
        """)
        
        # Tytuł i Link (Pionowo)
        title_box = QVBoxLayout()
        title_box.setSpacing(5)
        self.title_label = QLabel("GitHub")
        self.title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #f5f5f7;")
        self.link_label = QLabel("https://github.com")
        self.link_label.setStyleSheet("font-size: 16px; color: #0a84ff;")
        self.link_label.setCursor(Qt.PointingHandCursor)
        # Opcjonalnie: link_label.mousePressEvent...
        
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.link_label)
        
        # Gwiazdka (Ulubione)
        self.star_btn = QPushButton("★")
        self.star_btn.setFixedSize(40, 40)
        self.star_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffd60a; 
                font-size: 24px;
                border: none;
            }
        """)
        
        header_layout.addWidget(self.icon_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(self.star_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # --- FIELDS LAYER ---
        # Pola: Username, Password, Website, Notes
        self.create_field("USERNAME", "john.doe@email.com", is_copyable=True)
        self.create_field("PASSWORD", "•••••••••••••", is_copyable=True, is_password=True)
        self.create_field("WEBSITE", "https://github.com", is_copyable=True)
        self.create_field("NOTES", "Main development account", is_multiline=True)
        
        self.main_layout.addStretch()

    def create_field(self, label_text, value_text, is_copyable=False, is_password=False, is_multiline=False):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2c2c2e;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Label
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #98989d; font-size: 12px; font-weight: 600; letter-spacing: 0.5px;")
        layout.addWidget(lbl)
        
        # Value Row
        row = QHBoxLayout()
        
        value_lbl = QLabel(value_text)
        value_lbl.setStyleSheet("color: #f5f5f7; font-size: 18px; border: none; background: transparent;")
        if is_multiline:
            value_lbl.setWordWrap(True)
        
        # Jeśli chcemy identyfikować pola do późniejszej aktualizacji
        # Możemy przypisać je do self, np. słownik self.fields[label_text] = value_lbl
        # Tutaj upraszczamy, przypisując do atrybutów bazując na labelu (quick & dirty dla demo)
        if label_text == "USERNAME": self.username_lbl = value_lbl
        elif label_text == "PASSWORD": self.password_lbl = value_lbl
        elif label_text == "WEBSITE":  self.website_lbl = value_lbl
        elif label_text == "NOTES":    self.notes_lbl = value_lbl
        
        row.addWidget(value_lbl)
        row.addStretch()
        
        # Akcje (Copy, Eye)
        if is_password:
            eye_btn = QPushButton("👁")
            eye_btn.setFixedSize(30, 30)
            eye_btn.setCursor(Qt.PointingHandCursor)
            eye_btn.setStyleSheet("color: #0a84ff; border: none; font-size: 16px; background: transparent;")
            row.addWidget(eye_btn)
        
        if is_copyable:
            copy_btn = QPushButton("❐")
            copy_btn.setFixedSize(30, 30)
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.setStyleSheet("color: #0a84ff; border: none; font-size: 16px; background: transparent;")
            copy_btn.clicked.connect(lambda: QGuiApplication.clipboard().setText(value_lbl.text()))
            row.addWidget(copy_btn)
            
        layout.addLayout(row)
        self.main_layout.addWidget(container)

    def update_data(self, title, subtitle, color, letter):
        self.title_label.setText(title)
        self.icon_label.setText(letter)
        self.icon_label.setStyleSheet(f"""
            background-color: {color};
            color: #f5f5f7;
            border-radius: 20px;
            font-size: 40px;
            font-weight: bold;
        """)
        
        # Symulacja danych szczegółowych
        self.username_lbl.setText(subtitle)
        self.link_label.setText(f"https://{title.lower()}.com")
        self.website_lbl.setText(f"https://{title.lower()}.com")
        
