"""Panel szczegółów wpisu - prawa kolumna widoku listy (wg wzorca Vault).

Zamiast osobnej strony w QStackedWidget jest osadzony obok listy haseł.
Pokazuje pusty stan, dopóki użytkownik nie wybierze wpisu.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTextEdit, QStackedLayout,
                             QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QGuiApplication, QIcon, QFont
from widgets.notification_popup import NotificationPopup
from widgets.master_password_overlay import MasterPasswordOverlay
from widgets.icons import tinted_pixmap, icon_label
from services.authentication_service import AuthenticationService
import styles
from constants import MSG_COPIED

# Maska hasła jak we wzorcu DetailField: 12 kropek z lekkim odstępem liter
PASSWORD_MASK = "•" * 12


class DetailView(QWidget):

    def __init__(self, switch_back_callback=None, favorite_callback=None,
                 edit_callback=None, delete_callback=None):
        """Inicjalizuj panel szczegółów.

        Argumenty:
            switch_back_callback: Zachowane dla kompatybilności (panel nie ma
                przycisku powrotu - nawigacja przez sidebar).
            favorite_callback: Funkcja przełączająca status ulubionego wpisu.
            edit_callback: Funkcja otwierająca edycję bieżącego wpisu (dict).
            delete_callback: Funkcja usuwająca bieżący wpis (nazwa).
        """
        super().__init__()
        self.switch_back_callback = switch_back_callback
        self.favorite_callback = favorite_callback
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        self.current_name = ""
        self._last_entry = None

        # Zmienne stanu
        self.is_favorite = False
        self.strength_level = "strong"
        self.password_visible = False
        self.auth_service = AuthenticationService()
        self.actual_password = ""
        self.is_weak = False

        self.stack = QStackedLayout(self)
        self.stack.setContentsMargins(0, 0, 0, 0)

        self._build_ui()

    # --- Budowanie UI ---
    def _build_ui(self):
        self.setStyleSheet(f"background-color: {styles.DARK_BG};")

        # --- Strona 0: pusty stan ---
        empty_page = QWidget()
        empty_page.setStyleSheet(f"background-color: {styles.DARK_BG};")
        empty_layout = QVBoxLayout(empty_page)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(14)

        empty_icon_tile = QLabel()
        empty_icon_tile.setFixedSize(64, 64)
        empty_icon_tile.setAlignment(Qt.AlignCenter)
        empty_icon_tile.setPixmap(tinted_pixmap("key-round", styles.TEXT_TERTIARY, 28))
        empty_icon_tile.setStyleSheet(
            f"background-color: {styles.CARD_BG}; border: 1px solid {styles.HAIRLINE};"
            " border-radius: 12px;"
        )
        empty_layout.addWidget(empty_icon_tile, 0, Qt.AlignHCenter)

        empty_lbl = QLabel("Select an entry to view its details")
        empty_lbl.setStyleSheet(
            f"font-size: {styles.font_px(15)}px; color: {styles.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        empty_layout.addWidget(empty_lbl, 0, Qt.AlignHCenter)

        self.stack.addWidget(empty_page)

        # --- Strona 1: treść wpisu ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background-color: {styles.DARK_BG}; }}"
            " QScrollBar:vertical { width: 0px; }"
        )
        content = QWidget()
        content.setStyleSheet(f"background-color: {styles.DARK_BG};")
        self.main_layout = QVBoxLayout(content)
        self.main_layout.setContentsMargins(32, 28, 32, 28)
        self.main_layout.setSpacing(12)

        # --- Nagłówek: awatar + tytuł/login/badge + gwiazdka ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        self.icon_label = QLabel("G")
        self.icon_label.setFixedSize(56, 56)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            background-color: {styles.CARD_BG};
            color: white;
            border-radius: 14px;
            font-size: {styles.font_px(26)}px;
            font-weight: bold;
            border: none;
        """)

        title_box = QVBoxLayout()
        title_box.setSpacing(8)
        self.title_label = QLabel("")
        self.title_label.setStyleSheet(
            f"font-size: {styles.font_px(28)}px; font-weight: bold; color: {styles.TEXT_PRIMARY};"
            " background: transparent; border: none;"
        )

        sub_row = QHBoxLayout()
        sub_row.setSpacing(10)
        self.link_label = QLabel("")
        self.link_label.setStyleSheet(
            f"font-size: {styles.font_px(13)}px; color: {styles.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        self.strength_badge = QLabel("")
        self.strength_badge.setFixedHeight(styles.font_px(22))
        sub_row.addWidget(self.link_label)
        sub_row.addWidget(self.strength_badge)
        sub_row.addStretch()

        title_box.addWidget(self.title_label)
        title_box.addLayout(sub_row)

        # Gwiazdka (ulubione) - mały ikonowy przycisk bez ramki (jak IconButton)
        self.star_btn = QPushButton()
        self.star_btn.setFixedSize(36, 36)
        self.star_btn.setIconSize(QSize(18, 18))
        self.star_btn.setCursor(Qt.PointingHandCursor)
        self.update_star_style()
        self.star_btn.clicked.connect(self.toggle_favorite)

        # Edycja wpisu - przycisk wtórny z piórem (na prawo od gwiazdki)
        self.edit_btn = QPushButton("  Edit")
        self.edit_btn.setIcon(QIcon(tinted_pixmap("pencil", styles.TEXT_PRIMARY, 16)))
        self.edit_btn.setIconSize(QSize(16, 16))
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.setFixedHeight(styles.font_px(36))
        self.edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.RAISED_BG};
                color: {styles.TEXT_PRIMARY};
                border: 1px solid {styles.HAIRLINE_STRONG};
                border-radius: 8px;
                padding: 0px 14px;
                font-size: {styles.font_px(13)}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {styles.HOVER_BG};
            }}
        """)
        self.edit_btn.clicked.connect(self._on_edit_clicked)

        # Usuwanie wpisu - czerwony przycisk wtórny z koszem (obok Edit)
        self.remove_btn = QPushButton("  Remove")
        self.remove_btn.setIcon(QIcon(tinted_pixmap("trash-2", styles.COLOR_RED, 16)))
        self.remove_btn.setIconSize(QSize(16, 16))
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.setFixedHeight(styles.font_px(36))
        self.remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.RAISED_BG};
                color: {styles.COLOR_RED};
                border: 1px solid {styles.HAIRLINE_STRONG};
                border-radius: 8px;
                padding: 0px 14px;
                font-size: {styles.font_px(13)}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {styles.RED_SOFT};
                border: 1px solid {styles.COLOR_RED};
            }}
        """)
        self.remove_btn.clicked.connect(self._on_remove_clicked)

        header_layout.addWidget(self.icon_label, 0, Qt.AlignTop)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(self.star_btn, 0, Qt.AlignTop)
        header_layout.addWidget(self.edit_btn, 0, Qt.AlignTop)
        header_layout.addWidget(self.remove_btn, 0, Qt.AlignTop)

        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(16)

        # --- Pola: nazwa użytkownika, hasło, strona, notatki ---
        self.create_field("USERNAME", "", icon="user", is_copyable=True)
        self.create_field("PASSWORD", "", icon="key-round", is_copyable=True, is_password=True)
        self.create_field("WEBSITE", "", icon="globe", is_copyable=True, is_link=True)
        self.create_field("NOTES", "", icon="sticky-note", is_multiline=True)

        self.main_layout.addStretch()
        scroll.setWidget(content)
        self.stack.addWidget(scroll)

        self.stack.setCurrentIndex(0)

    # --- Motyw ---
    def refresh_theme(self):
        """Przebuduj UI z bieżącymi kolorami motywu, zachowując stan."""
        saved_name = self.current_name
        saved_favorite = self.is_favorite
        saved_password = self.actual_password
        saved_weak = self.is_weak
        saved_entry = getattr(self, "_last_entry", None)

        # Usuń obie strony stosu
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()

        self._build_ui()

        self.current_name = saved_name
        self.is_favorite = saved_favorite
        self.actual_password = saved_password
        self.is_weak = saved_weak
        if saved_entry is not None:
            self.update_data(saved_entry)

    # --- Pola ---
    def create_field(self, label_text, value_text, icon=None, is_copyable=False,
                     is_password=False, is_multiline=False, is_link=False):
        container = QFrame()
        container.setObjectName("fieldCard")
        container.setStyleSheet(f"""
            QFrame#fieldCard {{
                background-color: {styles.CARD_BG};
                border: 1px solid {styles.HAIRLINE};
                border-radius: 12px;
            }}
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 14, 14, 14)
        layout.setSpacing(14)

        # Chip z ikoną pola
        if icon:
            chip = QLabel()
            chip.setFixedSize(36, 36)
            chip.setAlignment(Qt.AlignCenter)
            chip.setPixmap(tinted_pixmap(icon, styles.TEXT_SECONDARY, 18))
            chip.setStyleSheet(
                f"background-color: {styles.RAISED_BG}; border-radius: 8px; border: none;"
            )
            layout.addWidget(chip, 0, Qt.AlignTop if is_multiline else Qt.AlignVCenter)

        # Kolumna: etykieta + wartość
        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(styles.FIELD_LABEL_STYLE)
        text_col.addWidget(lbl)

        if is_multiline:
            value_widget = QTextEdit()
            value_widget.setPlainText(value_text)
            value_widget.setReadOnly(True)
            value_widget.setStyleSheet(f"""
                QTextEdit {{
                    color: {styles.TEXT_PRIMARY};
                    font-size: {styles.font_px(15)}px;
                    border: none;
                    background: transparent;
                }}
            """)
            # Pionowa polityka Fixed - domyślne Expanding QTextEdit propaguje
            # się przez layout karty i rozciąga całe pole na wolną przestrzeń
            value_widget.setFixedHeight(styles.font_px(72))
            value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.notes_edit = value_widget
        else:
            value_widget = QLabel(value_text)
            color = styles.COLOR_BLUE if is_link else styles.TEXT_PRIMARY
            value_widget.setStyleSheet(
                f"color: {color}; font-size: {styles.font_px(15)}px; border: none; background: transparent;"
            )

            if label_text == "USERNAME": self.username_lbl = value_widget
            elif label_text == "PASSWORD": self.password_lbl = value_widget
            elif label_text == "WEBSITE":  self.website_lbl = value_widget

        text_col.addWidget(value_widget)
        layout.addLayout(text_col, 1)

        # Akcje (kopiowanie, podgląd)
        if is_password:
            self.eye_btn = QPushButton()
            self.eye_btn.setFixedSize(34, 34)
            self.eye_btn.setIconSize(QSize(18, 18))
            self.eye_btn.setCursor(Qt.PointingHandCursor)
            self.eye_btn.setIcon(QIcon(tinted_pixmap("eye", styles.TEXT_SECONDARY, 18)))
            self.eye_btn.setStyleSheet(self._field_btn_style())
            self.eye_btn.clicked.connect(self.toggle_password_visibility)
            layout.addWidget(self.eye_btn)

            copy_pwd_btn = QPushButton()
            copy_pwd_btn.setFixedSize(34, 34)
            copy_pwd_btn.setIconSize(QSize(18, 18))
            copy_pwd_btn.setCursor(Qt.PointingHandCursor)
            copy_pwd_btn.setIcon(QIcon(tinted_pixmap("copy", styles.COLOR_BLUE, 18)))
            copy_pwd_btn.setStyleSheet(self._field_btn_style())
            copy_pwd_btn.clicked.connect(lambda: self.copy_with_notification(self.actual_password, "PASSWORD"))
            layout.addWidget(copy_pwd_btn)

        if is_copyable and not is_multiline and not is_password:
            copy_btn = QPushButton()
            copy_btn.setFixedSize(34, 34)
            copy_btn.setIconSize(QSize(18, 18))
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.setIcon(QIcon(tinted_pixmap("copy", styles.COLOR_BLUE, 18)))
            copy_btn.setStyleSheet(self._field_btn_style())
            copy_btn.clicked.connect(lambda checked, w=value_widget, l=label_text: self.copy_with_notification(w.text(), l))
            layout.addWidget(copy_btn)

        self.main_layout.addWidget(container)

    def request_master_password(self, on_success):
        if self.auth_service.is_authenticated():
            on_success()
            return

        def auth_success_wrapper():
            self.auth_service.set_authenticated(True)
            on_success()

        overlay = MasterPasswordOverlay(self, auth_success_wrapper, self.auth_service)
        overlay.show()

    def toggle_password_visibility_with_auth(self):
        """Przełącz widoczne hasła po weryfikacji hasła głównego (master password)"""
        if not self.password_visible:
            self.request_master_password(self._show_password)
        else:
            self.password_visible = False
            self.password_lbl.setText("•••••••••••••")
            self._set_eye_icon()

    def _show_password(self):
        self.password_visible = True
        self.password_lbl.setText(self.actual_password)
        self._set_eye_icon()

    def copy_password_with_auth(self):
        self.request_master_password(self._copy_password_action)

    def _copy_password_action(self):
        QGuiApplication.clipboard().setText(self.actual_password)
        self.show_notification(MSG_COPIED)

    def copy_with_notification(self, text, field_name):
        """Skopiuj tekst i pokaż powiadomienie

        Argumenty:
            text: Tekst do skopiowania do schowka
            field_name: Nazwa kopiowanego pola
        """
        QGuiApplication.clipboard().setText(text)
        self.show_notification(MSG_COPIED)

    def show_notification(self, message):
        popup = NotificationPopup(message, self)
        popup.show()

    def _on_edit_clicked(self):
        """Otwórz modal edycji bieżącego wpisu."""
        if self.edit_callback and self._last_entry:
            self.edit_callback(dict(self._last_entry))

    def _on_remove_clicked(self):
        """Usuń bieżący wpis (potwierdzenie po stronie głównego okna)."""
        if self.delete_callback and self.current_name:
            self.delete_callback(self.current_name)

    def toggle_favorite(self):
        self.is_favorite = not self.is_favorite
        self.update_star_style()

        if self.favorite_callback and self.current_name:
            self.favorite_callback(self.current_name, self.is_favorite)

    def update_star_style(self):
        if self.is_favorite:
            self.star_btn.setIcon(QIcon(tinted_pixmap("star-filled", styles.COLOR_YELLOW, 18)))
            self.star_btn.setToolTip("Remove from favorites")
        else:
            self.star_btn.setIcon(QIcon(tinted_pixmap("star", styles.TEXT_SECONDARY, 18)))
            self.star_btn.setToolTip("Add to favorites")
        self.star_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 8px; }"
            f"QPushButton:hover {{ background-color: {styles.OVERLAY_HOVER}; }}"
        )

    def _update_strength_badge(self):
        """Pokaż pigułkę Strong/Medium/Weak obok loginu (jak Badge we wzorcu)."""
        levels = {
            "strong": ("Strong", styles.COLOR_GREEN, styles.GREEN_SOFT),
            "medium": ("Medium", styles.COLOR_YELLOW, styles.YELLOW_SOFT),
            "weak": ("Weak", styles.COLOR_RED, styles.RED_SOFT),
        }
        text, fg, bg = levels.get(self.strength_level, levels["weak"])
        self.strength_badge.setText(text)
        self.strength_badge.setFixedHeight(styles.font_px(20))
        self.strength_badge.setStyleSheet(
            f"color: {fg}; background-color: {bg}; border: none; border-radius: 10px;"
            f" font-size: {styles.font_px(11)}px; font-weight: 600; padding: 0px 8px;"
        )

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_lbl.setText(self.actual_password)
        else:
            self.password_lbl.setText("•••••••••••••")
        self._set_eye_icon()

    def _set_eye_icon(self):
        """Ustaw ikonę oczka zależnie od widoczności hasła."""
        name = "eye-off" if self.password_visible else "eye"
        self.eye_btn.setIcon(QIcon(tinted_pixmap(name, styles.TEXT_SECONDARY, 18)))

    @staticmethod
    def _field_btn_style() -> str:
        """Styl ikonowych przycisków akcji w polach (kopiuj/podgląd)."""
        return (
            "QPushButton { border: none; background: transparent; border-radius: 8px; }"
            f"QPushButton:hover {{ background-color: {styles.HOVER_BG}; }}"
        )

    def show_empty(self):
        """Pokaż pusty stan (brak wybranego wpisu)."""
        self.current_name = ""
        self._last_entry = None
        self.stack.setCurrentIndex(0)

    def update_data(self, entry: dict):
        name = entry.get("name", "")
        email = entry.get("email", "")
        color = entry.get("color", styles.CARD_BG)
        favorite = bool(entry.get("favorite", False))
        notes = entry.get("notes", "")
        password = entry.get("password", "")
        letter = name[0].upper() if name else "?"

        self._last_entry = dict(entry)
        self.current_name = name
        self.is_favorite = favorite
        self.actual_password = password
        self.is_weak = bool(entry.get("weak_password", False))
        self.strength_level = entry.get(
            "strength", "weak" if self.is_weak else "strong"
        )
        self.update_star_style()
        self._update_strength_badge()
        score = entry.get("pw_score")
        if score is not None:
            tip = f"Password score: {score}/100"
            if entry.get("dictionary"):
                tip += " (dictionary-based)"
            self.strength_badge.setToolTip(tip)

        self.title_label.setText(name)
        self.icon_label.setText(letter)
        self.icon_label.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 14px;
            font-size: {styles.font_px(26)}px;
            font-weight: bold;
            border: none;
        """)

        self.link_label.setText(email)
        self.username_lbl.setText(email)
        self.website_lbl.setText(name)
        self.notes_edit.setPlainText(notes)

        # Ukryj hasło do czasu ponownego uwierzytelnienia użytkownika.
        self.password_visible = False
        self.password_lbl.setText("•••••••••••••" if password else "")
        self._set_eye_icon()

        self.stack.setCurrentIndex(1)
