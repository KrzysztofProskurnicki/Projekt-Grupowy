"""Widget elementu hasła - pojedyncza karta na liście haseł"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt5.QtCore import Qt
from styles import CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY


class PasswordItemWidget(QWidget):
    
    def __init__(self, title: str, subtitle: str, color: str, letter: str, favorite: bool = False):
        """Inicjalizuj widget elementu hasła
        
        Argumenty:
            title: Nazwa/tytuł hasła.
            subtitle: Email/podtytuł hasła.
            color: Kolor tła ikony.
            letter: Litera ikony.
            favorite: Czy has?o jest oznaczone jako ulubione.
        """
        super().__init__()
        
        # Widget kontenera (przezroczysty, trzyma marginesy)
        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 5, 0, 5)
        container_layout.setSpacing(0)
        
        # Ramka karty
        card_frame = QFrame()
        card_frame.setMinimumHeight(80)
        card_frame.setObjectName("cardFrame")
        card_frame.setStyleSheet(f"""
            QFrame#cardFrame {{
                background-color: {CARD_BG};
                border-radius: 12px;
            }}
            QFrame#cardFrame:hover {{
                background-color: #3a3a3c;
            }}
        """)
        
        # Układ treści wewnątrz karty
        hbox = QHBoxLayout(card_frame)
        hbox.setContentsMargins(15, 10, 15, 10)
        hbox.setSpacing(15)
        
        # Okrąg ikony
        icon_lbl = QLabel(letter)
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 24px;
            font-weight: bold;
            font-size: {styles.font_px(22)}px;
            border: none;
        """)
        hbox.addWidget(icon_lbl)
        
        # Treść tekstowa
        text_container = QWidget()
        vbox = QVBoxLayout(text_container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.setAlignment(Qt.AlignVCenter)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: {styles.font_px(24)}px; font-weight: 600; color: {TEXT_PRIMARY}; "
            f"border: none; background: transparent;"
        )
        
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet(
            f"font-size: {styles.font_px(16)}px; color: {TEXT_SECONDARY}; "
            f"border: none; background: transparent;"
        )
        
        vbox.addWidget(title_lbl)
        vbox.addWidget(subtitle_lbl)
        
        hbox.addWidget(text_container)
        hbox.addStretch()
        
        # Ikona ulubionego wpisu
        if favorite:
            fav_lbl = QLabel("⭐")
            fav_lbl.setStyleSheet(f"font-size: {styles.font_px(16)}px; background: transparent; border: none;")
            hbox.addWidget(fav_lbl)
            
        # Chevron
        chevron = QLabel("›")
        chevron.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {styles.font_px(24)}px; font-weight: bold; "
            f"background: transparent; border: none;"
        )
        hbox.addWidget(chevron)
        
        # Dodaj kartę do kontenera
        container_layout.addWidget(card_frame)
