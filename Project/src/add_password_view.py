"""Modal dodawania hasła - wyśrodkowana karta na przyciemnionym tle (wg wzorca Vault)."""

import styles
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QPushButton, QFrame,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from widgets.icons import tinted_pixmap
from services.password_generator import generate_strong_password


class AddPasswordModal(QWidget):
    """Nakładka modalna z formularzem nowego wpisu.

    Tworzona na żądanie (przycisk "+ Add"), zamyka się po utworzeniu wpisu,
    kliknięciu Cancel/X lub wciśnięciu Esc.
    """

    password_created = pyqtSignal(dict)
    password_edited = pyqtSignal(str, dict)  # (oryginalna nazwa, nowe dane)

    def __init__(self, parent, entry=None, existing_names=None):
        """Argumenty:
            entry: Edytowany wpis (dict) - None oznacza tryb dodawania.
            existing_names: Nazwy istniejących wpisów (walidacja duplikatów).
        """
        super().__init__(parent)
        self._edit_entry = dict(entry) if entry else None
        self._existing_names = set(existing_names or [])
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        # Przyciemnienie tła (overlay-scrim)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 55%);")
        self.resize(parent.size())
        self.init_ui()
        if self._edit_entry:
            self.website_input.setText(self._edit_entry.get("name", ""))
            self.username_input.setText(self._edit_entry.get("email", ""))
            self.password_input.setText(self._edit_entry.get("password", ""))
            self.notes_input.setPlainText(self._edit_entry.get("notes", ""))

    def init_ui(self):
        """Zbuduj kartę formularza"""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFixedWidth(460)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        card.setObjectName("modalCard")
        card.setStyleSheet(f"""
            QFrame#modalCard {{
                background-color: {styles.CARD_BG};
                border: 1px solid {styles.HAIRLINE_STRONG};
                border-radius: 16px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(16)

        # --- Nagłówek: tytuł + X ---
        head_row = QHBoxLayout()
        title = QLabel("Edit Password" if self._edit_entry else "New Password")
        title.setStyleSheet(
            f"font-size: {styles.font_px(21)}px; font-weight: bold; color: {styles.TEXT_PRIMARY};"
            " background: transparent; border: none;"
        )
        head_row.addWidget(title)
        head_row.addStretch()

        close_btn = QPushButton()
        close_btn.setFixedSize(32, 32)
        close_btn.setIconSize(QSize(16, 16))
        close_btn.setIcon(QIcon(tinted_pixmap("x", styles.TEXT_SECONDARY, 16)))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 8px; }"
            f"QPushButton:hover {{ background-color: {styles.HOVER_BG}; }}"
        )
        close_btn.clicked.connect(self.close)
        head_row.addWidget(close_btn)
        card_layout.addLayout(head_row)

        # --- Pola ---
        self.website_input = self._add_field(card_layout, "WEBSITE", "e.g. github.com", "globe")
        self.username_input = self._add_field(card_layout, "USERNAME", "e.g. you@email.com", "user")

        self.password_input = self._add_field(card_layout, "PASSWORD", "Enter or generate", "key-round")
        self.password_input.setEchoMode(QLineEdit.Password)
        # Akcje w polu: podgląd + generator (jak trailing icons we wzorcu)
        self._eye_action = self.password_input.addAction(
            QIcon(tinted_pixmap("eye", styles.TEXT_SECONDARY, 16)), QLineEdit.TrailingPosition
        )
        self._eye_action.setToolTip("Show / hide password")
        self._eye_action.triggered.connect(self._toggle_reveal)
        gen_action = self.password_input.addAction(
            QIcon(tinted_pixmap("wand-sparkles", styles.COLOR_BLUE, 16)), QLineEdit.TrailingPosition
        )
        gen_action.setToolTip("Generate a strong random password")
        gen_action.triggered.connect(self._on_generate)

        # Notatki
        notes_group = QVBoxLayout()
        notes_group.setSpacing(6)
        notes_lbl = QLabel("NOTES")
        notes_lbl.setStyleSheet(styles.FIELD_LABEL_STYLE)
        notes_group.addWidget(notes_lbl)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
        self.notes_input.setFixedHeight(styles.font_px(76))
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {styles.INPUT_BG};
                color: {styles.TEXT_PRIMARY};
                border-radius: 8px;
                padding: 10px;
                border: 1px solid {styles.HAIRLINE};
                font-size: {styles.font_px(14)}px;
            }}
            QTextEdit:focus {{
                border: 1px solid {styles.COLOR_BLUE};
            }}
        """)
        notes_group.addWidget(self.notes_input)
        card_layout.addLayout(notes_group)

        # Etykieta statusu (walidacja)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            f"color: {styles.COLOR_RED}; font-size: {styles.font_px(13)}px; background: transparent; border: none;"
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.status_label)

        # --- Przyciski: Cancel (ghost) + Create (akcent) ---
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {styles.TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: {styles.font_px(14)}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {styles.HOVER_BG};
                color: {styles.TEXT_PRIMARY};
            }}
        """)
        cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(cancel_btn)

        create_btn = QPushButton("  Save" if self._edit_entry else "  Create")
        create_btn.setIcon(QIcon(tinted_pixmap("check", "#ffffff", 16)))
        create_btn.setIconSize(QSize(16, 16))
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.COLOR_BLUE};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: {styles.font_px(14)}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {styles.COLOR_BLUE_HOVER};
            }}
        """)
        create_btn.clicked.connect(self._on_create)
        btn_row.addWidget(create_btn)

        card_layout.addLayout(btn_row)

        # Karta wyśrodkowana, nigdy nie rozciągana na wysokość okna
        outer.addStretch()
        outer.addWidget(card, 0, Qt.AlignHCenter)
        outer.addStretch()

    def _add_field(self, layout, label_text, placeholder, icon_name) -> QLineEdit:
        """Dodaj etykietę (uppercase) + pole z ikoną wiodącą; zwróć pole."""
        group = QVBoxLayout()
        group.setSpacing(6)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(styles.FIELD_LABEL_STYLE)
        group.addWidget(lbl)

        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        # Wysokość skaluje się z fontem - sztywne 40px ucina descendery (g, y)
        field.setFixedHeight(styles.font_px(40))
        field.addAction(
            QIcon(tinted_pixmap(icon_name, styles.TEXT_TERTIARY, 16)),
            QLineEdit.LeadingPosition,
        )
        field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {styles.INPUT_BG};
                color: {styles.TEXT_PRIMARY};
                border-radius: 8px;
                padding: 8px 10px;
                border: 1px solid {styles.HAIRLINE};
                font-size: {styles.font_px(14)}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {styles.COLOR_BLUE};
            }}
        """)
        group.addWidget(field)
        layout.addLayout(group)
        return field

    # --- Akcje ---
    def _toggle_reveal(self):
        revealed = self.password_input.echoMode() == QLineEdit.Normal
        self.password_input.setEchoMode(QLineEdit.Password if revealed else QLineEdit.Normal)
        icon = "eye" if revealed else "eye-off"
        self._eye_action.setIcon(QIcon(tinted_pixmap(icon, styles.TEXT_SECONDARY, 16)))

    def _on_generate(self):
        """Wypełnij pole hasła nowo wygenerowanym silnym hasłem"""
        self.password_input.setText(generate_strong_password(length=20))
        if self.password_input.echoMode() != QLineEdit.Normal:
            self._toggle_reveal()

    def _on_create(self):
        """Zweryfikuj dane i utwórz nowy wpis hasła."""
        website = self.website_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        notes = self.notes_input.toPlainText().strip()

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

        # Duplikaty nazw: przy edycji własna nazwa wpisu jest dozwolona
        original_name = self._edit_entry.get("name") if self._edit_entry else None
        if website in self._existing_names and website != original_name:
            self.status_label.setText("An entry with this name already exists")
            self.website_input.setFocus()
            return

        if self._edit_entry:
            edited = {
                "name": website,
                "email": username,
                "password": password,
                "notes": notes,
                # Kolor i status ulubionego zostają z oryginału
                "color": self._edit_entry.get("color", "#333333"),
                "weak_password": len(password) < 8,
                "favorite": self._edit_entry.get("favorite", False),
            }
            self.password_edited.emit(original_name, edited)
            self.close()
            return

        # Wyznacz kolor na podstawie nazwy strony
        colors = ["#24292e", "#db4437", "#e50914", "#232f3e", "#1db954",
                  "#0077b5", "#0061ff", "#1da1f2", "#555555", "#003087",
                  "#00a4ef", "#ff0000", "#ff9f0a", "#bf5af2", "#30d158"]
        color = colors[hash(website) % len(colors)]

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
        self.close()

    # --- Zachowanie nakładki ---
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # Kliknięcie w przyciemnione tło (poza kartą) zamyka modal
        if self.childAt(event.pos()) is None:
            self.close()
        super().mousePressEvent(event)

    def showEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
        super().showEvent(event)
        self.website_input.setFocus()
