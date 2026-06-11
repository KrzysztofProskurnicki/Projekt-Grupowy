"""Helper ikon SVG - ładuje ikony Lucide z assets/icons i przekolorowuje pod motyw.

Renderuje wektor z nadpróbkowaniem i antyaliasingiem, więc ikony są ostre
niezależnie od skali ekranu (w przeciwieństwie do glifów emoji/fontów).
Kolor nakładany jest kompozycją SourceIn, więc dowolny SVG (outline lub filled)
przyjmuje zadany kolor zachowując kształt i wygładzone krawędzie.
"""

import os

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication
from PyQt5.QtSvg import QSvgRenderer

import styles

# Project/assets/icons (trzy poziomy w górę z src/widgets/icons.py)
_ICON_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "icons",
)

# Krotność nadpróbkowania przed wygładzonym zmniejszeniem do rozmiaru docelowego.
_SUPERSAMPLE = 4

_cache: dict = {}


def _screen_dpr() -> float:
    """Współczynnik pikseli ekranu (1.0 dla 100%, 2.0 dla 200% itd.)."""
    app = QApplication.instance()
    if app is not None:
        screen = app.primaryScreen()
        if screen is not None:
            return max(1.0, screen.devicePixelRatio())
    return 1.0


def tinted_pixmap(name: str, color: str, size: int = 20) -> QPixmap:
    """Zwróć QPixmap ikony *name* przekolorowanej na *color* o boku *size* px.

    Renderuje wektor mocno powiększony, a następnie zmniejsza go z wygładzaniem
    (SmoothTransformation) dokładnie do rozmiaru wyświetlania. Dzięki temu
    krawędzie są interpolowane i gładkie, bez schodków przy skalowaniu w widgecie.
    """
    dpr = _screen_dpr()
    key = (name, color, size, dpr)
    cached = _cache.get(key)
    if cached is not None:
        return cached

    path = os.path.join(_ICON_DIR, f"{name}.svg")
    renderer = QSvgRenderer(path)

    side = max(1, int(round(size * dpr)))           # docelowy rozmiar w pikselach urządzenia
    big = side * _SUPERSAMPLE

    canvas = QPixmap(big, big)
    canvas.fill(Qt.transparent)

    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    # Lekki margines (~6%), by gruba kreska (stroke-width) nie była przycinana na krawędzi
    inset = big * 0.06
    renderer.render(painter, QRectF(inset, inset, big - 2 * inset, big - 2 * inset))
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(canvas.rect(), QColor(color))
    painter.end()

    pm = canvas.scaled(side, side, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    pm.setDevicePixelRatio(dpr)
    _cache[key] = pm
    return pm


def tinted_icon(name: str, color: str, size: int = 20) -> QIcon:
    """Zwróć QIcon ikony *name* przekolorowanej na *color*."""
    return QIcon(tinted_pixmap(name, color, size))


def app_icon() -> QIcon:
    """Ikona aplikacji: biała tarcza (shield-check) bez tła.

    Renderowana w kilku rozmiarach, żeby pasek tytułu, Alt+Tab i pasek zadań
    dostały ostrą wersję.
    """
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(tinted_pixmap("shield-check", "#ffffff", size))
    return icon


def icon_label(name: str, color: str, size: int = 20) -> QLabel:
    """Zwróć QLabel z przekolorowaną ikoną (do wstawiania obok tekstu)."""
    lbl = QLabel()
    lbl.setPixmap(tinted_pixmap(name, color, size))
    lbl.setFixedSize(size, size)
    lbl.setStyleSheet("background: transparent; border: none;")
    return lbl


def section_header(
    name: str,
    text: str,
    icon_color: str,
    text_color: str,
    icon_size: int = 18,
    font_px: int = 16,
    bold: bool = True,
) -> QWidget:
    """Zbuduj wiersz nagłówka: ikona + tekst (zastępuje emoji w nagłówkach)."""
    wrap = QWidget()
    wrap.setStyleSheet("background: transparent; border: none;")
    lay = QHBoxLayout(wrap)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)

    lay.addWidget(icon_label(name, icon_color, icon_size))

    txt = QLabel(text)
    weight = "bold" if bold else "500"
    txt.setStyleSheet(
        f"font-size: {styles.font_px(font_px)}px; font-weight: {weight}; color: {text_color};"
        " background: transparent; border: none;"
    )
    lay.addWidget(txt)
    lay.addStretch()
    return wrap
