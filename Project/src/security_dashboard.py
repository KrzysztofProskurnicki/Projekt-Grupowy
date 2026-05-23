"""Security Dashboard View - Displays security statistics and analysis."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QScrollArea, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from widgets.gauge_widget import GaugeWidget
from widgets.vault_status_bar import VaultStatusBar
from services.security_service import SecurityService
from styles import *



class SecurityView(QWidget):
    """Security statistics dashboard."""
    
    def __init__(self, back_callback, detail_callback):
        """Initialize security view.
        
        Args:
            back_callback: Callback to return to previous view.
            detail_callback: Callback to navigate to detail view.
        """
        super().__init__()
        self.back_callback = back_callback
        self.detail_callback = detail_callback
        self.passwords_data = []
        self.security_service = SecurityService()
        self.init_ui()

    
    def create_section_frame(self):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 12px;")
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
        card.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 12px; border-left: 4px solid " + color + ";")
        
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
        """Get crack time using security service."""
        return self.security_service.get_crack_time(password)

    def calculate_security_score(self, strong, weak, total):
        """Calculate security score - delegate to service (deprecated, use service directly)."""
        if total == 0: 
            return 0
        return int(max(0, min(100, (strong/total * 100) - (weak * 5))))



    def update_stats(self, passwords_data):
        """Update all statistics and charts with password data."""
        self.passwords_data = passwords_data
        
        # Get stats using security service
        stats = self.security_service.get_security_stats(passwords_data)
        
        self.total_card.findChild(QLabel, "value").setText(str( stats['total']))
        self.weak_card.findChild(QLabel, "value").setText(str(stats['weak']))
        self.strong_card.findChild(QLabel, "value").setText(str(stats['strong']))
        self.fav_card.findChild(QLabel, "value").setText(str(stats['favorites']))
        
        score = self.security_service.calculate_security_score(passwords_data)
        self.gauge.set_score(score)
        self.vault_bar.set_stats(stats['strong'], stats['weak'], stats['total'])

        
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
        total = stats['total']
        self.table.setRowCount(total)
        for i, p in enumerate(passwords_data):
            self.table.setItem(i, 0, QTableWidgetItem(p['name']))
            self.table.setItem(i, 1, QTableWidgetItem(p['email']))
            s_text = "⚠️ Weak" if p.get('weak_password') else "✓ Strong"
            s_item = QTableWidgetItem(s_text)
            s_item.setForeground(QColor(COLOR_RED if p.get('weak_password') else COLOR_GREEN))
            self.table.setItem(i, 2, s_item)

            sim_pwd = "password" if p.get('weak_password') else "S3cur3P@ss!"
            self.table.setItem(i, 3, QTableWidgetItem(self.get_crack_time(sim_pwd)))
            
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
            self.detail_callback(e['name'], e['email'], e['color'], e['name'][0], e.get('favorite', False))
