"""ScoreRing - pierscien wyniku bezpieczenstwa (klon ScoreRing z wzorca Security.jsx).

Luk 270 stopni rysowany QPainterem: tor w kolorze RAISED_BG, luk postepu
w kolorze progu, w srodku duza liczba wyniku z "/100" i pastylka statusu.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPainter, QPen, QFont, QFontMetrics, QPainterPath
import styles


def _tier(score):
    """Zwraca (etykieta, kolor, tlo pastylki) dla danego wyniku."""
    if score >= 80:
        return "EXCELLENT", styles.COLOR_GREEN, QColor(48, 209, 88, 41)
    if score >= 60:
        return "GOOD", styles.COLOR_GREEN, QColor(48, 209, 88, 41)
    if score >= 40:
        return "FAIR", styles.COLOR_ORANGE, QColor(255, 159, 10, 41)
    return "AT RISK", styles.COLOR_RED, QColor(255, 69, 58, 41)


class GaugeWidget(QWidget):
    """Pierscien 270 stopni z wynikiem 0-100 i pastylka progu."""

    SIZE = 168       # bok widgetu (px), jak we wzorcu
    RADIUS = 64      # promien luku
    STROKE = 12      # grubosc kreski
    START_ANGLE = -135  # start: 135 stopni zgodnie z zegarem od godziny 3 (lewy dol)
    SPAN = 270          # luk obejmuje 270 stopni, przerwa na dole

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)
        self._score = 0

    def set_score(self, value: int):
        """Ustawia wynik (0-100) i odswieza rysunek.

        Celowo bez animacji - wartosc musi byc poprawna od pierwszej klatki
        (poprzednia QPropertyAnimation startowala od zera i kazdy render przed
        jej zakonczeniem pokazywal 0%).
        """
        self._score = max(0, min(100, int(value)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2
        r = self.RADIUS
        arc_rect = QRectF(cx - r, cy - r, r * 2, r * 2)

        label, color, soft_bg = _tier(self._score)

        # --- Tor (270 stopni, zaokraglone konce) ---
        pen = QPen(QColor(styles.RAISED_BG), self.STROKE, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(arc_rect, self.START_ANGLE * 16, -self.SPAN * 16)

        # --- Luk postepu w kolorze progu ---
        frac = self._score / 100.0
        if frac > 0:
            pen.setColor(QColor(color))
            painter.setPen(pen)
            painter.drawArc(arc_rect, self.START_ANGLE * 16,
                            int(round(-self.SPAN * frac * 16)))

        # --- Liczba wyniku + "/100" (wyrownane do linii bazowej) ---
        # Tłumione skalowanie - pierścień ma sztywne 168px, pełna skala
        # wypycha liczbę poza obrys przy większym foncie
        font_num = QFont("Segoe UI")
        font_num.setPixelSize(styles.font_px_soft(38))
        font_num.setWeight(QFont.Bold)
        fm_num = QFontMetrics(font_num)

        font_sub = QFont("Segoe UI")
        font_sub.setPixelSize(styles.font_px_soft(14))
        font_sub.setWeight(QFont.DemiBold)
        fm_sub = QFontMetrics(font_sub)

        num_str = str(self._score)
        sub_str = "/100"
        w_num = fm_num.horizontalAdvance(num_str)
        w_sub = fm_sub.horizontalAdvance(sub_str)
        total_w = w_num + 2 + w_sub

        # Wysokosc bloku: cyfry (cap height) + odstep 8 + pastylka
        try:
            cap_h = fm_num.capHeight()
        except AttributeError:
            cap_h = int(fm_num.ascent() * 0.72)

        font_pill = QFont("Segoe UI")
        font_pill.setPixelSize(styles.font_px_soft(11))
        font_pill.setWeight(QFont.Bold)
        font_pill.setLetterSpacing(QFont.AbsoluteSpacing, 0.7)
        fm_pill = QFontMetrics(font_pill)
        pill_h = fm_pill.height() + 6
        pill_w = fm_pill.horizontalAdvance(label) + 22

        block_h = cap_h + 8 + pill_h
        top = cy - block_h / 2
        baseline = top + cap_h

        x_num = cx - total_w / 2
        painter.setFont(font_num)
        painter.setPen(QColor(styles.TEXT_PRIMARY))
        painter.drawText(int(round(x_num)), int(round(baseline)), num_str)

        painter.setFont(font_sub)
        painter.setPen(QColor(styles.TEXT_TERTIARY))
        painter.drawText(int(round(x_num + w_num + 2)), int(round(baseline)), sub_str)

        # --- Pastylka progu (uppercase, miekkie tlo) ---
        pill_rect = QRectF(cx - pill_w / 2, baseline + 8, pill_w, pill_h)
        path = QPainterPath()
        path.addRoundedRect(pill_rect, pill_h / 2, pill_h / 2)
        painter.fillPath(path, soft_bg)

        painter.setFont(font_pill)
        painter.setPen(QColor(color))
        painter.drawText(pill_rect, Qt.AlignCenter, label)
