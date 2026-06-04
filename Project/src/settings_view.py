"""Settings View - User preferences for the application."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSlider,
)
from PyQt5.QtCore import Qt, pyqtSignal
import styles


class SettingsView(QWidget):
    """Settings configuration view."""

    settings_changed = pyqtSignal(str, object)
    theme_changed = pyqtSignal(str)
    font_size_changed = pyqtSignal(int)

    def __init__(self, settings_service):
        super().__init__()
        self._settings = settings_service
        self._btn_groups = {}
        self._build_ui()

    # -------------------------------------------------------------- refresh --
    def refresh_theme(self):
        """Rebuild UI with current theme colors."""
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        self._btn_groups = {}
        self._build_ui()

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

        title = QLabel("⚙️ Settings")
        title.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {styles.TEXT_PRIMARY}; margin-bottom: 10px;"
        )
        self.layout_main.addWidget(title)

        self._build_auto_lock()
        self._build_clipboard_clear()
        self._build_theme()
        self._build_font_size()

        self.layout_main.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _create_option_row(self, options, current_value, on_select, group_key):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        buttons = []
        for label_text, val in options:
            btn = QPushButton(label_text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=val: on_select(v))
            layout.addWidget(btn)
            buttons.append((val, btn))
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
                        border-radius: 8px;
                        padding: 10px 18px;
                        font-size: 14px;
                        font-weight: bold;
                        border: none;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {styles.INPUT_BG};
                        color: {styles.TEXT_SECONDARY};
                        border-radius: 8px;
                        padding: 10px 18px;
                        font-size: 14px;
                        font-weight: 500;
                        border: none;
                    }}
                    QPushButton:hover {{
                        background-color: {styles.BORDER_COLOR};
                        color: {styles.TEXT_PRIMARY};
                    }}
                """)

    def _card_frame(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {styles.CARD_BG}; border-radius: 12px;")
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

        btn_row = QHBoxLayout()
        btn_row.setSpacing(20)

        self.dark_btn = QPushButton("🌙 Dark")
        self.light_btn = QPushButton("☀️ Light")
        for btn in (self.dark_btn, self.light_btn):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(80)

        self._apply_theme_btn_styles(self._settings.theme)

        def set_theme(t):
            self._settings.theme = t
            self._apply_theme_btn_styles(t)
            self.theme_changed.emit(t)

        self.dark_btn.clicked.connect(lambda: set_theme('dark'))
        self.light_btn.clicked.connect(lambda: set_theme('light'))

        btn_row.addWidget(self.dark_btn)
        btn_row.addWidget(self.light_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.layout_main.addWidget(card)

    def _apply_theme_btn_styles(self, theme):
        active_style = f"""
            QPushButton {{
                background-color: {styles.HOVER_BG};
                color: {styles.TEXT_PRIMARY};
                border-radius: 12px;
                border: 2px solid {styles.COLOR_BLUE};
                font-size: 18px;
                font-weight: bold;
            }}
        """
        inactive_style = f"""
            QPushButton {{
                background-color: {styles.DARK_BG};
                color: {styles.TEXT_SECONDARY};
                border-radius: 12px;
                border: 1px solid {styles.BORDER_COLOR};
                font-size: 18px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {styles.HOVER_BG};
            }}
        """
        self.dark_btn.setStyleSheet(active_style if theme == 'dark' else inactive_style)
        self.light_btn.setStyleSheet(active_style if theme == 'light' else inactive_style)

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
