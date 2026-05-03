from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QSizePolicy, QSpacerItem, QTextEdit,
                             QMessageBox, QInputDialog, QToolTip, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt5.QtGui import QFont, QIcon, QClipboard, QGuiApplication, QColor
from styles import TEXT_PRIMARY

class DetailView(QWidget):
    def __init__(self, switch_back_callback, favorite_callback=None, verify_callback=None):
        super().__init__()
        self.switch_back_callback = switch_back_callback
        self.favorite_callback = favorite_callback
        self.verify_callback = verify_callback
        self.current_id = None
        
        # Zmienne stanu
        self.is_favorite = True
        self.password_visible = False
        self.is_authenticated = False # Autoryzacja sesji
        self.actual_password = ""
        
        # Główny layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)
        
        # TOP LAYER: Nawigacja
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
        
        # HEADER LAYER: Ikona + Tytuł + Gwiazdka
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
        self.star_btn.setCursor(Qt.PointingHandCursor)
        self.update_star_style()
        self.star_btn.clicked.connect(self.toggle_favorite)
        
        header_layout.addWidget(self.icon_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(self.star_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # FIELDS LAYER
        # Pola: Username, Password, Website, Notes
        self.create_field("Nazwa Użytkownika", "", is_copyable=True)
        self.create_field("Hasło", "•••••••••••••", is_copyable=True, is_password=True)
        self.create_field("Strona usługi", "", is_copyable=True)
        self.create_field("Nototki", "", is_multiline=True)
        
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
        
        # Use QTextEdit for multiline fields (Notes), QLabel for others
        if is_multiline:
            value_widget = QTextEdit()
            value_widget.setPlainText(value_text)
            value_widget.setStyleSheet("""
                QTextEdit {
                    color: #f5f5f7;
                    font-size: 18px;
                    border: none;
                    background: transparent;
                }
            """)
            value_widget.setMinimumHeight(60)
            value_widget.setMaximumHeight(100)
            self.notes_edit = value_widget
        else:
            value_widget = QLabel(value_text)
            value_widget.setStyleSheet("color: #f5f5f7; font-size: 18px; border: none; background: transparent;")
        
            # DO identyfikacji pól
            if label_text == "Nazwa Użytkownika": self.username_lbl = value_widget
            elif label_text == "Hasło": self.password_lbl = value_widget
            elif label_text == "Strona usługi":  self.website_lbl = value_widget
        
        row.addWidget(value_widget)
        row.addStretch()
        
        # Akcje (Copy, Eye)
        if is_password:
            self.eye_btn = QPushButton("👁")
            self.eye_btn.setFixedSize(30, 30)
            self.eye_btn.setCursor(Qt.PointingHandCursor)
            self.eye_btn.setStyleSheet("color: #0a84ff; border: none; font-size: 16px; background: transparent;")
            self.eye_btn.clicked.connect(self.toggle_password_visibility_with_auth)
            row.addWidget(self.eye_btn)
            
            # Copy password button (requires auth)
            copy_pwd_btn = QPushButton("❐")
            copy_pwd_btn.setFixedSize(30, 30)
            copy_pwd_btn.setCursor(Qt.PointingHandCursor)
            copy_pwd_btn.setStyleSheet("color: #0a84ff; border: none; font-size: 16px; background: transparent;")
            copy_pwd_btn.clicked.connect(self.copy_password_with_auth)
            row.addWidget(copy_pwd_btn)
        
        if is_copyable and not is_multiline and not is_password:
            copy_btn = QPushButton("❐")
            copy_btn.setFixedSize(30, 30)
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.setStyleSheet("color: #0a84ff; border: none; font-size: 16px; background: transparent;")
            copy_btn.clicked.connect(lambda checked, w=value_widget, l=label_text: self.copy_with_notification(w.text(), l))
            row.addWidget(copy_btn)
            
        layout.addLayout(row)
        self.main_layout.addWidget(container)
    
    def request_master_password(self, on_success):
        """Show embedded master password overlay if not authenticated."""
        if self.is_authenticated:
            on_success()
            return
            
        def auth_success_wrapper():
            self.is_authenticated = True
            on_success()
            
        overlay = MasterPasswordOverlay(self, auth_success_wrapper, self.verify_callback)
        overlay.show()
    
    def toggle_password_visibility_with_auth(self):
        """Toggle password visibility with master password verification."""
        if not self.password_visible:
            # Need to verify before showing
            self.request_master_password(self._show_password)
        else:
            # Just hide it
            self.password_visible = False
            self.password_lbl.setText("•••••••••••••")
            self.eye_btn.setText("👁")
    
    def _show_password(self):
        self.password_visible = True
        self.password_lbl.setText(self.actual_password)
        self.eye_btn.setText("👁‍🗨")
    
    def copy_password_with_auth(self):
        """Copy password to clipboard with master password verification."""
        self.request_master_password(self._copy_password_action)
    
    def _copy_password_action(self):
        QGuiApplication.clipboard().setText(self.actual_password)
        self.show_notification("Copied!")
    
    def copy_with_notification(self, text, field_name):
        """Copy text and show notification."""
        QGuiApplication.clipboard().setText(text)
        self.show_notification("Copied!")
    
    def show_notification(self, message):
        """Show a temporary notification message using a custom popup."""
        popup = NotificationPopup(message, self)
        popup.show()

    def toggle_favorite(self):
        """Toggle the favorite state and update star appearance."""
        self.is_favorite = not self.is_favorite
        self.update_star_style()
        
        if self.favorite_callback and self.current_id is not None:
            self.favorite_callback(self.current_id, self.is_favorite)
    
    def update_star_style(self):
        """Update star button appearance based on favorite state."""
        if self.is_favorite:
            self.star_btn.setText("★")
            self.star_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #ffd60a;
                    font-size: 24px;
                    border: none;
                }
                QPushButton:hover {
                    color: #ffe066;
                }
            """)
        else:
            self.star_btn.setText("☆")
            self.star_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #98989d;
                    font-size: 24px;
                    border: none;
                }
                QPushButton:hover {
                    color: #ffd60a;
                }
            """)
    
    def toggle_password_visibility(self):
        """Toggle password visibility between hidden and shown."""
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_lbl.setText(self.actual_password)
            self.eye_btn.setText("👁‍🗨")
        else:
            self.password_lbl.setText("•••••••••••••")
            self.eye_btn.setText("👁")

    def update_data(self, entry):
        self.current_id = entry.get("id")
        title = entry.get("name", "")
        subtitle = entry.get("email", "")
        color = entry.get("color", "#333333")
        letter = entry.get("letter") or title[:1].upper() or "?"
        self.actual_password = entry.get("password", "")
        self.is_favorite = entry.get("favorite", False)
        self.is_authenticated = False # Reset auth when switching to new entry
        self.update_star_style()
        
        self.title_label.setText(title)
        self.icon_label.setText(letter)
        self.icon_label.setStyleSheet(f"""
            background-color: {color};
            color: #f5f5f7;
            border-radius: 20px;
            font-size: 40px;
            font-weight: bold;
        """)
        
        self.username_lbl.setText(subtitle)
        website = entry.get("url", "")
        self.link_label.setText(website or "No website")
        self.website_lbl.setText(website)
        self.notes_edit.setPlainText(entry.get("notes", ""))
        
        # Reset password visibility when switching entries
        self.password_visible = False
        self.password_lbl.setText("•••••••••••••")
        self.eye_btn.setText("👁")

class NotificationPopup(QWidget):
    """Custom toast notification with animation (Embedded Overlay)."""
    def __init__(self, message, parent=None):
        super().__init__(parent)
        # No Window flags -> Child widget
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Frame
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: #1c351e; 
                color: #ffffff;
                border: 1px solid black;
                border-radius: 6px;
                padding: 0px;
            }}
        """)
        
        frame_layout = QHBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        
        # Text
        text_lbl = QLabel(message)
        text_lbl.setAlignment(Qt.AlignCenter)
        text_lbl.setStyleSheet("font-size: 13px; font-weight: 500; border: none; background: transparent; padding: 4px 12px;") # Min padding for readability inside box
        frame_layout.addWidget(text_lbl)
        
        layout.addWidget(self.frame)
        
        # Position at top center of parent (Local Coordinates)
        if parent:
            # We are a child, so 0,0 is parent's top-left
            p_width = parent.width()
            my_width = self.sizeHint().width()
            x = (p_width - my_width) // 2
            y = 20 # 20px from top
            self.move(x, y)
            self.raise_() # Ensure top of siblings
        
        # Animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_animation)
        self.timer.start(2000) # Show for 2 seconds
        
        # Entry animation (Slide down small bit + Fade in)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.group_enter = QParallelAnimationGroup(self)
        
        # Opacity
        anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim_fade.setDuration(200)
        anim_fade.setStartValue(0)
        anim_fade.setEndValue(1)
        
        # Slide Down
        anim_pos = QPropertyAnimation(self, b"pos")
        anim_pos.setDuration(200)
        start_pos = self.pos()
        anim_pos.setStartValue(QPoint(start_pos.x(), start_pos.y() - 10))
        anim_pos.setEndValue(start_pos)
        
        self.group_enter.addAnimation(anim_fade)
        self.group_enter.addAnimation(anim_pos)
        self.group_enter.start()

    def close_animation(self):
        """Fade out and slide up."""
        self.group = QParallelAnimationGroup(self)
        
        # Opacity
        anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim_fade.setDuration(300)
        anim_fade.setStartValue(1)
        anim_fade.setEndValue(0)
        
        # Position (Slide Up)
        anim_pos = QPropertyAnimation(self, b"pos")
        anim_pos.setDuration(300)
        start_pos = self.pos()
        anim_pos.setStartValue(start_pos)
        anim_pos.setEndValue(QPoint(start_pos.x(), start_pos.y() - 20))
        
        self.group.addAnimation(anim_fade)
        self.group.addAnimation(anim_pos)
        
        self.group.finished.connect(self.close)
        self.group.start()

class MasterPasswordOverlay(QWidget):
    """Embedded overlay for Master Password verification."""
    def __init__(self, parent, on_success_callback, verify_callback=None):
        super().__init__(parent)
        self.on_success = on_success_callback
        self.verify_callback = verify_callback
        self.resize(parent.size())  # Cover entire parent
        
        # No window layout, just simple overlay behavior
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);") # Dimmed darker background
        
        # Main layout for centering
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Container
        container = QFrame()
        container.setFixedSize(320, 180)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: #1c1c1e;
                border: 1px solid #3a3a3c;
                border-radius: 12px;
            }}
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 16px;
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                background-color: #2c2c2e;
                color: white;
                border: 1px solid #48484a;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid #0a84ff;
            }}
            QPushButton {{
                background-color: #3a3a3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #48484a;
            }}
            QPushButton#primary {{
                background-color: #0a84ff;
            }}
            QPushButton#primary:hover {{
                background-color: #0077ed;
            }}
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setSpacing(16)
        
        # Title
        title_lbl = QLabel("Enter Master Password")
        title_lbl.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_lbl)
        
        # Input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.returnPressed.connect(self.verify_password)
        container_layout.addWidget(self.password_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.close)
        
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("primary")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(self.verify_password)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        
        container_layout.addLayout(btn_layout)
        layout.addWidget(container)
        
        self.password_input.setFocus()
    
    def verify_password(self):
        entered_pwd = self.password_input.text()
        
        if self.verify_callback and self.verify_callback(entered_pwd):
            self.on_success()
            self.close()
        else:
            # Shake animation or visual feedback for error
            anim = QPropertyAnimation(self.password_input, b"pos")
            anim.setDuration(100)
            anim.setLoopCount(3)
            start_pos = self.password_input.pos()
            # Simple shake logic not easily doable with layout managed widget without custom property
            # Instead, let's flash red border
            self.password_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2c2c2e;
                    color: white;
                    border: 1px solid #ff453a;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
            """)
            QTimer.singleShot(1000, lambda: self.password_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2c2c2e;
                    color: white;
                    border: 1px solid #48484a;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #0a84ff;
                }
            """))

    def showEvent(self, event):
        # Resize to cover parent whenever shown
        if self.parent():
            self.resize(self.parent().size())
        super().showEvent(event)
