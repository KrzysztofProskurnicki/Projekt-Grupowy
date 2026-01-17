"""Notification Popup Widget - Toast notification with animation."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame, QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QParallelAnimationGroup



class NotificationPopup(QWidget):
    """Custom toast notification with animation (Embedded Overlay)."""
    
    def __init__(self, message: str, parent=None):
        """Initialize notification popup.
        
        Args:
            message: Message to display.
            parent: Parent widget (for positioning).
        """
        super().__init__(parent)
        # No Window flags -> Child widget
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Frame
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #1c351e; 
                color: #ffffff;
                border: 1px solid black;
                border-radius: 6px;
                padding: 0px;
            }
        """)
        
        frame_layout = QHBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        
        # Text
        text_lbl = QLabel(message)
        text_lbl.setAlignment(Qt.AlignCenter)
        text_lbl.setStyleSheet(
            "font-size: 13px; font-weight: 500; border: none; "
            "background: transparent; padding: 4px 12px;"
        )
        frame_layout.addWidget(text_lbl)
        
        layout.addWidget(self.frame)
        
        # Position at top center of parent (Local Coordinates)
        if parent:
            # We are a child, so 0,0 is parent's top-left
            p_width = parent.width()
            my_width = self.sizeHint().width()
            x = (p_width - my_width) // 2
            y = 20  # 20px from top
            self.move(x, y)
            self.raise_()  # Ensure top of siblings
        
        # Animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_animation)
        self.timer.start(2000)  # Show for 2 seconds
        
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
