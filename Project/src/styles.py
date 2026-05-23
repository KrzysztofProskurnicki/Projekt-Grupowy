"""Style constants and shared stylesheets."""

# ===== COLORS =====
# Background colors
DARK_BG = "#1c1c1e"
CARD_BG = "#2c2c2e"
HOVER_BG = "#3a3a3c"
BORDER_COLOR = "#38383a"

# Text colors
TEXT_PRIMARY = "#f5f5f7"
TEXT_SECONDARY = "#98989d"

# Accent colors
COLOR_BLUE = "#0a84ff"
COLOR_RED = "#ff453a"
COLOR_GREEN = "#30d158"
COLOR_YELLOW = "#ffd60a"

# Additional UI colors
COLOR_ORANGE = "#ff9f0a"
COLOR_PURPLE = "#bf5af2"

# ===== FONTS =====
FONT_SIZE_SMALL = "12px"
FONT_SIZE_NORMAL = "14px"
FONT_SIZE_MEDIUM = "16px"
FONT_SIZE_LARGE = "20px"
FONT_SIZE_XLARGE = "24px"
FONT_SIZE_TITLE = "32px"

# ===== REUSABLE STYLES =====
CARD_STYLE = f"background-color: {CARD_BG}; border-radius: 12px;"
SECTION_TITLE_STYLE = f"font-size: {FONT_SIZE_MEDIUM}; font-weight: bold; color: {TEXT_PRIMARY};"
PROGRESS_BAR_STYLE = f"""
    QProgressBar {{ background-color: {BORDER_COLOR}; border-radius: 4px; height: 20px; text-align: center; color: {TEXT_PRIMARY}; }}
    QProgressBar::chunk {{ background-color: {{color}}; border-radius: 4px; }}
"""


STYLESHEET = """
    QMainWindow {
        background-color: #1c1c1e;
    }
    QListWidget {
        background-color: transparent;
        border: none;
        outline: none;
    }
    QListWidget::item {
        background-color: transparent;
        padding: 0px;
        border: none;
    }
    QListWidget::item:selected {
        background-color: transparent;
    }
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QLineEdit {
        background-color: #2c2c2e;
        color: #f5f5f7;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #38383a;
        font-size: 14px;
    }
    QLineEdit:focus {
        border: 1px solid #0a84ff;
    }
    QLabel#AppTitle {
        font-size: 24px;
        font-weight: bold;
        color: #f5f5f7;
        padding: 24px;
    }
    QFrame#Sidebar {
        background-color: #2c2c2e;
        border-right: 1px solid #38383a;
        min-width: 280px;
        max-width: 280px;
    }
    QPushButton.nav-btn {
        text-align: left;
        padding: 12px 16px;
        border-radius: 8px;
        color: #98989d;
        font-size: 20px;
        font-weight: 500;
        background-color: transparent;
        border: none;
    }
    QPushButton.nav-btn:hover {
        background-color: #3a3a3c;
        color: #f5f5f7;
    }
    QPushButton.nav-btn:checked {
        background-color: #0a84ff;
        color: white;
    }
    QLabel.badge {
        color: #98989d;
        font-size: 14px;
        font-weight: bold;
    }
"""
