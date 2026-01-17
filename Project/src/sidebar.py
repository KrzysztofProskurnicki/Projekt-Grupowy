"""Sidebar component with navigation buttons."""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from widgets.nav_button_widget import NavButtonWidget


class Sidebar(QFrame):
    """Sidebar widget with navigation."""
    nav_clicked = pyqtSignal(int)  # Signal emitting index of clicked button
    
    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar Header
        app_title = QLabel("Passwords")
        app_title.setObjectName("AppTitle")
        layout.addWidget(app_title)
        
        # Navigation container
        nav_container = QWidget()
        self.nav_layout = QVBoxLayout(nav_container)
        self.nav_layout.setContentsMargins(8, 8, 8, 8)
        self.nav_layout.setSpacing(4)
        
        # Define buttons configuration
        # Format: (Title, Icon, Badge Count, ID)
        self.buttons_config = [
            ("All Passwords", "🔑", 12),
            ("Favorites", "⭐", 3),
            ("Security Recommendations", "🛡️", 2),
            ("Vault", "🔒", 0),      # Proposed new item
            ("Settings", "⚙️", 0),   # Proposed new item
            ("Profile", "👤", 0)     # Proposed new item
        ]
        
        self.nav_buttons = []
        for i, (text, icon, count) in enumerate(self.buttons_config):
            is_active = (i == 0)
            btn = NavButtonWidget(text, icon, count, is_active)
            # Use closure to capture index
            btn.btn.clicked.connect(lambda checked, idx=i: self.handle_click(idx))
            self.nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        layout.addWidget(nav_container)
        layout.addStretch()
        
        # User footer (optional proposal)
        user_footer = QLabel("Logged in as: User")
        user_footer.setStyleSheet("color: #98989d; padding: 16px; font-size: 12px;")
        layout.addWidget(user_footer)

    def handle_click(self, index):
        """Handle mutual exclusion and emit signal."""
        for i, nav_widget in enumerate(self.nav_buttons):
            if i == index:
                nav_widget.btn.setChecked(True)
                nav_widget.badge.setStyleSheet("color: white;")
            else:
                nav_widget.btn.setChecked(False)
                nav_widget.badge.setStyleSheet("color: #98989d;")
        
        self.nav_clicked.emit(index)
        
    def update_badge(self, index, count):
        """Update badge count for a specific button."""
        if 0 <= index < len(self.nav_buttons):
            self.nav_buttons[index].badge.setText(str(count) if count > 0 else "")
