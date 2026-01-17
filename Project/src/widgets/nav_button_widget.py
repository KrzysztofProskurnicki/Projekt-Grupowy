"""Navigation Button Widget for Sidebar."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import Qt


class NavButtonWidget(QWidget):
    """Custom navigation button with badge and icon."""
    
    def __init__(self, text: str, icon_char: str, count: int, is_active: bool = False):
        """Initialize navigation button.
        
        Args:
            text: Button label text.
            icon_char: Icon character (emoji).
            count: Badge count to display.
            is_active: Whether button is currently active.
        """
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)
        
        self.btn = QPushButton(f" {icon_char}   {text}")
        self.btn.setProperty("class", "nav-btn")
        self.btn.setCheckable(True)
        self.btn.setChecked(is_active)
        self.btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.badge = QLabel(str(count) if count > 0 else "")
        self.badge.setProperty("class", "badge")
        if is_active:
            self.badge.setStyleSheet("color: white;") 

        self.btn_layout = QHBoxLayout(self.btn)
        self.btn_layout.setContentsMargins(10, 0, 10, 0)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.badge)
        
        layout.addWidget(self.btn)
        self.setLayout(layout)
