"""Widok panelu bezpieczeństwa - wyświetla statystyki i analizę bezpieczeństwa."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QScrollArea, QTableWidget, QTableWidgetItem, 
                             QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from widgets.gauge_widget import GaugeWidget
from widgets.vault_status_bar import VaultStatusBar
from widgets.icons import section_header, icon_label, tinted_pixmap
from services.security_service import SecurityService
import styles



class SecurityView(QWidget):
    """Panel statystyk bezpieczeństwa."""
    
    def __init__(self, back_callback, detail_callback):
        """Inicjalizuj widok bezpieczeństwa.
        
        Argumenty:
            back_callback: Funkcja powrotu do poprzedniego widoku.
            detail_callback: Funkcja przejścia do widoku szczegółów.
        """
        super().__init__()
        self.back_callback = back_callback
        self.detail_callback = detail_callback
        self.passwords_data = []
        self.security_service = SecurityService()
        self.init_ui()

    
    def create_section_frame(self):
        frame = QFrame()
        frame.setObjectName("sectionCard")
        frame.setStyleSheet(
            f"QFrame#sectionCard {{ background-color: {styles.CARD_BG};"
            f" border: 1px solid {styles.HAIRLINE}; border-radius: 12px; }}"
        )
        return frame
    
    def init_ui(self):
        old = self.layout()
        if old is not None:
            QWidget().setLayout(old)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background-color: {styles.DARK_BG}; }} QScrollBar:vertical {{ width: 0px; }}")
        
        content = QWidget()
        content.setObjectName("securityContent")
        # Scope'owane tło - goły "background-color" kaskadowałby na etykiety
        content.setStyleSheet(f"QWidget#securityContent {{ background-color: {styles.DARK_BG}; }}")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Ogranicz szerokość treści jak we wzorcu (maxWidth 1080)
        inner = QWidget()
        inner.setObjectName("securityInner")
        inner.setStyleSheet("QWidget#securityInner { background: transparent; }")
        inner.setFixedWidth(1080)
        layout_outer = layout
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)
        layout_outer.addWidget(inner, 0, Qt.AlignHCenter | Qt.AlignTop)

        title = section_header(
            "shield-check", "Security",
            styles.COLOR_BLUE, styles.TEXT_PRIMARY, icon_size=26, font_px=28,
        )
        layout.addWidget(title)

        top_section = QHBoxLayout()
        top_section.setSpacing(16)

        # 1. Lewa strona: siatka statystyk (2x2)
        stats_container = QWidget()
        stats_container.setStyleSheet("background: transparent; border: none;")
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(16)

        row1 = QHBoxLayout()
        row1.setSpacing(16)
        self.total_card = self.create_stat_card("Total Accounts", "0", styles.COLOR_BLUE, styles.BLUE_SOFT, "key-round")
        self.fav_card = self.create_stat_card("Favorites", "0", styles.COLOR_YELLOW, styles.YELLOW_SOFT, "star")
        row1.addWidget(self.total_card)
        row1.addWidget(self.fav_card)

        row2 = QHBoxLayout()
        row2.setSpacing(16)
        self.strong_card = self.create_stat_card("Strong Passwords", "0", styles.COLOR_GREEN, styles.GREEN_SOFT, "shield-check")
        self.weak_card = self.create_stat_card("Weak Passwords", "0", styles.COLOR_RED, styles.RED_SOFT, "triangle-alert")
        row2.addWidget(self.strong_card)
        row2.addWidget(self.weak_card)
        
        stats_layout.addLayout(row1)
        stats_layout.addLayout(row2)
        
        top_section.addWidget(stats_container, stretch=3)
        
        # 2. Prawa strona: wskaźnik
        chart_frame = self.create_section_frame()
        chart_frame.setMaximumHeight(300)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(20, 15, 20, 15)

        gauge_title = QLabel("Security Score")
        gauge_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {styles.TEXT_PRIMARY}; background: transparent; border: none; margin-bottom: 5px;")
        chart_layout.addWidget(gauge_title)
        
        self.gauge = GaugeWidget()
        chart_layout.addWidget(self.gauge, 0, Qt.AlignCenter)
        
        top_section.addWidget(chart_frame, stretch=2)
        layout.addLayout(top_section)
        
        # --- Środkowa sekcja: pasek sejfu ---
        bar_frame = self.create_section_frame()
        bar_layout = QVBoxLayout(bar_frame)
        bar_layout.setContentsMargins(30, 25, 30, 30)
        
        bar_title = QLabel("Vault Overview")
        bar_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {styles.TEXT_PRIMARY}; background: transparent; border: none; margin-bottom: 15px;")
        bar_layout.addWidget(bar_title)
        
        self.vault_bar = VaultStatusBar()
        bar_layout.addWidget(self.vault_bar)
        
        layout.addWidget(bar_frame)
        
        # --- Dolna sekcja: słabe hasła + wskazówki ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        
        # Lista słabych haseł
        weak_frame = self.create_section_frame()
        weak_layout = QVBoxLayout(weak_frame)
        weak_layout.setContentsMargins(20, 20, 20, 20)
        
        weak_head = section_header(
            "triangle-alert", "Needs Attention",
            styles.COLOR_RED, styles.TEXT_PRIMARY, icon_size=18, font_px=17,
        )
        weak_layout.addWidget(weak_head)
        
        self.weak_list_widget = QWidget()
        self.weak_list_widget.setStyleSheet("background: transparent;")
        self.weak_list_layout = QVBoxLayout(self.weak_list_widget)
        self.weak_list_layout.setContentsMargins(0, 0, 0, 0)
        self.weak_list_layout.setSpacing(8)
        weak_layout.addWidget(self.weak_list_widget)
        weak_layout.addStretch()
        
        bottom_row.addWidget(weak_frame)
        
        # Wskazówki
        tips_frame = self.create_section_frame()
        tips_layout = QVBoxLayout(tips_frame)
        tips_layout.setContentsMargins(20, 20, 20, 20)
        tips_head = section_header(
            "lightbulb", "Security Tips",
            styles.COLOR_YELLOW, styles.TEXT_PRIMARY, icon_size=18, font_px=17,
        )
        tips_layout.addWidget(tips_head)

        tips = [
            "Enable two-factor authentication on financial and email accounts.",
            "Use a unique password for every account.",
            "Rotate critical passwords at least once a year.",
            "Never reuse your master password anywhere else.",
        ]
        for tip in tips:
            row = QHBoxLayout()
            row.setSpacing(10)
            row.addWidget(icon_label("check", styles.COLOR_GREEN, 16), 0, Qt.AlignTop)
            t = QLabel(tip)
            t.setWordWrap(True)
            t.setStyleSheet(f"font-size: 13px; color: {styles.TEXT_SECONDARY}; border: none; background: transparent;")
            row.addWidget(t, 1)
            tips_layout.addLayout(row)
        tips_layout.addStretch()
        
        bottom_row.addWidget(tips_frame)
        layout.addLayout(bottom_row)
        
        # Tabela
        table_frame = self.create_section_frame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_title = section_header(
            "list", "All Passwords",
            styles.TEXT_SECONDARY, styles.TEXT_PRIMARY, icon_size=18, font_px=16,
        )
        table_layout.addWidget(table_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.cellDoubleClicked.connect(self.on_table_double_clicked)
        self.table.setHorizontalHeaderLabels(["Name", "Email", "Status", "Crack Time", "Favorite"])
        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: {styles.DARK_BG}; color: {styles.TEXT_PRIMARY}; border: none; }}
            QTableWidget::item {{ padding: 10px; }}
            QHeaderView::section {{ background-color: {styles.CARD_BG}; color: {styles.TEXT_PRIMARY}; padding: 10px; border: none; font-weight: bold; border-bottom: 2px solid {styles.BORDER_COLOR}; }}
            QTableWidget::item:selected {{ background-color: {styles.COLOR_BLUE}; }}
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        table_layout.addWidget(self.table)
        
        layout.addWidget(table_frame)
        
        scroll.setWidget(content)
        
        main_layout.addWidget(scroll)

    def refresh_theme(self):
        saved_data = list(self.passwords_data)
        self.init_ui()
        if saved_data:
            self.update_stats(saved_data)

    def create_stat_card(self, title, value, color, soft_bg, icon):
        """StatTile wg wzorca: tintowany chip ikony + liczba i etykieta obok."""
        card = QFrame()
        card.setObjectName("statTile")
        card.setStyleSheet(
            f"QFrame#statTile {{ background-color: {styles.CARD_BG};"
            f" border: 1px solid {styles.HAIRLINE}; border-radius: 12px; }}"
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        chip = QLabel()
        chip.setFixedSize(44, 44)
        chip.setAlignment(Qt.AlignCenter)
        chip.setPixmap(tinted_pixmap(icon, color, 20))
        chip.setStyleSheet(f"background-color: {soft_bg}; border-radius: 8px; border: none;")
        layout.addWidget(chip)

        col = QVBoxLayout()
        col.setSpacing(2)
        val = QLabel(value)
        val.setObjectName("value")
        val.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {styles.TEXT_PRIMARY}; border: none; background: transparent;")
        tit = QLabel(title)
        tit.setStyleSheet(f"font-size: 13px; color: {styles.TEXT_SECONDARY}; border: none; background: transparent;")
        col.addWidget(val)
        col.addWidget(tit)
        layout.addLayout(col)
        layout.addStretch()
        return card


    def get_crack_time(self, password):
        """Pobierz czas złamania hasła przez serwis bezpieczeństwa."""
        return self.security_service.get_crack_time(password)

    def calculate_security_score(self, strong, weak, total):
        """Oblicza wynik bezpieczeństwa"""
        if total == 0: 
            return 0
        return int(max(0, min(100, (strong/total * 100) - (weak * 5))))



    def update_stats(self, passwords_data):
        """Zaktualizuj wszystkie statystyki i wykresy danymi haseł"""
        self.passwords_data = passwords_data
        
        # Pobierz statystyki przez serwis bezpieczeństwa
        stats = self.security_service.get_security_stats(passwords_data)
        
        self.total_card.findChild(QLabel, "value").setText(str( stats['total']))
        self.weak_card.findChild(QLabel, "value").setText(str(stats['weak']))
        self.strong_card.findChild(QLabel, "value").setText(str(stats['strong']))
        self.fav_card.findChild(QLabel, "value").setText(str(stats['favorites']))
        
        score = self.security_service.calculate_security_score(passwords_data)
        self.gauge.set_score(score)
        self.vault_bar.set_stats(stats['strong'], stats['weak'], stats['total'])

        
        # Zaktualizuj listę słabych haseł
        while self.weak_list_layout.count():
            w = self.weak_list_layout.takeAt(0).widget()
            if w: w.deleteLater()
            
        weak_accs = [p for p in passwords_data if p.get('weak_password', False)]
        if weak_accs:
            for acc in weak_accs:
                f = QFrame()
                f.setStyleSheet("background: transparent; border: none;")
                l = QHBoxLayout(f)
                l.setContentsMargins(0, 0, 0, 0)
                l.setSpacing(8)
                l.addWidget(QLabel(acc['name'], styleSheet=f"color:{styles.TEXT_PRIMARY}; font-size: 14px; border: none; background: transparent;"))
                l.addStretch()
                badge = QLabel("Weak password")
                badge.setStyleSheet(
                    f"color: {styles.COLOR_RED}; background-color: {styles.RED_SOFT};"
                    " border: none; border-radius: 10px; font-size: 11px;"
                    " font-weight: bold; padding: 3px 10px;"
                )
                l.addWidget(badge)
                self.weak_list_layout.addWidget(f)
        else:
            self.weak_list_layout.addWidget(section_header(
                "circle-check", "All passwords are strong",
                styles.COLOR_GREEN, styles.COLOR_GREEN, icon_size=16, font_px=14, bold=False,
            ))
            
        # Tabela
        total = stats['total']
        self.table.setRowCount(total)
        for i, p in enumerate(passwords_data):
            self.table.setItem(i, 0, QTableWidgetItem(p['name']))
            self.table.setItem(i, 1, QTableWidgetItem(p['email']))
            s_text = "Weak" if p.get('weak_password') else "Strong"
            s_item = QTableWidgetItem(s_text)
            s_item.setForeground(QColor(styles.COLOR_RED if p.get('weak_password') else styles.COLOR_GREEN))
            self.table.setItem(i, 2, s_item)

            sim_pwd = "password" if p.get('weak_password') else "S3cur3P@ss!"
            self.table.setItem(i, 3, QTableWidgetItem(self.get_crack_time(sim_pwd)))

            fav = "★" if p.get('favorite') else ""
            f_item = QTableWidgetItem(fav)
            f_item.setForeground(QColor(styles.COLOR_YELLOW))
            f_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, f_item)
            
        self.table.resizeRowsToContents()
        hh = self.table.horizontalHeader().height()
        rh = sum(self.table.rowHeight(i) for i in range(total))
        self.table.setFixedHeight(hh + rh + 20)

    def on_table_double_clicked(self, row, column):
        if 0 <= row < len(self.passwords_data):
            self.detail_callback(self.passwords_data[row])
