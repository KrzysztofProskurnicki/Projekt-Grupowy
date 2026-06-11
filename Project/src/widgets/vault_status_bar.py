"""Widget paska statusu sejfu - smukły zaokrąglony pasek Strong/Weak (wg wzorca)."""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath
import styles


class VaultStatusBar(QWidget):
    """Pasek 12px z udziałem haseł silnych/słabych i legendą z kropkami."""

    BAR_H = 12
    GAP = 2  # przerwa między segmentami

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(56)
        self.stats = {"strong": 0, "medium": 0, "weak": 0, "total": 1}

    def set_stats(self, strong: int, medium: int, weak: int, total: int):
        """Ustaw statystyki paska.

        Argumenty:
            strong: Liczba silnych haseł
            medium: Liczba średnich haseł
            weak: Liczba słabych haseł
            total: Liczba haseł.
        """
        self.stats = {"strong": strong, "medium": medium, "weak": weak,
                      "total": max(1, total)}
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w_total = self.width()
        y_bar = 6
        radius = self.BAR_H / 2

        # Przytnij wszystko do zaokrąglonego kształtu paska
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, y_bar, w_total, self.BAR_H), radius, radius)

        painter.save()
        painter.setClipPath(clip)
        painter.setPen(Qt.NoPen)

        # Tor
        painter.setBrush(QColor(styles.RAISED_BG))
        painter.drawRect(QRectF(0, y_bar, w_total, self.BAR_H))

        total = self.stats["total"]
        segments = [
            (self.stats["strong"], QColor(styles.COLOR_GREEN), "Strong"),
            (self.stats["medium"], QColor(styles.COLOR_YELLOW), "Medium"),
            (self.stats["weak"], QColor(styles.COLOR_RED), "Weak"),
        ]

        x = 0.0
        for val, color, _label in segments:
            if val > 0:
                seg_w = (val / total) * w_total
                painter.setBrush(color)
                painter.drawRect(QRectF(x, y_bar, max(0.0, seg_w - self.GAP), self.BAR_H))
                x += seg_w
        painter.restore()

        # Legenda: kropka + "Strong (75%)"
        y_leg = y_bar + self.BAR_H + 24
        x_leg = 0
        font = QFont("Segoe UI")
        font.setPixelSize(styles.font_px(13))
        painter.setFont(font)

        for val, color, label in segments:
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(int(x_leg), int(y_leg) - 8, 8, 8)

            label_full = f"{label} ({int(round(val / total * 100))}%)"
            painter.setPen(QColor(styles.TEXT_SECONDARY))
            painter.drawText(int(x_leg) + 14, int(y_leg), label_full)

            w_text = painter.fontMetrics().horizontalAdvance(label_full)
            x_leg += 14 + w_text + 24
