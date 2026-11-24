"""Carga de imágenes y utilidades de dibujo."""
import os
from PIL import Image, ImageDraw, ImageTk
import config


def cargar(nombre):
    return Image.open(os.path.join(config.ASSETS, nombre)).convert("RGBA")


def tk_img(nombre, tam=None):
    im = cargar(nombre)
    if tam:
        im = im.resize(tam, Image.LANCZOS)
    return ImageTk.PhotoImage(im)


def icono_ovalado(nombre, ancho=92, alto=66, icono=44):
    """Ícono negro sobre un óvalo blanco (como el botón de chat de tu captura)."""
    fondo = Image.new("RGBA", (ancho * 4, alto * 4), (0, 0, 0, 0))
    ImageDraw.Draw(fondo).ellipse((0, 0, ancho * 4 - 1, alto * 4 - 1), fill=(250, 248, 248, 255))
    fondo = fondo.resize((ancho, alto), Image.LANCZOS)
    ic = cargar(nombre).resize((icono, icono), Image.LANCZOS)
    fondo.alpha_composite(ic, ((ancho - icono) // 2, (alto - icono) // 2))
    return ImageTk.PhotoImage(fondo)


def rect_redondeado(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


def mezclar(c1, c2, p):
    """Mezcla dos colores #rrggbb (p=0 -> c1, p=1 -> c2)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * p) for i in range(3))
