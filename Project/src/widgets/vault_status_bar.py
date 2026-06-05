"""Widget paska statusu sejfu - poziomy skumulowany pasek kategorii haseł."""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QFont
from styles import COLOR_GREEN, COLOR_RED, COLOR_YELLOW, COLOR_BLUE
import styles


class VaultStatusBar(QWidget):
    
    def __init__(self, parent=None):

        super().__init__(parent)
        self.setMinimumHeight(100)
        self.stats = {"strong": 0, "weak": 0, "reused": 0, "old": 0, "total": 1}
        
    def set_stats(self, strong: int, weak: int, total: int):
        """Ustaw statystyki paska.
        
        Argumenty:
            strong: Liczba silnych haseł
            weak: Liczba słabych haseł
            total: Liczba haseł.
        """
        # Logika demonstracyjna dla dodatkowych segmentów
        reused = int(weak * 0.3)
        old = int(weak * 0.2)
        
        self.stats = {
            "strong": strong,
            "weak": weak - reused - old,
            "reused": reused,
            "old": old,
            "total": max(1, total)
        }
        self.update()
        
    def paintEvent(self, event):
        """Narysuj pasek statusu sejfu"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        bar_h = 24
        y_bar = 20
        w_total = rect.width()
        
        # --- 1. Ścieżka tła ---
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(styles.HOVER_BG))
        painter.drawRoundedRect(0, y_bar, w_total, bar_h, 12, 12)
        
        # Oblicz szerokości
        total = self.stats["total"]
        if total == 0: 
            return

        # Dane segment?w: (wartości, kolor, etykieta)
        segments = [
            (self.stats["strong"], QColor(COLOR_GREEN), "Strong"),
            (self.stats["weak"], QColor(COLOR_RED), "Weak"),
            (self.stats["reused"], QColor(COLOR_YELLOW), "Reused"),
            (self.stats["old"], QColor(COLOR_BLUE), "Old")
        ]
        
        current_x = 0
        
        # --- 2. Rysowanie segmentu ---
        for val, color, label in segments:
            if val > 0:
                seg_w = (val / total) * w_total
                
                # Rysuje poświatę (efekt neonowy)
                color_glow = QColor(color)
                color_glow.setAlpha(40)
                painter.setBrush(color_glow)
                painter.drawRoundedRect(int(current_x), y_bar - 2, int(seg_w), bar_h + 4, 4, 4)
                
                # Rysuje główny segment paska
                painter.setBrush(color)
                draw_w = max(2, seg_w - 2)
                painter.drawRoundedRect(int(current_x), y_bar, int(draw_w), bar_h, 4, 4)
                
                current_x += seg_w
        
        # --- 3. Legenda ---
        y_leg = y_bar + bar_h + 25
        x_leg = 0
        painter.setFont(QFont("Segoe UI", 12))
        
        for val, color, label in segments:
            if val >= 0:
                # Kropka
                painter.setBrush(color)
                painter.drawEllipse(int(x_leg), int(y_leg) - 8, 8, 8)
                
                # Tekst
                label_full = f"{label} ({int((val/total)*100)}%)"
                painter.setPen(QColor(styles.TEXT_SECONDARY))
                painter.drawText(int(x_leg) + 15, int(y_leg), label_full)
                
                # Przesunięcie
                w_text = painter.fontMetrics().horizontalAdvance(label_full)
                x_leg += w_text + 35
