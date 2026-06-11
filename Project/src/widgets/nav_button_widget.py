"""Widget przycisku nawigacji dla sidebara."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from widgets.icons import tinted_pixmap
import styles


class NavButtonWidget(QWidget):
    """Niestandardowy przycisk nawigacji z ikoną SVG i odznaką licznika."""

    def __init__(self, text: str, icon_name: str, count: int, is_active: bool = False):
        """Inicjalizuj przycisk nawigacji.

        Argumenty:
            text: Tekst etykiety przycisku.
            icon_name: Nazwa ikony Lucide (plik assets/icons/<name>.svg).
            count: Licznik odznaki do wyświetlenia.
            is_active: Czy przycisk jest aktualnie aktywny.
        """
        super().__init__()
        self.icon_name = icon_name

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn = QPushButton(f"  {text}")
        self.btn.setCheckable(True)
        self.btn.setChecked(is_active)
        self.btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.btn.setIconSize(QSize(18, 18))
        self.set_icon_color("white" if is_active else styles.TEXT_SECONDARY)
        self.update_style(is_active)

        self.badge = QLabel(str(count) if count > 0 else "")
        self.badge.setProperty("class", "badge")
        if is_active:
            self.badge.setStyleSheet("color: rgba(255, 255, 255, 85%); font-size: 13px; font-weight: 600;")

        self.btn_layout = QHBoxLayout(self.btn)
        self.btn_layout.setContentsMargins(10, 0, 10, 0)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.badge)

        layout.addWidget(self.btn)
        self.setLayout(layout)

    def set_icon_color(self, color: str):
        """Przekoloruj ikonę (biała gdy aktywny, szara gdy nieaktywny)."""
        self.btn.setIcon(QIcon(tinted_pixmap(self.icon_name, color, 18)))

    def update_style(self, is_active: bool):
        """Ustaw styl przycisku (aktywny = niebieska pigułka jak NavItem we wzorcu)."""
        if is_active:
            self.btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 11px 12px;
                    border-radius: 8px;
                    color: white;
                    font-size: 14px;
                    font-weight: 500;
                    background-color: {styles.COLOR_BLUE};
                    border: none;
                }}
            """)
        else:
            self.btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 11px 12px;
                    border-radius: 8px;
                    color: {styles.TEXT_SECONDARY};
                    font-size: 14px;
                    font-weight: 500;
                    background-color: transparent;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {styles.OVERLAY_HOVER};
                    color: {styles.TEXT_PRIMARY};
                }}
            """)
