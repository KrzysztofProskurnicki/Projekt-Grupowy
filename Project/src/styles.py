"""Style constants and shared stylesheets.

Colours are module-level *variables* so that ``apply_theme()`` can swap
the entire palette at runtime.  Every view should re-read these after a
theme change (call its ``refresh_theme()``).
"""

# ===== THEME PALETTES =====
_THEMES = {
    "dark": {
        "DARK_BG":       "#1c1c1e",
        "CARD_BG":       "#2c2c2e",
        "HOVER_BG":      "#3a3a3c",
        "BORDER_COLOR":  "#38383a",
        "TEXT_PRIMARY":  "#f5f5f7",
        "TEXT_SECONDARY":"#98989d",
        "INPUT_BG":      "#3a3a3c",
    },
    "light": {
        "DARK_BG":       "#f2f2f7",
        "CARD_BG":       "#ffffff",
        "HOVER_BG":      "#e5e5ea",
        "BORDER_COLOR":  "#d1d1d6",
        "TEXT_PRIMARY":  "#1c1c1e",
        "TEXT_SECONDARY":"#6e6e73",
        "INPUT_BG":      "#e5e5ea",
    },
}

# ===== Current palette (module-level, mutable) =====
DARK_BG       = _THEMES["dark"]["DARK_BG"]
CARD_BG       = _THEMES["dark"]["CARD_BG"]
HOVER_BG      = _THEMES["dark"]["HOVER_BG"]
BORDER_COLOR  = _THEMES["dark"]["BORDER_COLOR"]
TEXT_PRIMARY   = _THEMES["dark"]["TEXT_PRIMARY"]
TEXT_SECONDARY = _THEMES["dark"]["TEXT_SECONDARY"]
INPUT_BG       = _THEMES["dark"]["INPUT_BG"]

# Accent colors (same for both themes)
COLOR_BLUE   = "#0a84ff"
COLOR_RED    = "#ff453a"
COLOR_GREEN  = "#30d158"
COLOR_YELLOW = "#ffd60a"
COLOR_ORANGE = "#ff9f0a"
COLOR_PURPLE = "#bf5af2"

# ===== FONTS =====
FONT_SIZE_SMALL  = "12px"
FONT_SIZE_NORMAL = "14px"
FONT_SIZE_MEDIUM = "16px"
FONT_SIZE_LARGE  = "20px"
FONT_SIZE_XLARGE = "24px"
FONT_SIZE_TITLE  = "32px"

# ===== Derived helpers (re-computed on theme change) =====
CARD_STYLE          = ""
SECTION_TITLE_STYLE = ""
PROGRESS_BAR_STYLE  = ""


def _rebuild_derived():
    """Rebuild derived style strings from current palette variables."""
    global CARD_STYLE, SECTION_TITLE_STYLE, PROGRESS_BAR_STYLE
    CARD_STYLE = f"background-color: {CARD_BG}; border-radius: 12px;"
    SECTION_TITLE_STYLE = (
        f"font-size: {FONT_SIZE_MEDIUM}; font-weight: bold; "
        f"color: {TEXT_PRIMARY}; background: transparent; border: none;"
    )
    PROGRESS_BAR_STYLE = (
        f"QProgressBar {{ background-color: {BORDER_COLOR}; border-radius: 4px; "
        f"height: 20px; text-align: center; color: {TEXT_PRIMARY}; }}\n"
        f"QProgressBar::chunk {{ background-color: {{color}}; border-radius: 4px; }}"
    )


_rebuild_derived()  # initial build


# ------------------------------------------------------------------ public API
def apply_theme(name: str) -> None:
    """Switch the active colour palette.

    After calling this, every module that imported colours via
    ``from styles import *`` still holds *stale* references.
    Views must call their own ``refresh_theme()`` to re-read.
    """
    global DARK_BG, CARD_BG, HOVER_BG, BORDER_COLOR
    global TEXT_PRIMARY, TEXT_SECONDARY, INPUT_BG

    palette = _THEMES.get(name, _THEMES["dark"])
    DARK_BG       = palette["DARK_BG"]
    CARD_BG       = palette["CARD_BG"]
    HOVER_BG      = palette["HOVER_BG"]
    BORDER_COLOR  = palette["BORDER_COLOR"]
    TEXT_PRIMARY   = palette["TEXT_PRIMARY"]
    TEXT_SECONDARY = palette["TEXT_SECONDARY"]
    INPUT_BG       = palette["INPUT_BG"]

    _rebuild_derived()


def get_stylesheet(theme: str) -> str:
    """Return the QApplication-level stylesheet for *theme*."""
    p = _THEMES.get(theme, _THEMES["dark"])
    accent = "#007aff" if theme == "light" else "#0a84ff"
    return f"""
    QMainWindow {{
        background-color: {p["DARK_BG"]};
    }}
    QListWidget {{
        background-color: transparent;
        border: none;
        outline: none;
    }}
    QListWidget::item {{
        background-color: transparent;
        padding: 0px;
        border: none;
    }}
    QListWidget::item:selected {{
        background-color: transparent;
    }}
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QLineEdit {{
        background-color: {p["INPUT_BG"]};
        color: {p["TEXT_PRIMARY"]};
        border-radius: 8px;
        padding: 12px;
        border: 1px solid {p["BORDER_COLOR"]};
        font-size: 14px;
    }}
    QLineEdit:focus {{
        border: 1px solid {accent};
    }}
    QLabel#AppTitle {{
        font-size: 24px;
        font-weight: bold;
        color: {p["TEXT_PRIMARY"]};
        padding: 24px;
    }}
    QFrame#Sidebar {{
        background-color: {p["CARD_BG"]};
        border-right: 1px solid {p["BORDER_COLOR"]};
        min-width: 280px;
        max-width: 280px;
    }}
    QPushButton.nav-btn {{
        text-align: left;
        padding: 12px 16px;
        border-radius: 8px;
        color: {p["TEXT_SECONDARY"]};
        font-size: 20px;
        font-weight: 500;
        background-color: transparent;
        border: none;
    }}
    QPushButton.nav-btn:hover {{
        background-color: {p["HOVER_BG"]};
        color: {p["TEXT_PRIMARY"]};
    }}
    QPushButton.nav-btn:checked {{
        background-color: {accent};
        color: white;
    }}
    QLabel.badge {{
        color: {p["TEXT_SECONDARY"]};
        font-size: 14px;
        font-weight: bold;
    }}
"""
