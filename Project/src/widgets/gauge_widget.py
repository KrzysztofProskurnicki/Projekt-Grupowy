"""Gauge Widget - półokrągły wskaźnik bezpieczeństwa z animacją."""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient, QFont, QPainterPath
import styles


class GaugeWidget(QWidget):
    """Wskaźnik półokrągły dla wyniku bezpieczeństwa."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 260)  # Minimalny rozmiar widgetu
        self._score = 0  # Docelowy wynik (0-100)
        self._animated_score = 0
    
    @pyqtProperty(int)
    def score(self):

        return self._animated_score
        
    @score.setter
    def score(self, value):
        """Setter dla property - aktualizuje wynik i odświeża widget"""
        self._animated_score = value
        self.update()
        
    def set_score(self, value: int):
        """Ustawia wynik i animuje do nowej wartości."""
        self._score = max(0, min(100, value))  # Ogranicz do 0-100
        self.anim = QPropertyAnimation(self, b"score")
        self.anim.setDuration(1500)  # 1.5 sekundy
        self.anim.setStartValue(self._animated_score)
        self.anim.setEndValue(self._score)
        self.anim.setEasingCurve(QEasingCurve.OutBack)
        self.anim.start()

    def paintEvent(self, event):
        """Rysuj wskaźnik gauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Antyaliasing dla gładkich krawędzi
        
        width = self.width()
        height = self.height()
        
        # Oblicz środek i promień
        center = QPointF(width / 2, height - 45)  # Środek u dołu
        radius = min(width / 2 - 40, height - 55)  # Zewnętrzny promień
        inner_radius = radius - 35  # Wewnętrzny promień (szerokość paska)
        
        # --- 1. Rysuj tło (szary półokrąg) ---
        path_bg = QPainterPath()
        # Zewnętrzny łuk (180° do 0°)
        path_bg.arcMoveTo(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 180)
        path_bg.arcTo(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 180, -180)
        # Wewnętrzny łuk
        path_bg.arcTo(center.x() - inner_radius, center.y() - inner_radius, 
                     inner_radius * 2, inner_radius * 2, 0, 180)
        path_bg.closeSubpath()
        
        painter.setPen(Qt.NoPen)  # Bez obramowania
        painter.setBrush(QColor(styles.HOVER_BG))  # Theme-aware tło
        painter.drawPath(path_bg)
        
        # Subtelne obramowanie
        pen_outline = QPen(QColor(255, 255, 255, 77), 1)
        painter.strokePath(path_bg, pen_outline)
        
        # --- 2. Kolorowy łuk ---
        angle_span = (self._animated_score / 100) * 180
        
        if angle_span > 0:
            path_val = QPainterPath()
            path_val.arcMoveTo(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 180)
            path_val.arcTo(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 180, -angle_span)
            path_val.arcTo(center.x() - inner_radius, center.y() - inner_radius, 
                          inner_radius * 2, inner_radius * 2, 180 - angle_span, angle_span)
            path_val.closeSubpath()
            
            # Wype?nienie gradientem
            gradient = QLinearGradient(center.x() - radius, center.y(), center.x() + radius, center.y())
            gradient.setColorAt(0.0, QColor("#ff453a")) 
            gradient.setColorAt(0.5, QColor("#ffd60a")) 
            gradient.setColorAt(1.0, QColor("#30d158")) 
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawPath(path_val)

            # Zewnętrzna poświata
            if self._animated_score >= 80: 
                glow_c = QColor("#30d158")
            elif self._animated_score >= 50: 
                glow_c = QColor("#ffd60a")
            else: 
                glow_c = QColor("#ff453a")
            glow_c.setAlpha(80)
            
            glow_rad = radius + 15
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow_c)
            path_outer_glow = QPainterPath()
            path_outer_glow.arcMoveTo(center.x() - glow_rad, center.y() - glow_rad, 
                                     glow_rad * 2, glow_rad * 2, 180)
            path_outer_glow.arcTo(center.x() - glow_rad, center.y() - glow_rad, 
                                 glow_rad * 2, glow_rad * 2, 180, -angle_span)
            path_outer_glow.arcTo(center.x() - inner_radius, center.y() - inner_radius, 
                                 inner_radius * 2, inner_radius * 2, 180 - angle_span, angle_span)
            path_outer_glow.closeSubpath()
            painter.drawPath(path_outer_glow)

        # --- 3. Wskazówka ---
        painter.save()
        painter.translate(center)
        rotation = 180 + angle_span
        painter.rotate(rotation)
        
        needle_len = inner_radius - 8
        needle_width = 6
        
        grad_needle = QLinearGradient(0, 0, needle_len, 0)
        grad_needle.setColorAt(0.0, QColor(255, 255, 255, 0))
        grad_needle.setColorAt(0.6, QColor(255, 255, 255, 0))
        grad_needle.setColorAt(1.0, QColor(255, 255, 255, 255))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad_needle))
        
        path_needle = QPainterPath()
        path_needle.addRoundedRect(0, -needle_width/2, needle_len, needle_width, 
                                  needle_width/2, needle_width/2)
        painter.drawPath(path_needle)
        painter.restore()

        # --- 4. Tekst wyniku ---
        font_score = QFont("Segoe UI", 32)
        font_score.setBold(False)
        painter.setFont(font_score)
        
        score_str = f"{int(self._animated_score)}%"
        rect_s = painter.fontMetrics().boundingRect(score_str)
        
        current_color = self.get_color_for_score(self._animated_score)
        color_shadow = QColor(current_color)
        color_shadow.setAlpha(100)
        
        painter.setPen(color_shadow)
        painter.drawText(int(center.x() - rect_s.width() / 2) + 2, 
                        int(center.y() - 10) + 2, score_str)
        
        painter.setPen(QColor(styles.TEXT_PRIMARY))
        painter.drawText(int(center.x() - rect_s.width() / 2), 
                        int(center.y() - 10), score_str)
        
        # --- 5. Etykieta statusu ---
        s = self._animated_score
        if s >= 90:    
            status, s_col = "EXCELLENT", "#30d158"
        elif s >= 75:  
            status, s_col = "GOOD", "#30d158"
        elif s >= 60:  
            status, s_col = "FAIR", "#ffd60a"
        elif s >= 40:  
            status, s_col = "POOR", "#ff453a"
        else:          
            status, s_col = "CRITICAL", "#ff453a"
        
        font_lbl = QFont("Segoe UI", 16)
        font_lbl.setWeight(QFont.DemiBold)
        font_lbl.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
        painter.setFont(font_lbl)
        
        c_status = QColor(s_col)
        c_status_glow = QColor(s_col)
        c_status_glow.setAlpha(100)
        
        rect_l = painter.fontMetrics().boundingRect(status)
        pos_x = int(center.x() - rect_l.width() / 2)
        pos_y = int(center.y() + 25)
        
        painter.setPen(c_status_glow)
        painter.drawText(pos_x, pos_y, status)
        
        painter.setPen(c_status)
        painter.drawText(pos_x, pos_y, status)

        # --- 6. Etykiety procentowe ---
        font_pct = QFont("Segoe UI", 10)
        font_pct.setBold(True)
        painter.setFont(font_pct)
        painter.setPen(QColor(styles.TEXT_SECONDARY))
        
        l_str = "0%"
        l_rect = painter.fontMetrics().boundingRect(l_str)
        painter.drawText(int(center.x() - radius - l_rect.width()/2 + 20), 
                        int(center.y() + 25), l_str)
        
        r_str = "100%"
        r_rect = painter.fontMetrics().boundingRect(r_str)
        painter.drawText(int(center.x() + radius - r_rect.width()/2 - 20), 
                        int(center.y() + 25), r_str)
        
        m_str = "50%"
        m_rect = painter.fontMetrics().boundingRect(m_str)
        painter.drawText(int(center.x() - m_rect.width()/2), 
                        int(center.y() - radius + 60), m_str)

    def get_color_for_score(self, score):
        """Pobierz kolor na podstawie wartości wyniku"""
        if score < 40: 
            return QColor("#ff453a")
        if score < 75: 
            return QColor("#ffd60a")
        return QColor("#30d158")
