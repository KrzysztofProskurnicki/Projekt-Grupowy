"""Widok profilu - zarządzanie profilem użytkownika, eksportem, zmiany hasła i usuwaniem konta"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QScrollArea, QFileDialog, QProgressBar,
    QMessageBox, QApplication,
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
import styles
from widgets.icons import section_header, icon_label
from constants import (
    MSG_PASSWORD_CHANGED, MSG_EXPORT_SUCCESS,
    MSG_WRONG_CURRENT_PASSWORD, MSG_NEW_PASSWORDS_NOT_MATCH,
    MSG_FILL_ALL_FIELDS,
)
from services.authentication_service import AuthenticationService
from widgets.notification_popup import NotificationPopup


class ChangePasswordWorker(QThread):
    """Wątek tła do przeszyfrowania sejfu podczas zmiany hasła"""
    progress = pyqtSignal(int)
    finished_ok = pyqtSignal()
    finished_err = pyqtSignal(str)

    def __init__(self, auth_service, old_pw, new_pw):
        super().__init__()
        self._auth = auth_service
        self._old = old_pw
        self._new = new_pw

    def run(self):
        try:
            ok = self._auth.change_master_password(
                self._old, self._new,
                progress_callback=lambda pct: self.progress.emit(pct),
            )
            if ok:
                self.finished_ok.emit()
            else:
                self.finished_err.emit(MSG_WRONG_CURRENT_PASSWORD)
        except Exception as e:
            self.finished_err.emit(str(e))


class ProfileView(QWidget):
    """Widok zarządzania profilem."""

    account_deleted = pyqtSignal()

    def __init__(self, username: str, password_service):
        super().__init__()
        self._username = username
        self._password_service = password_service
        self._auth_service = AuthenticationService()
        self._worker = None
        self._build_ui()

    def refresh_theme(self):
        """Przebuduj UI z bieżącymi kolorami motywu"""
        # Zapisz stan pól hasła
        old_cur = self.current_pw.text() if hasattr(self, 'current_pw') else ""
        old_new = self.new_pw.text() if hasattr(self, 'new_pw') else ""
        old_conf = self.confirm_pw.text() if hasattr(self, 'confirm_pw') else ""

        # Usuń wszystko
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        self._build_ui()

        # Przywróć
        self.current_pw.setText(old_cur)
        self.new_pw.setText(old_new)
        self.confirm_pw.setText(old_conf)

    # --- UI --
    def _build_ui(self):
        self.setStyleSheet(f"background-color: {styles.DARK_BG};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background-color: {styles.DARK_BG}; }}"
            f" QScrollBar:vertical {{ width: 0px; }}"
        )

        content = QWidget()
        content.setStyleSheet(f"background-color: {styles.DARK_BG};")
        self.layout_main = QVBoxLayout(content)
        self.layout_main.setContentsMargins(40, 40, 40, 40)
        self.layout_main.setSpacing(30)

        # Tytuł strony
        title = section_header(
            "user", "Profile",
            styles.COLOR_BLUE, styles.TEXT_PRIMARY, icon_size=26, font_px=28,
        )
        self.layout_main.addWidget(title)

        self._build_account_info()
        self._build_export_section()
        self._build_change_password()
        self._build_delete_account()

        self.layout_main.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # --- 1. Karta informacji o koncie --
    def _build_account_info(self):
        card = self._card_frame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        top = QHBoxLayout()
        top.setSpacing(20)

        letter = self._username[0].upper() if self._username else "?"
        avatar = QLabel(letter)
        avatar.setFixedSize(64, 64)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {styles.COLOR_BLUE};
            color: white;
            border-radius: 32px;
            font-size: {styles.font_px(28)}px;
            font-weight: bold;
            border: none;
        """)
        top.addWidget(avatar)

        info_box = QVBoxLayout()
        info_box.setSpacing(4)

        name_lbl = QLabel(self._username)
        name_lbl.setStyleSheet(
            f"font-size: {styles.font_px(21)}px; font-weight: bold; color: {styles.TEXT_PRIMARY};"
            " background: transparent; border: none;"
        )
        info_box.addWidget(name_lbl)

        created = self._auth_service.get_user_created_at()
        since_text = created.strftime("%B %d, %Y") if created else "Unknown"
        since_lbl = QLabel(f"Member since {since_text}")
        since_lbl.setStyleSheet(
            f"font-size: {styles.font_px(14)}px; color: {styles.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        info_box.addWidget(since_lbl)
        top.addLayout(info_box)
        top.addStretch()
        layout.addLayout(top)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {styles.HAIRLINE}; border: none;")
        layout.addWidget(divider)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(0)

        all_passwords = self._password_service.get_all_passwords()
        total = len(all_passwords)
        favs = sum(1 for p in all_passwords if p.get("favorite"))
        levels = [
            p.get("strength") if p.get("strength") in ("weak", "medium", "strong")
            else ("weak" if p.get("weak_password") else "strong")
            for p in all_passwords
        ]
        weak = levels.count("weak")
        medium = levels.count("medium")
        strong = levels.count("strong")

        self._add_stat(stats_row, "key-round", "Total", str(total), styles.COLOR_BLUE)
        self._add_stat(stats_row, "star", "Favorites", str(favs), styles.COLOR_YELLOW)
        self._add_stat(stats_row, "circle-check", "Strong", str(strong), styles.COLOR_GREEN)
        self._add_stat(stats_row, "shield-half", "Medium", str(medium), styles.COLOR_YELLOW)
        self._add_stat(stats_row, "triangle-alert", "Weak", str(weak), styles.COLOR_RED)

        layout.addLayout(stats_row)
        self.layout_main.addWidget(card)

    def _add_stat(self, parent_layout, icon, label, value, color):
        box = QVBoxLayout()
        box.setAlignment(Qt.AlignCenter)
        val_row = QHBoxLayout()
        val_row.setAlignment(Qt.AlignCenter)
        val_row.setSpacing(6)
        ico = icon_label(icon, color, 17)
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(
            f"font-size: {styles.font_px(22)}px; font-weight: bold; color: {styles.TEXT_PRIMARY};"
            " background: transparent; border: none;"
        )
        val_row.addWidget(ico)
        val_row.addWidget(val_lbl)
        box.addLayout(val_row)

        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"font-size: {styles.font_px(13)}px; color: {styles.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        box.addWidget(lbl)
        parent_layout.addLayout(box)

    # --- 2. Eksport sejfu --
    def _build_export_section(self):
        card = self._card_frame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        head = section_header(
            "download", "Export Vault",
            styles.TEXT_SECONDARY, styles.TEXT_PRIMARY, icon_size=18, font_px=17,
        )
        layout.addWidget(head)

        desc = QLabel(
            "Export all your saved passwords to a CSV file.\n"
            "The exported file will contain unencrypted data - store it safely."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(
            f"font-size: {styles.font_px(14)}px; color: {styles.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        layout.addWidget(desc)

        btn_row = QHBoxLayout()
        export_btn = QPushButton("Export to CSV")
        export_btn.setCursor(Qt.PointingHandCursor)
        # Przycisk drugorzędny (variant="secondary" we wzorcu)
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.RAISED_BG};
                color: {styles.TEXT_PRIMARY};
                border-radius: 8px;
                padding: 10px 18px;
                font-size: {styles.font_px(14)}px;
                font-weight: 600;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {styles.HOVER_BG};
            }}
        """)
        export_btn.clicked.connect(self._on_export)
        btn_row.addWidget(export_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.layout_main.addWidget(card)

    def _on_export(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Vault", "passwords_export.csv", "CSV Files (*.csv)"
        )
        if not filepath:
            return
        try:
            self._password_service.export_to_csv(filepath)
            NotificationPopup(MSG_EXPORT_SUCCESS, self).show()
        except Exception as e:
            NotificationPopup(f"Export failed: {e}", self).show()

    # --- 3. Zmiana hasła głównego ---
    def _build_change_password(self):
        card = self._card_frame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        head = section_header(
            "lock", "Change Master Password",
            styles.TEXT_SECONDARY, styles.TEXT_PRIMARY, icon_size=18, font_px=17,
        )
        layout.addWidget(head)

        desc = QLabel(
            "All vault entries will be re-encrypted with the new password.\n"
            "Make sure to remember your new password - it cannot be recovered."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(
            f"font-size: {styles.font_px(14)}px; color: {styles.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        layout.addWidget(desc)

        # Siatka jak we wzorcu: Current na całą szerokość, New + Confirm obok
        # siebie, całość ograniczona do 560px
        fields_box = QWidget()
        fields_box.setMaximumWidth(560)
        fields_box.setStyleSheet("background: transparent; border: none;")
        fields_layout = QVBoxLayout(fields_box)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(14)

        self.current_pw = self._pw_field("Current Password")
        fields_layout.addWidget(self.current_pw)

        pw_row = QHBoxLayout()
        pw_row.setSpacing(14)
        self.new_pw = self._pw_field("New Password")
        self.confirm_pw = self._pw_field("Confirm New Password")
        pw_row.addWidget(self.new_pw)
        pw_row.addWidget(self.confirm_pw)
        fields_layout.addLayout(pw_row)

        layout.addWidget(fields_box)

        self.pw_status = QLabel("")
        self.pw_status.setStyleSheet(
            f"color: {styles.COLOR_RED}; font-size: {styles.font_px(14)}px;"
            " background: transparent; border: none;"
        )
        self.pw_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pw_status)

        self.pw_progress = QProgressBar()
        self.pw_progress.setMinimum(0)
        self.pw_progress.setMaximum(100)
        self.pw_progress.setValue(0)
        self.pw_progress.setTextVisible(True)
        self.pw_progress.setFormat("%p%")
        self.pw_progress.setFixedHeight(22)
        self.pw_progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {styles.BORDER_COLOR};
                border-radius: 6px;
                text-align: center;
                color: {styles.TEXT_PRIMARY};
                font-size: {styles.font_px(12)}px;
                font-weight: 600;
            }}
            QProgressBar::chunk {{
                background-color: {styles.COLOR_BLUE};
                border-radius: 6px;
            }}
        """)
        self.pw_progress.hide()
        layout.addWidget(self.pw_progress)

        btn_row = QHBoxLayout()
        self.change_pw_btn = QPushButton("Change Password")
        self.change_pw_btn.setCursor(Qt.PointingHandCursor)
        self.change_pw_btn.setStyleSheet(self._action_btn_style(styles.COLOR_BLUE))
        self.change_pw_btn.clicked.connect(self._on_change_password)
        btn_row.addWidget(self.change_pw_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.layout_main.addWidget(card)

    def _on_change_password(self):
        old = self.current_pw.text().strip()
        new = self.new_pw.text().strip()
        confirm = self.confirm_pw.text().strip()

        if not old or not new or not confirm:
            self.pw_status.setText(MSG_FILL_ALL_FIELDS)
            self.pw_status.setStyleSheet(
                f"color: {styles.COLOR_RED}; font-size: {styles.font_px(14)}px;"
                " background: transparent; border: none;"
            )
            return
        if new != confirm:
            self.pw_status.setText(MSG_NEW_PASSWORDS_NOT_MATCH)
            self.pw_status.setStyleSheet(
                f"color: {styles.COLOR_RED}; font-size: {styles.font_px(14)}px;"
                " background: transparent; border: none;"
            )
            return
        if new == old:
            self.pw_status.setText("New password must be different from current.")
            self.pw_status.setStyleSheet(
                f"color: {styles.COLOR_RED}; font-size: {styles.font_px(14)}px;"
                " background: transparent; border: none;"
            )
            return

        self.change_pw_btn.setEnabled(False)
        self.pw_progress.setValue(0)
        self.pw_progress.show()
        self.pw_status.setText("")

        self._worker = ChangePasswordWorker(self._auth_service, old, new)
        self._worker.progress.connect(self._on_pw_progress)
        self._worker.finished_ok.connect(self._on_pw_success)
        self._worker.finished_err.connect(self._on_pw_error)
        self._worker.start()

    @pyqtSlot(int)
    def _on_pw_progress(self, pct):
        self.pw_progress.setValue(pct)

    @pyqtSlot()
    def _on_pw_success(self):
        self.pw_progress.setValue(100)
        self.pw_status.setText(MSG_PASSWORD_CHANGED)
        self.pw_status.setStyleSheet(
            f"color: {styles.COLOR_GREEN}; font-size: {styles.font_px(14)}px;"
            " background: transparent; border: none;"
        )
        self.current_pw.clear()
        self.new_pw.clear()
        self.confirm_pw.clear()
        self.change_pw_btn.setEnabled(True)
        self.pw_progress.hide()
        self._worker = None

    @pyqtSlot(str)
    def _on_pw_error(self, msg):
        self.pw_status.setText(msg)
        self.pw_status.setStyleSheet(
            f"color: {styles.COLOR_RED}; font-size: {styles.font_px(14)}px;"
            " background: transparent; border: none;"
        )
        self.change_pw_btn.setEnabled(True)
        self.pw_progress.hide()
        self._worker = None

    # --- 4. Usunięcie konta ---
    def _build_delete_account(self):
        card = QFrame()
        card.setStyleSheet(f"""
            background-color: {styles.CARD_BG};
            border-radius: 12px;
            border: 1px solid {styles.COLOR_RED};
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        head = section_header(
            "triangle-alert", "Danger Zone",
            styles.COLOR_RED, styles.COLOR_RED, icon_size=18, font_px=17,
        )
        layout.addWidget(head)

        desc = QLabel(
            "Permanently delete your account and all saved passwords.\n"
            "This action cannot be undone."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(
            f"font-size: {styles.font_px(14)}px; color: {styles.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        layout.addWidget(desc)

        confirm_lbl = QLabel(f'Type "{self._username}" to confirm:')
        confirm_lbl.setStyleSheet(
            f"font-size: {styles.font_px(13)}px; color: {styles.TEXT_SECONDARY};"
            " background: transparent; border: none;"
        )
        layout.addWidget(confirm_lbl)

        self.delete_confirm_input = QLineEdit()
        self.delete_confirm_input.setPlaceholderText("Enter your username")
        self.delete_confirm_input.setMaximumWidth(350)
        self.delete_confirm_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {styles.INPUT_BG};
                color: {styles.TEXT_PRIMARY};
                border-radius: 8px;
                padding: 10px;
                border: 1px solid {styles.BORDER_COLOR};
                font-size: {styles.font_px(14)}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {styles.COLOR_RED};
            }}
        """)
        layout.addWidget(self.delete_confirm_input)

        self.delete_status = QLabel("")
        self.delete_status.setStyleSheet(
            f"color: {styles.COLOR_RED}; font-size: {styles.font_px(14)}px;"
            " background: transparent; border: none;"
        )
        layout.addWidget(self.delete_status)

        btn_row = QHBoxLayout()
        delete_btn = QPushButton("Delete Account")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.COLOR_RED};
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: {styles.font_px(16)}px;
                font-weight: 600;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #e0392e;
            }}
            QPushButton:pressed {{
                background-color: #c0302a;
            }}
        """)
        delete_btn.clicked.connect(self._on_delete_account)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.layout_main.addWidget(card)

    def _on_delete_account(self):
        typed = self.delete_confirm_input.text().strip()
        if typed != self._username:
            self.delete_status.setText("Username does not match. Please try again.")
            return
        reply = QMessageBox.warning(
            self, "Delete Account",
            f"Are you absolutely sure you want to delete the account \"{self._username}\"?\n\n"
            "All passwords will be permanently lost.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        ok = self._auth_service.delete_current_account()
        if ok:
            self.account_deleted.emit()
        else:
            self.delete_status.setText("Failed to delete account.")

    # --- Pomocniki --
    def _card_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("profileCard")
        frame.setStyleSheet(
            f"QFrame#profileCard {{ background-color: {styles.CARD_BG};"
            f" border: 1px solid {styles.HAIRLINE}; border-radius: 12px; }}"
        )
        return frame

    def _pw_field(self, placeholder: str) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setEchoMode(QLineEdit.Password)
        field.setMaximumWidth(350)
        field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {styles.INPUT_BG};
                color: {styles.TEXT_PRIMARY};
                border-radius: 8px;
                padding: 10px;
                border: 1px solid {styles.BORDER_COLOR};
                font-size: {styles.font_px(14)}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {styles.COLOR_BLUE};
            }}
        """)
        return field

    @staticmethod
    def _action_btn_style(color: str) -> str:
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: {styles.font_px(14)}px;
                font-weight: 600;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #0077ea;
            }}
        """
