"""Nakładka potwierdzenia - ciemna karta na przyciemnionym tle (wg motywu).

Zamiennik systemowego QMessageBox: wyśrodkowana karta z pytaniem oraz
przyciskami potwierdzenia (checkmark) i anulowania (iks). Kliknięcie poza
kartą lub Esc zamyka nakładkę bez akcji.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect
from PyQt5.QtGui import QIcon
from widgets.icons import tinted_pixmap
import styles


class ConfirmOverlay(QWidget):
    """Modalna nakładka "Are you sure?" emitująca *confirmed* po akceptacji."""

    confirmed = pyqtSignal()

    def __init__(self, parent, title="Are you sure?", message="",
                 confirm_text="  Remove", danger=True):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 55%);")
        self.resize(parent.size())

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFixedWidth(400)
        # Pion Preferred (nie Fixed) - wysokość musi uwzględnić zawinięty
        # komunikat (heightForWidth); stretch w outer i tak nie pozwala rosnąć
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        card.setObjectName("confirmCard")
        card.setStyleSheet(f"""
            QFrame#confirmCard {{
                background-color: {styles.CARD_BG};
                border: 1px solid {styles.HAIRLINE_STRONG};
                border-radius: 16px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 26, 28, 24)
        card_layout.setSpacing(12)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: {styles.font_px(19)}px; font-weight: bold;"
            f" color: {styles.TEXT_PRIMARY}; background: transparent; border: none;"
        )
        card_layout.addWidget(title_lbl)

        if message:
            msg_lbl = QLabel(message)
            msg_lbl.setWordWrap(True)
            msg_lbl.setStyleSheet(
                f"font-size: {styles.font_px(14)}px; color: {styles.TEXT_SECONDARY};"
                " background: transparent; border: none;"
            )
            # Jawna wysokość zawiniętego tekstu - layout karty nie propaguje
            # heightForWidth i ucina drugą linijkę
            text_width = 400 - 28 - 28
            wrapped = msg_lbl.fontMetrics().boundingRect(
                QRect(0, 0, text_width, 1000), Qt.TextWordWrap, message
            )
            msg_lbl.setMinimumHeight(wrapped.height() + 4)
            card_layout.addWidget(msg_lbl)

        card_layout.addSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("  Cancel")
        cancel_btn.setIcon(QIcon(tinted_pixmap("x", styles.TEXT_SECONDARY, 16)))
        cancel_btn.setIconSize(QSize(16, 16))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {styles.TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: {styles.font_px(14)}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {styles.HOVER_BG};
                color: {styles.TEXT_PRIMARY};
            }}
        """)
        cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(cancel_btn)

        accent = styles.COLOR_RED if danger else styles.COLOR_BLUE
        hover = "#e03a30" if danger else styles.COLOR_BLUE_HOVER
        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setIcon(QIcon(tinted_pixmap("check", "#ffffff", 16)))
        confirm_btn.setIconSize(QSize(16, 16))
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: {styles.font_px(14)}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """)
        confirm_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(confirm_btn)

        card_layout.addLayout(btn_row)

        outer.addStretch()
        outer.addWidget(card, 0, Qt.AlignHCenter)
        outer.addStretch()

    def _on_confirm(self):
        self.confirmed.emit()
        self.close()

    # --- Zachowanie nakładki ---
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # Kliknięcie w przyciemnione tło (poza kartą) zamyka nakładkę
        if self.childAt(event.pos()) is None:
            self.close()
        super().mousePressEvent(event)

    def showEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
        super().showEvent(event)
        self.setFocus()
