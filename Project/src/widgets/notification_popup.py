"""Widget powiadomienia popup"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame, QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QParallelAnimationGroup



class NotificationPopup(QWidget):
    """Niestandardowe powiadomienie toast z animacją"""
    
    def __init__(self, message: str, parent=None):
        """Inicjalizuj popup powiadomienia.
        
        Argumenty:
            message: Komunikat do wyświetlenia.
            parent: Widget nadrzędny (do pozycjonowania).
        """
        super().__init__(parent)
        # Bez flag okna -> widget potomny
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Układ
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Ramka
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
        
        # Tekst
        text_lbl = QLabel(message)
        text_lbl.setAlignment(Qt.AlignCenter)
        text_lbl.setStyleSheet(
            f"font-size: {styles.font_px(13)}px; font-weight: 500; border: none; "
            "background: transparent; padding: 4px 12px;"
        )
        frame_layout.addWidget(text_lbl)
        
        layout.addWidget(self.frame)
        
        # Pozycja u góry na środku parent
        if parent:
            p_width = parent.width()
            my_width = self.sizeHint().width()
            x = (p_width - my_width) // 2
            y = 20
            self.move(x, y)
            self.raise_()
        
        # Animacja
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_animation)
        self.timer.start(2000)  # Poka? przez 2 sekundy
        
        # Animacja wejścia (lekki zjazd w dół + pojawienie)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.group_enter = QParallelAnimationGroup(self)
        
        # Przezroczystość
        anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim_fade.setDuration(200)
        anim_fade.setStartValue(0)
        anim_fade.setEndValue(1)
        
        # Zjazd w dół
        anim_pos = QPropertyAnimation(self, b"pos")
        anim_pos.setDuration(200)
        start_pos = self.pos()
        anim_pos.setStartValue(QPoint(start_pos.x(), start_pos.y() - 10))
        anim_pos.setEndValue(start_pos)
        
        self.group_enter.addAnimation(anim_fade)
        self.group_enter.addAnimation(anim_pos)
        self.group_enter.start()

    def close_animation(self):
        """Wygaszenie i przesunięcie w górę"""
        self.group = QParallelAnimationGroup(self)
        
        # Przezroczystość
        anim_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim_fade.setDuration(300)
        anim_fade.setStartValue(1)
        anim_fade.setEndValue(0)
        
        # Pozycja
        anim_pos = QPropertyAnimation(self, b"pos")
        anim_pos.setDuration(300)
        start_pos = self.pos()
        anim_pos.setStartValue(start_pos)
        anim_pos.setEndValue(QPoint(start_pos.x(), start_pos.y() - 20))
        
        self.group.addAnimation(anim_fade)
        self.group.addAnimation(anim_pos)
        
        self.group.finished.connect(self.close)
        self.group.start()
