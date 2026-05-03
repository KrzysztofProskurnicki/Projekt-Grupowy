from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QScrollArea, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QRectF, QPoint, QPointF, QTimer, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient, QConicalGradient, QFont, QPainterPath, QRadialGradient
import zxcvbn
import math
from styles import *

class GaugeWidget(QWidget):
    """Custom Semicircle Gauge Widget for Security Score (High Fidelity / V2.0 JSON Strict)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 260) # Slightly larger for padding/glow
        self._score = 0
        self._animated_score = 0
    
    @pyqtProperty(int)
    def score(self):
        return self._animated_score
        
    @score.setter
    def score(self, value):
        self._animated_score = value
        self.update()
        
    def set_score(self, value):
        """Set target score and animate to it."""
        self._score = max(0, min(100, value))
        self.anim = QPropertyAnimation(self, b"score")
        self.anim.setDuration(1500) # 1500ms per JSON
        self.anim.setStartValue(self._animated_score)
        self.anim.setEndValue(self._score)
        self.anim.setEasingCurve(QEasingCurve.OutBack) # Overshoot effect per JSON
        self.anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Center & Radius
        center = QPointF(width / 2, height - 45)
        radius = min(width / 2 - 40, height - 55)
        inner_radius = radius - 35
        
        # --- 1. Background Track (Dark + Outline + Glow) ---
        path_bg = QPainterPath()
        # Outer arc (180 to 0)
        path_bg.arcMoveTo(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 180)
        path_bg.arcTo(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 180, -180)
        # Inner arc reverse
        path_bg.arcTo(center.x() - inner_radius, center.y() - inner_radius, inner_radius * 2, inner_radius * 2, 0, 180)
        path_bg.closeSubpath()
        
        # Fill Track
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#2c2c2e"))
        painter.drawPath(path_bg)
        
        # Track Outline (White, 30% Opacity)
        pen_outline = QPen(QColor(255, 255, 255, 77), 1) # 77/255 ~= 30%
        painter.strokePath(path_bg, pen_outline)
        
        # --- 2. Colored Arc (Gradient + Glow) ---
        angle_span = (self._animated_score / 100) * 180
        
        if angle_span > 0:
            # Value Path
            path_val = QPainterPath()
            path_val.arcMoveTo(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 180)
            path_val.arcTo(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 180, -angle_span)
            path_val.arcTo(center.x() - inner_radius, center.y() - inner_radius, inner_radius * 2, inner_radius * 2, 180 - angle_span, angle_span)
            path_val.closeSubpath()
            
            # Gradient Fill (Red -> Yellow -> Green)
            gradient = QLinearGradient(center.x() - radius, center.y(), center.x() + radius, center.y())
            gradient.setColorAt(0.0, QColor("#ff453a")) 
            gradient.setColorAt(0.5, QColor("#ffd60a")) 
            gradient.setColorAt(1.0, QColor("#30d158")) 
            
            # Draw Value Arc
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawPath(path_val)
            
            # Outer Glow for Value Arc
            # Color logic
            if self._animated_score >= 80: glow_c = QColor("#30d158")
            elif self._animated_score >= 50: glow_c = QColor("#ffd60a")
            else: glow_c = QColor("#ff453a")
            glow_c.setAlpha(80) # Stronger glow
            
            path_glow = QPainterPath()
            glow_rad = radius + 15
            path_glow.arcMoveTo(center.x() - glow_rad, center.y() - glow_rad, glow_rad * 2, glow_rad * 2, 180)
            path_glow.arcTo(center.x() - glow_rad, center.y() - glow_rad, glow_rad * 2, glow_rad * 2, 180, -angle_span)
            # Connect to center approximately or just close? 
            # To make a nice glow, let's just stroke a wide pen of the arc centerline
            arc_center_rad = (radius + inner_radius) / 2
            path_stroke_glow = QPainterPath()
            path_stroke_glow.arcMoveTo(center.x() - arc_center_rad, center.y() - arc_center_rad, arc_center_rad * 2, arc_center_rad * 2, 180)
            path_stroke_glow.arcTo(center.x() - arc_center_rad, center.y() - arc_center_rad, arc_center_rad * 2, arc_center_rad * 2, 180, -angle_span)
            
            pen_glow = QPen(glow_c, (radius - inner_radius) + 20)
            pen_glow.setCapStyle(Qt.FlatCap)
            painter.setPen(pen_glow)
            painter.setBrush(Qt.NoBrush)
            # Clip to outside of inner radius to avoid internal mess?
            # Actually, standard glow drawing is fine.
            # Let's stick to the previous 'filled larger arc' method which gave good results, just adjusted opacity
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow_c)
            path_outer_glow = QPainterPath()
            path_outer_glow.arcMoveTo(center.x() - glow_rad, center.y() - glow_rad, glow_rad * 2, glow_rad * 2, 180)
            path_outer_glow.arcTo(center.x() - glow_rad, center.y() - glow_rad, glow_rad * 2, glow_rad * 2, 180, -angle_span)
            path_outer_glow.arcTo(center.x() - inner_radius, center.y() - inner_radius, inner_radius * 2, inner_radius * 2, 180 - angle_span, angle_span)
            path_outer_glow.closeSubpath()
            painter.drawPath(path_outer_glow)

        # --- 3. Scale Ticks (Decorations) ---
        # Removed per user request ("usuń te jakby linie takie podobne do zegara")
        pass

        # --- 4. Needle (Gradient: Transparent -> White) ---
        painter.save()
        painter.translate(center)
        rotation = 180 + angle_span
        painter.rotate(rotation)
        
        needle_len = inner_radius - 8
        needle_width = 6 # Slightly thicker for gradient visibility
        
        # Define Gradient: Pivot (0,0) -> Tip (needle_len, 0)
        grad_needle = QLinearGradient(0, 0, needle_len, 0)
        grad_needle.setColorAt(0.0, QColor(255, 255, 255, 0)) # Alpha 0
        grad_needle.setColorAt(0.6, QColor(255, 255, 255, 0)) # Delayed start
        grad_needle.setColorAt(1.0, QColor(255, 255, 255, 255)) # Solid White
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad_needle))
        
        # Draw Needle as Rounded Rect or Tapered? JSON says Rounded Rect / Tapered.
        # Let's draw a tapered polygon for visual effect
        # Or Just rounded rect as per previous code but with gradient
        path_needle = QPainterPath()
        # Start at 0,0
        path_needle.addRoundedRect(0, -needle_width/2, needle_len, needle_width, needle_width/2, needle_width/2)
        
        painter.drawPath(path_needle)
        painter.restore()

        # --- 5. Main Score Text (With Shadow/Glow) ---
        # Score Value

        font_score = QFont("Segoe UI", 32)
        font_score.setBold(False)
        painter.setFont(font_score)
        
        score_str = f"{int(self._animated_score)}%"
        rect_s = painter.fontMetrics().boundingRect(score_str)
        
        # Text Glow/Shadow
        current_color = self.get_color_for_score(self._animated_score)
        color_shadow = QColor(current_color)
        color_shadow.setAlpha(100)
        
        painter.setPen(color_shadow)
        painter.drawText(int(center.x() - rect_s.width() / 2) + 2, int(center.y() - 10) + 2, score_str)
        
        painter.setPen(QColor("#ffffff"))
        painter.drawText(int(center.x() - rect_s.width() / 2), int(center.y() - 10), score_str)
        
        # --- 6. Status Label Text ---
        # ... (Status Logic)
        s = self._animated_score
        if s >= 90:    status, s_col = "EXCELLENT", "#30d158"
        elif s >= 75:  status, s_col = "GOOD", "#30d158"
        elif s >= 60:  status, s_col = "FAIR", "#ffd60a"
        elif s >= 40:  status, s_col = "POOR", "#ff453a"
        else:          status, s_col = "CRITICAL", "#ff453a"
        
        font_lbl = QFont("Segoe UI", 16)
        font_lbl.setWeight(QFont.DemiBold)
        font_lbl.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
        painter.setFont(font_lbl)
        
        c_status = QColor(s_col)
        c_status_glow = QColor(s_col)
        c_status_glow.setAlpha(100)
        
        rect_l = painter.fontMetrics().boundingRect(status)
        pos_x = int(center.x() - rect_l.width() / 2)
        pos_y = int(center.y() + 25) # Moved higher closer to score
        
        painter.setPen(c_status_glow)
        painter.drawText(pos_x, pos_y, status)
        
        painter.setPen(c_status)
        painter.drawText(pos_x, pos_y, status)

        # --- 7. Percentage Labels (0%, 50%, 100%) ---
        font_pct = QFont("Segoe UI", 10)
        font_pct.setBold(True)
        painter.setFont(font_pct)
        painter.setPen(QColor("#98989d"))
        
        # 0% (Shifted Right)
        l_str = "0%"
        l_rect = painter.fontMetrics().boundingRect(l_str)
        # Standard: center.x - radius. Move right => Add.
        painter.drawText(int(center.x() - radius - l_rect.width()/2 + 20), int(center.y() + 25), l_str)
        
        # 100% (Shifted Left)
        r_str = "100%"
        r_rect = painter.fontMetrics().boundingRect(r_str)
        # Standard: center.x + radius. Move left => Subtract.
        painter.drawText(int(center.x() + radius - r_rect.width()/2 - 20), int(center.y() + 25), r_str)
        
        # 50% (Lowered)
        m_str = "50%"
        m_rect = painter.fontMetrics().boundingRect(m_str)
        # Lower means increasing Y relative to top. 
        # Previous: center.y - radius + 35. 
        # User wants "50% lower" (ambiguous, assume deeper down).
        painter.drawText(int(center.x() - m_rect.width()/2), int(center.y() - radius + 60), m_str)

    def get_color_for_score(self, score):
        if score < 40: return QColor("#ff453a")
        if score < 75: return QColor("#ffd60a")
        return QColor("#30d158")


class VaultStatusBar(QWidget):
    """Stacked Horizontal Bar (Option C Style - Neon/Modern)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.stats = {"strong": 0, "weak": 0, "reused": 0, "old": 0, "total": 1}
        
    def set_stats(self, strong, weak, total):
        # Demo logic for extra segments
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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        bar_h = 24
        y_bar = 20
        w_total = rect.width()
        
        # --- 1. Background Track ---
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#2c2c2e"))
        painter.drawRoundedRect(0, y_bar, w_total, bar_h, 12, 12)
        
        # Calculate widths
        total = self.stats["total"]
        if total == 0: return

        # Segments data: (Value, Color, Label)
        segments = [
            (self.stats["strong"], QColor(COLOR_GREEN), "Strong"),
            (self.stats["weak"], QColor(COLOR_RED), "Weak"),
            (self.stats["reused"], QColor(COLOR_YELLOW), "Reused"),
            (self.stats["old"], QColor(COLOR_BLUE), "Old")
        ]
        
        current_x = 0
        
        # --- 2. Draw Segments ---
        for val, color, label in segments:
            if val > 0:
                seg_w = (val / total) * w_total
                
                # Draw Glow (Neon effect)
                color_glow = QColor(color)
                color_glow.setAlpha(40)
                painter.setBrush(color_glow)
                painter.drawRoundedRect(int(current_x), y_bar - 2, int(seg_w), bar_h + 4, 4, 4)
                
                # Draw Main Bar segment
                painter.setBrush(color)
                draw_w = max(2, seg_w - 2)
                painter.drawRoundedRect(int(current_x), y_bar, int(draw_w), bar_h, 4, 4)
                
                current_x += seg_w
        
        # --- 3. Legend Below ---
        y_leg = y_bar + bar_h + 25
        x_leg = 0
        painter.setFont(QFont("Segoe UI", 12))
        
        for val, color, label in segments:
            if val >= 0: # Show all legends or only > 0? Let's show all if total > 0 for consistency
                # Dot
                painter.setBrush(color)
                painter.drawEllipse(int(x_leg), int(y_leg) - 8, 8, 8)
                
                # Text
                label_full = f"{label} ({int((val/total)*100)}%)"
                painter.setPen(QColor("#b0b0b5"))
                painter.drawText(int(x_leg) + 15, int(y_leg), label_full)
                
                # Advance
                w_text = painter.fontMetrics().horizontalAdvance(label_full)
                x_leg += w_text + 35 # Gap

class SecurityView(QWidget):
    """Security statistics dashboard."""
    
    def __init__(self, back_callback, detail_callback):
        super().__init__()
        self.back_callback = back_callback
        self.detail_callback = detail_callback
        self.passwords_data = []
        self.init_ui()
    
    def create_section_frame(self):
        frame = QFrame()
        frame.setStyleSheet(CARD_STYLE)
        return frame
    
    def init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background-color: {DARK_BG}; }} QScrollBar:vertical {{ width: 0px; }}")
        
        content = QWidget()
        content.setStyleSheet(f"background-color: {DARK_BG};")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header
        title = QLabel("🛡️ Security Dashboard")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {TEXT_PRIMARY}; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # --- Top Section: 2 Columns (Stats Left | Gauge Right) ---
        top_section = QHBoxLayout()
        top_section.setSpacing(30)
        
        # 1. Left: Stats Grid (2x2)
        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(15)
        
        row1 = QHBoxLayout()
        self.total_card = self.create_stat_card("Total Accounts", "0", COLOR_BLUE, "🔑")
        self.fav_card = self.create_stat_card("Favorites", "0", COLOR_YELLOW, "⭐")
        row1.addWidget(self.total_card)
        row1.addWidget(self.fav_card)
        
        row2 = QHBoxLayout()
        self.strong_card = self.create_stat_card("Strong Passwords", "0", COLOR_GREEN, "✓")
        self.weak_card = self.create_stat_card("Weak Passwords", "0", COLOR_RED, "⚠️")
        row2.addWidget(self.strong_card)
        row2.addWidget(self.weak_card)
        
        stats_layout.addLayout(row1)
        stats_layout.addLayout(row2)
        
        top_section.addWidget(stats_container, stretch=3)
        
        # 2. Right: Gauge (Smaller, Centered)
        chart_frame = self.create_section_frame()
        chart_frame.setMaximumHeight(300)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(20, 15, 20, 15)

        gauge_title = QLabel("Security Score")
        gauge_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_PRIMARY}; margin-bottom: 5px;")
        chart_layout.addWidget(gauge_title)
        
        self.gauge = GaugeWidget()
        chart_layout.addWidget(self.gauge, 0, Qt.AlignCenter)
        
        top_section.addWidget(chart_frame, stretch=2)
        layout.addLayout(top_section)
        
        # --- Middle Section: Vault Bar (Full Width, Option C Style) ---
        bar_frame = self.create_section_frame()
        bar_layout = QVBoxLayout(bar_frame)
        bar_layout.setContentsMargins(30, 25, 30, 30)
        
        bar_title = QLabel("Vault Overview")
        bar_title.setStyleSheet("font-size: 16px; font-weight: bold; color: " + TEXT_PRIMARY + "; margin-bottom: 15px;")
        bar_layout.addWidget(bar_title)
        
        self.vault_bar = VaultStatusBar()
        bar_layout.addWidget(self.vault_bar)
        
        layout.addWidget(bar_frame)
        
        # --- Bottom Section: Weak Passwords + Tips ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        
        # Weak list
        weak_frame = self.create_section_frame()
        weak_layout = QVBoxLayout(weak_frame)
        weak_layout.setContentsMargins(20, 20, 20, 20)
        
        weak_head = QLabel("⚠️ Weak Passwords")
        weak_head.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLOR_RED};")
        weak_layout.addWidget(weak_head)
        
        self.weak_list_widget = QWidget()
        self.weak_list_widget.setStyleSheet("background: transparent;")
        self.weak_list_layout = QVBoxLayout(self.weak_list_widget)
        self.weak_list_layout.setContentsMargins(0, 0, 0, 0)
        self.weak_list_layout.setSpacing(8)
        weak_layout.addWidget(self.weak_list_widget)
        weak_layout.addStretch()
        
        bottom_row.addWidget(weak_frame)
        
        # Tips
        tips_frame = self.create_section_frame()
        tips_layout = QVBoxLayout(tips_frame)
        tips_layout.setContentsMargins(20, 20, 20, 20)
        tips_head = QLabel("💡 Security Tips")
        tips_head.setStyleSheet(SECTION_TITLE_STYLE)
        tips_layout.addWidget(tips_head)
        
        for tip in ["• Enable 2FA on all financial accounts", "• Use unique passwords everywhere", "• Rotate critical passwords yearly", "• Use a password manager (like this one!)"]:
            t = QLabel(tip)
            t.setStyleSheet(f"font-size: 14px; color: {TEXT_SECONDARY}; padding: 4px 0;")
            tips_layout.addWidget(t)
        tips_layout.addStretch()
        
        bottom_row.addWidget(tips_frame)
        layout.addLayout(bottom_row)
        
        # Table
        table_frame = self.create_section_frame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_title = QLabel("📋 All Passwords")
        table_title.setStyleSheet(SECTION_TITLE_STYLE)
        table_layout.addWidget(table_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.cellDoubleClicked.connect(self.on_table_double_clicked)
        self.table.setHorizontalHeaderLabels(["Name", "Email", "Status", "Crack Time", "Favorite"])
        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: {DARK_BG}; color: {TEXT_PRIMARY}; border: none; }}
            QTableWidget::item {{ padding: 10px; }}
            QHeaderView::section {{ background-color: {CARD_BG}; color: {TEXT_PRIMARY}; padding: 10px; border: none; font-weight: bold; border-bottom: 2px solid #38383a; }}
            QTableWidget::item:selected {{ background-color: {COLOR_BLUE}; }}
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        table_layout.addWidget(self.table)
        
        layout.addWidget(table_frame)
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def create_stat_card(self, title, value, color, icon):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background-color: {CARD_BG}; border-radius: 12px; border-left: 4px solid {color}; }}")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        
        top = QHBoxLayout()
        ico = QLabel(icon)
        ico.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        top.addWidget(ico)
        top.addStretch()
        val = QLabel(value)
        val.setObjectName("value")
        val.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color}; border: none; background: transparent;")
        top.addWidget(val)
        layout.addLayout(top)
        
        tit = QLabel(title)
        tit.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY}; border: none; background: transparent;")
        layout.addWidget(tit)
        return card

    def get_crack_time(self, password):
        try:
            return zxcvbn.zxcvbn(password)['crack_times_display']['offline_slow_hashing_1e4_per_second']
        except:
             return "Unknown"

    def calculate_security_score(self, strong, weak, total):
        if total == 0: return 0
        return int(max(0, min(100, (strong/total * 100) - (weak * 5))))

    def update_stats(self, passwords_data):
        self.passwords_data = passwords_data
        total = len(passwords_data)
        weak = sum(1 for p in passwords_data if p.get('weak_password', False))
        strong = total - weak
        favorites = sum(1 for p in passwords_data if p.get('favorite', False))
        
        self.total_card.findChild(QLabel, "value").setText(str(total))
        self.weak_card.findChild(QLabel, "value").setText(str(weak))
        self.strong_card.findChild(QLabel, "value").setText(str(strong))
        self.fav_card.findChild(QLabel, "value").setText(str(favorites))
        
        score = self.calculate_security_score(strong, weak, total)
        self.gauge.set_score(score)
        self.vault_bar.set_stats(strong, weak, total)
        
        # Update weak list
        # ... existing logic ...
        while self.weak_list_layout.count():
            w = self.weak_list_layout.takeAt(0).widget()
            if w: w.deleteLater()
            
        weak_accs = [p for p in passwords_data if p.get('weak_password', False)]
        if weak_accs:
            for acc in weak_accs:
                f = QFrame()
                l = QHBoxLayout(f)
                l.setContentsMargins(0, 0, 0, 0)
                l.addWidget(QLabel("⚠️", objectName="icon"))
                l.addWidget(QLabel(acc['name'], styleSheet=f"color:{TEXT_PRIMARY}; font-weight:500;"))
                l.addWidget(QLabel(f"({acc['email']})", styleSheet=f"color:{TEXT_SECONDARY};"))
                l.addStretch()
                self.weak_list_layout.addWidget(f)
        else:
            self.weak_list_layout.addWidget(QLabel("Avalanche Secure! 🎉", styleSheet=f"color:{COLOR_GREEN}; font-style:italic;"))
            
        # Table
        self.table.setRowCount(total)
        for i, p in enumerate(passwords_data):
            self.table.setItem(i, 0, QTableWidgetItem(p['name']))
            self.table.setItem(i, 1, QTableWidgetItem(p['email']))
            s_text = "⚠️ Weak" if p.get('weak_password') else "✓ Strong"
            s_item = QTableWidgetItem(s_text)
            s_item.setForeground(QColor(COLOR_RED if p.get('weak_password') else COLOR_GREEN))
            self.table.setItem(i, 2, s_item)

            self.table.setItem(i, 3, QTableWidgetItem(self.get_crack_time(p.get('password', ''))))
            
            fav = "⭐" if p.get('favorite') else ""
            f_item = QTableWidgetItem(fav)
            f_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, f_item)
            
        self.table.resizeRowsToContents()
        hh = self.table.horizontalHeader().height()
        rh = sum(self.table.rowHeight(i) for i in range(total))
        self.table.setFixedHeight(hh + rh + 20)

    def on_table_double_clicked(self, row, column):
        if 0 <= row < len(self.passwords_data):
            e = self.passwords_data[row]
            self.detail_callback(e['id'])
