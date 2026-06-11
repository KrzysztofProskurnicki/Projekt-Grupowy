"""Widok ustawień - preferencje użytkownika aplikacji"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSlider,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from widgets.icons import section_header, tinted_icon
import styles


class SettingsView(QWidget):

    settings_changed = pyqtSignal(str, object)
    theme_changed = pyqtSignal(str)
    accent_changed = pyqtSignal(str)
    font_size_changed = pyqtSignal(int)

    def __init__(self, settings_service):
        super().__init__()
        self._settings = settings_service
        self._btn_groups = {}
        self._build_ui()

    def refresh_theme(self):
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        self._btn_groups = {}
        self._build_ui()

    def _build_ui(self):
        # Tło scope'owane selektorem - goły "background-color" kaskadowałby
        # na wszystkie etykiety (ciemne paski za tekstem na kartach)
        self.setObjectName("settingsView")
        self.setStyleSheet(f"QWidget#settingsView {{ background-color: {styles.DARK_BG}; }}")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background-color: {styles.DARK_BG}; }}"
            f" QScrollBar:vertical {{ width: 0px; }}"
        )

        content = QWidget()
        content.setObjectName("settingsContent")
        content.setStyleSheet(f"QWidget#settingsContent {{ background-color: {styles.DARK_BG}; }}")
        self.layout_main = QVBoxLayout(content)
        self.layout_main.setContentsMargins(40, 40, 40, 40)
        self.layout_main.setSpacing(30)

        title = section_header(
            "settings", "Settings",
            styles.COLOR_BLUE, styles.TEXT_PRIMARY, icon_size=26, font_px=28,
        )
        self.layout_main.addWidget(title)

        self._build_auto_lock()
        self._build_clipboard_clear()
        self._build_theme()
        self._build_accent()
        self._build_font_size()

        self.layout_main.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _create_option_row(self, options, current_value, on_select, group_key):
        """Zbuduj segmented control (wspólny kontener z pigułkami) wg wzorca."""
        layout = QHBoxLayout()
        layout.setSpacing(0)

        seg = QWidget()
        seg.setObjectName("segControl")
        seg.setStyleSheet(
            f"QWidget#segControl {{ background-color: {styles.DARK_BG};"
            f" border: 1px solid {styles.HAIRLINE}; border-radius: 8px; }}"
        )
        seg_layout = QHBoxLayout(seg)
        seg_layout.setContentsMargins(3, 3, 3, 3)
        seg_layout.setSpacing(2)

        buttons = []
        for label_text, val in options:
            btn = QPushButton(label_text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=val: on_select(v))
            seg_layout.addWidget(btn)
            buttons.append((val, btn))

        layout.addWidget(seg)
        layout.addStretch()
        self._btn_groups[group_key] = buttons
        self._update_btn_styles(group_key, current_value)
        return layout

    def _update_btn_styles(self, group_key, active_value):
        if group_key not in self._btn_groups:
            return
        for val, btn in self._btn_groups[group_key]:
            if val == active_value:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {styles.COLOR_BLUE};
                        color: white;
                        border-radius: 6px;
                        padding: 6px 14px;
                        font-size: 13px;
                        font-weight: 600;
                        border: none;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {styles.TEXT_SECONDARY};
                        border-radius: 6px;
                        padding: 6px 14px;
                        font-size: 13px;
                        font-weight: 600;
                        border: none;
                    }}
                    QPushButton:hover {{
                        background-color: {styles.OVERLAY_HOVER};
                        color: {styles.TEXT_PRIMARY};
                    }}
                """)

    def _card_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("settingsCard")
        frame.setStyleSheet(
            f"QFrame#settingsCard {{ background-color: {styles.CARD_BG};"
            f" border: 1px solid {styles.HAIRLINE}; border-radius: 12px; }}"
        )
        return frame

    def _build_auto_lock(self):
        card = self._card_frame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        head = QLabel("Auto-Lock Timer")
        head.setStyleSheet(styles.SECTION_TITLE_STYLE)
        layout.addWidget(head)
        desc = QLabel(
            "Automatically lock the vault after a period of inactivity. "
            "You will be logged out and need to sign in again."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 14px; color: {styles.TEXT_SECONDARY}; border: none;")
        layout.addWidget(desc)
        options = [("Off", 0), ("1 min", 1), ("5 min", 5), ("10 min", 10), ("15 min", 15), ("30 min", 30)]

        def on_select(val):
            self._settings.auto_lock_minutes = val
            self._update_btn_styles('auto_lock', val)
            self.settings_changed.emit('auto_lock_minutes', val)

        layout.addLayout(self._create_option_row(options, self._settings.auto_lock_minutes, on_select, 'auto_lock'))
        self.layout_main.addWidget(card)

    def _build_clipboard_clear(self):
        card = self._card_frame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        head = QLabel("Clipboard Auto-Clear")
        head.setStyleSheet(styles.SECTION_TITLE_STYLE)
        layout.addWidget(head)
        desc = QLabel(
            "Automatically clear the clipboard after copying a password "
            "to prevent it from staying accessible."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 14px; color: {styles.TEXT_SECONDARY}; border: none;")
        layout.addWidget(desc)
        options = [("Off", 0), ("10 sec", 10), ("30 sec", 30), ("60 sec", 60), ("120 sec", 120)]

        def on_select(val):
            self._settings.clipboard_clear_seconds = val
            self._update_btn_styles('clipboard_clear', val)
            self.settings_changed.emit('clipboard_clear_seconds', val)

        layout.addLayout(self._create_option_row(options, self._settings.clipboard_clear_seconds, on_select, 'clipboard_clear'))
        self.layout_main.addWidget(card)

    def _build_theme(self):
        card = self._card_frame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        head = QLabel("Theme")
        head.setStyleSheet(styles.SECTION_TITLE_STYLE)
        layout.addWidget(head)
        desc = QLabel("Choose the visual appearance of the application.")
        desc.setStyleSheet(f"font-size: 14px; color: {styles.TEXT_SECONDARY}; border: none;")
        layout.addWidget(desc)

        def set_theme(t):
            self._settings.theme = t
            self._update_btn_styles('theme', t)
            self._update_theme_icons(t)
            self.theme_changed.emit(t)

        options = [("  System", 'system'), ("  Dark", 'dark'), ("  Light", 'light')]
        layout.addLayout(self._create_option_row(options, self._settings.theme, set_theme, 'theme'))

        # Ikony monitora/księżyca/słońca w segmentach
        for val, btn in self._btn_groups['theme']:
            btn.setIconSize(QSize(16, 16))
        self._update_theme_icons(self._settings.theme)

        self.layout_main.addWidget(card)

    _THEME_ICONS = {'system': 'monitor', 'dark': 'moon', 'light': 'sun'}

    def _update_theme_icons(self, active_theme):
        """Przekoloruj ikony segmentów System/Dark/Light (białe gdy aktywne)."""
        for val, btn in self._btn_groups.get('theme', []):
            icon_name = self._THEME_ICONS.get(val, 'sun')
            color = "white" if val == active_theme else styles.TEXT_SECONDARY
            btn.setIcon(tinted_icon(icon_name, color, 16))

    def _build_accent(self):
        """Karta wyboru koloru akcentu - okrągłe próbki palet."""
        card = self._card_frame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        head = QLabel("Accent Color")
        head.setStyleSheet(styles.SECTION_TITLE_STYLE)
        layout.addWidget(head)
        desc = QLabel("Pick the highlight color used for buttons, links and selections.")
        desc.setStyleSheet(f"font-size: 14px; color: {styles.TEXT_SECONDARY}; border: none;")
        layout.addWidget(desc)

        row = QHBoxLayout()
        row.setSpacing(12)
        self._accent_buttons = []

        def on_select(val):
            self._settings.accent = val
            self._update_accent_styles(val)
            self.accent_changed.emit(val)

        for key, label, color in styles.ACCENT_CHOICES:
            btn = QPushButton()
            btn.setFixedSize(34, 34)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(label)
            btn.setIconSize(QSize(16, 16))
            btn.clicked.connect(lambda checked, v=key: on_select(v))
            row.addWidget(btn)
            self._accent_buttons.append((key, color, btn))
        row.addStretch()
        layout.addLayout(row)

        self._update_accent_styles(self._settings.accent)
        self.layout_main.addWidget(card)

    def _update_accent_styles(self, active_accent):
        """Obrysuj aktywną próbkę i pokaż na niej znacznik wyboru."""
        for key, color, btn in self._accent_buttons:
            active = (key == active_accent)
            ring = styles.TEXT_PRIMARY if active else "transparent"
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {color}; border-radius: 17px;"
                f" border: 3px solid {ring}; }}"
            )
            btn.setIcon(tinted_icon("check", "white", 16) if active else QIcon())

    def _build_font_size(self):
        card = self._card_frame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        head = QLabel("Font Size")
        head.setStyleSheet(styles.SECTION_TITLE_STYLE)
        layout.addWidget(head)
        desc = QLabel("Adjust the interface font size for better readability.")
        desc.setStyleSheet(f"font-size: 14px; color: {styles.TEXT_SECONDARY}; border: none;")
        layout.addWidget(desc)

        slider_row = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(22)
        self.slider.setValue(self._settings.font_size)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(2)
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {styles.BORDER_COLOR};
                height: 8px;
                background: {styles.INPUT_BG};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {styles.COLOR_BLUE};
                border: 1px solid #005bb5;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """)

        self.size_lbl = QLabel(f"{self._settings.font_size}px")
        self.size_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {styles.TEXT_PRIMARY}; border:none;")

        slider_row.addWidget(self.slider)
        slider_row.addWidget(self.size_lbl)
        layout.addLayout(slider_row)

        self.preview_lbl = QLabel("The quick brown fox jumps over the lazy dog")
        self.preview_lbl.setStyleSheet(
            f"font-size: {self._settings.font_size}px; color: {styles.TEXT_PRIMARY}; border: none; margin-top: 10px;"
        )
        layout.addWidget(self.preview_lbl)

        def on_slider_change(val):
            self.size_lbl.setText(f"{val}px")
            self.preview_lbl.setStyleSheet(
                f"font-size: {val}px; color: {styles.TEXT_PRIMARY}; border: none; margin-top: 10px;"
            )
            self._settings.font_size = val
            self.font_size_changed.emit(val)

        self.slider.valueChanged.connect(on_slider_change)
        self.layout_main.addWidget(card)
