"""Stałe zmienne stylów i współdzielone arkusze stylów.

Paleta przeniesiona 1:1 z wzorca Claude Design (wzorzec_claude_design.html):
ciemny kanwas Apple-style, hairline'owe separatory, akcent #0a84ff,
miękkie tinty statusów (16% alpha).
"""

# ===== PALETY MOTYWÓW =====
_THEMES = {
    "dark": {
        "DARK_BG":        "#1c1c1e",   # tło aplikacji (surface-app)
        "SIDEBAR_BG":     "#232325",   # sidebar (surface-sidebar)
        "CARD_BG":        "#2c2c2e",   # karty / panele (surface-card)
        "HOVER_BG":       "#3a3a3c",
        "RAISED_BG":      "#3a3a3c",   # chipy ikon, pola (surface-raised)
        "BORDER_COLOR":   "#38383a",
        "HAIRLINE":       "rgba(255, 255, 255, 8%)",
        "HAIRLINE_STRONG":"rgba(255, 255, 255, 14%)",
        "OVERLAY_HOVER":  "rgba(255, 255, 255, 5%)",
        "TEXT_PRIMARY":   "#f5f5f7",
        "TEXT_SECONDARY": "#98989d",
        "TEXT_TERTIARY":  "#7c7c80",
        "INPUT_BG":       "#3a3a3c",
        "ACCENT_TINT":    "rgba(10, 132, 255, 16%)",
    },
    "light": {
        "DARK_BG":        "#f2f2f7",
        "SIDEBAR_BG":     "#e8e8ed",
        "CARD_BG":        "#ffffff",
        "HOVER_BG":       "#e5e5ea",
        "RAISED_BG":      "#ececf1",
        "BORDER_COLOR":   "#d1d1d6",
        "HAIRLINE":       "rgba(0, 0, 0, 8%)",
        "HAIRLINE_STRONG":"rgba(0, 0, 0, 14%)",
        "OVERLAY_HOVER":  "rgba(0, 0, 0, 4%)",
        "TEXT_PRIMARY":   "#1c1c1e",
        "TEXT_SECONDARY": "#6e6e73",
        "TEXT_TERTIARY":  "#8e8e93",
        "INPUT_BG":       "#e5e5ea",
        "ACCENT_TINT":    "rgba(10, 132, 255, 12%)",
    },
}

# ===== Bieżąca paleta =====
DARK_BG        = _THEMES["dark"]["DARK_BG"]
SIDEBAR_BG     = _THEMES["dark"]["SIDEBAR_BG"]
CARD_BG        = _THEMES["dark"]["CARD_BG"]
HOVER_BG       = _THEMES["dark"]["HOVER_BG"]
RAISED_BG      = _THEMES["dark"]["RAISED_BG"]
BORDER_COLOR   = _THEMES["dark"]["BORDER_COLOR"]
HAIRLINE       = _THEMES["dark"]["HAIRLINE"]
HAIRLINE_STRONG= _THEMES["dark"]["HAIRLINE_STRONG"]
OVERLAY_HOVER  = _THEMES["dark"]["OVERLAY_HOVER"]
TEXT_PRIMARY   = _THEMES["dark"]["TEXT_PRIMARY"]
TEXT_SECONDARY = _THEMES["dark"]["TEXT_SECONDARY"]
TEXT_TERTIARY  = _THEMES["dark"]["TEXT_TERTIARY"]
INPUT_BG       = _THEMES["dark"]["INPUT_BG"]
ACCENT_TINT    = _THEMES["dark"]["ACCENT_TINT"]

# ===== PALETY AKCENTU =====
# COLOR_BLUE to historyczna nazwa "koloru akcentu" - cala aplikacja maluje nim
# aktywne elementy (pigulka nawigacji, przyciski, linki, zaznaczenia).
# apply_accent() przebindowuje go na wybrana palete.
_ACCENTS = {
    "blue":   {"label": "Blue",   "base": "#0a84ff", "hover": "#0077ea"},
    "indigo": {"label": "Indigo", "base": "#5e5ce6", "hover": "#4b49d6"},
    "purple": {"label": "Purple", "base": "#bf5af2", "hover": "#aa3ee6"},
    "pink":   {"label": "Pink",   "base": "#ff375f", "hover": "#e9224b"},
    "orange": {"label": "Orange", "base": "#ff9f0a", "hover": "#ec8f00"},
    "green":  {"label": "Green",  "base": "#30d158", "hover": "#28b94e"},
}
# Kolejnosc i etykiety do UI ustawien: (klucz, etykieta, kolor)
ACCENT_CHOICES = [(k, v["label"], v["base"]) for k, v in _ACCENTS.items()]
ACTIVE_ACCENT = "blue"

# Kolory akcentu
COLOR_BLUE   = "#0a84ff"
COLOR_BLUE_HOVER = "#0077ea"
COLOR_RED    = "#ff453a"
COLOR_GREEN  = "#30d158"
COLOR_YELLOW = "#ffd60a"
COLOR_ORANGE = "#ff9f0a"
COLOR_PURPLE = "#bf5af2"

# Miękkie tinty statusów (niezależne od motywu, 16% alpha jak we wzorcu)
GREEN_SOFT  = "rgba(48, 209, 88, 16%)"
RED_SOFT    = "rgba(255, 69, 58, 16%)"
YELLOW_SOFT = "rgba(255, 214, 10, 16%)"
ORANGE_SOFT = "rgba(255, 159, 10, 16%)"
BLUE_SOFT   = "rgba(10, 132, 255, 16%)"

# ===== FONTY =====
FONT_SIZE_SMALL  = "12px"
FONT_SIZE_NORMAL = "14px"
FONT_SIZE_MEDIUM = "16px"
FONT_SIZE_LARGE  = "20px"
FONT_SIZE_XLARGE = "24px"
FONT_SIZE_TITLE  = "32px"

# ===== Pochodne pomocnicze (przeliczane po zmianie motywu) =====
CARD_STYLE          = ""
SECTION_TITLE_STYLE = ""
PROGRESS_BAR_STYLE  = ""
FIELD_LABEL_STYLE   = ""


def _rebuild_derived():
    """Przebuduj pochodne stringi stylów z bieżących zmiennych palety"""
    global CARD_STYLE, SECTION_TITLE_STYLE, PROGRESS_BAR_STYLE, FIELD_LABEL_STYLE
    CARD_STYLE = (
        f"background-color: {CARD_BG}; border-radius: 12px; "
        f"border: 1px solid {HAIRLINE};"
    )
    SECTION_TITLE_STYLE = (
        f"font-size: 17px; font-weight: 600; "
        f"color: {TEXT_PRIMARY}; background: transparent; border: none;"
    )
    PROGRESS_BAR_STYLE = (
        f"QProgressBar {{ background-color: {BORDER_COLOR}; border-radius: 4px; "
        f"height: 20px; text-align: center; color: {TEXT_PRIMARY}; }}\n"
        f"QProgressBar::chunk {{ background-color: {{color}}; border-radius: 4px; }}"
    )
    # Konwencja etykiet pól: uppercase, tracking, tertiary (ds-field-label)
    FIELD_LABEL_STYLE = (
        f"font-size: 11px; font-weight: 600; letter-spacing: 1px; "
        f"color: {TEXT_TERTIARY}; background: transparent; border: none;"
    )


_rebuild_derived()


# Nazwa aktualnie zaaplikowanego motywu (apply_theme nadpisuje).
# Zawsze "dark"/"light" - wybor "system" jest rozwiazywany przy aplikowaniu.
ACTIVE_THEME = "dark"


def _system_theme() -> str:
    """Odczytaj systemowy tryb jasny/ciemny (Windows: rejestr Personalize)."""
    import sys
    if sys.platform != "win32":
        return "dark"
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return "light" if value else "dark"
    except OSError:
        return "dark"


def resolve_theme(name: str) -> str:
    """Zamien wybor uzytkownika ("system"/"dark"/"light") na konkretny motyw."""
    if name == "system":
        return _system_theme()
    return name if name in _THEMES else "dark"


def _hex_to_rgb(color: str) -> str:
    """"#rrggbb" -> "r, g, b" (do skladania rgba w QSS)."""
    color = color.lstrip("#")
    return f"{int(color[0:2], 16)}, {int(color[2:4], 16)}, {int(color[4:6], 16)}"


def apply_accent(name: str) -> None:
    """Przebinduj kolor akcentu (COLOR_BLUE i pochodne tinty) na palete *name*."""
    global COLOR_BLUE, COLOR_BLUE_HOVER, BLUE_SOFT, ACCENT_TINT, ACTIVE_ACCENT

    ACTIVE_ACCENT = name if name in _ACCENTS else "blue"
    accent = _ACCENTS[ACTIVE_ACCENT]
    rgb = _hex_to_rgb(accent["base"])
    alpha = "12%" if ACTIVE_THEME == "light" else "16%"

    COLOR_BLUE = accent["base"]
    COLOR_BLUE_HOVER = accent["hover"]
    BLUE_SOFT = f"rgba({rgb}, 16%)"
    ACCENT_TINT = f"rgba({rgb}, {alpha})"

    _rebuild_derived()


# --- Publiczne API ---
def apply_theme(name: str) -> None:

    global DARK_BG, SIDEBAR_BG, CARD_BG, HOVER_BG, RAISED_BG, BORDER_COLOR
    global HAIRLINE, HAIRLINE_STRONG, OVERLAY_HOVER
    global TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY, INPUT_BG, ACCENT_TINT
    global ACTIVE_THEME

    ACTIVE_THEME = resolve_theme(name)
    palette = _THEMES[ACTIVE_THEME]
    DARK_BG        = palette["DARK_BG"]
    SIDEBAR_BG     = palette["SIDEBAR_BG"]
    CARD_BG        = palette["CARD_BG"]
    HOVER_BG       = palette["HOVER_BG"]
    RAISED_BG      = palette["RAISED_BG"]
    BORDER_COLOR   = palette["BORDER_COLOR"]
    HAIRLINE       = palette["HAIRLINE"]
    HAIRLINE_STRONG= palette["HAIRLINE_STRONG"]
    OVERLAY_HOVER  = palette["OVERLAY_HOVER"]
    TEXT_PRIMARY   = palette["TEXT_PRIMARY"]
    TEXT_SECONDARY = palette["TEXT_SECONDARY"]
    TEXT_TERTIARY  = palette["TEXT_TERTIARY"]
    INPUT_BG       = palette["INPUT_BG"]
    ACCENT_TINT    = palette["ACCENT_TINT"]

    # Ponownie nałóż wybrany akcent (tinty zależą od motywu)
    apply_accent(ACTIVE_ACCENT)


def apply_titlebar_theme(window, theme: str = None) -> None:
    """Dopasuj kolor systemowego paska tytułu okna do motywu (tylko Windows).

    Używa DWMWA_USE_IMMERSIVE_DARK_MODE (atrybut 20, na starszych buildach
    Windows 10 atrybut 19). Wywołuj po utworzeniu okna i przy zmianie motywu.
    """
    import sys
    if sys.platform != "win32":
        return
    import ctypes
    effective = resolve_theme(theme) if theme else ACTIVE_THEME
    dark = ctypes.c_int(1 if effective == "dark" else 0)
    try:
        hwnd = int(window.winId())
        for attr in (20, 19):
            res = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(dark), ctypes.sizeof(dark)
            )
            if res == 0:
                break
    except (OSError, AttributeError):
        pass  # brak dwmapi / egzotyczny build - pasek zostaje systemowy


def get_stylesheet(theme: str) -> str:
    """Zwróć arkusz stylów na poziomie QApplication dla danego *theme*."""
    p = _THEMES[resolve_theme(theme)]
    accent = _ACCENTS[ACTIVE_ACCENT]["base"]
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
        padding: 10px 12px;
        border: 1px solid {p["HAIRLINE"]};
        font-size: 14px;
    }}
    QLineEdit:focus {{
        border: 1px solid {accent};
    }}
    QFrame#Sidebar {{
        background-color: {p["SIDEBAR_BG"]};
        border-right: 1px solid {p["HAIRLINE"]};
        min-width: 280px;
        max-width: 280px;
    }}
    QPushButton.nav-btn {{
        text-align: left;
        padding: 11px 12px;
        border-radius: 8px;
        color: {p["TEXT_SECONDARY"]};
        font-size: 14px;
        font-weight: 500;
        background-color: transparent;
        border: none;
    }}
    QPushButton.nav-btn:hover {{
        background-color: {p["OVERLAY_HOVER"]};
        color: {p["TEXT_PRIMARY"]};
    }}
    QPushButton.nav-btn:checked {{
        background-color: {accent};
        color: white;
    }}
    QLabel.badge {{
        color: {p["TEXT_TERTIARY"]};
        font-size: 13px;
        font-weight: 600;
    }}
    QToolTip {{
        background-color: {p["CARD_BG"]};
        color: {p["TEXT_PRIMARY"]};
        border: 1px solid {p["HAIRLINE_STRONG"]};
        padding: 4px 8px;
    }}
"""
