"""Dibujos estilo Iron Man sobre la cámara (anillos, mira en los ojos, esquinas, chasquido)."""
import math
import cv2
import config

C_CIAN = (255, 230, 0)          # BGR
C_CIAN_TENUE = (140, 120, 0)
C_NARANJA = (0, 165, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def arco(layer, c, r, ang, span, color, th=2):
    cv2.ellipse(layer, c, (r, r), 0, ang, ang + span, color, th, cv2.LINE_AA)


def hud_mano(layer, c, r, t, progreso=0.0):
    a1 = int(t * 90) % 360
    for k in range(3):
        arco(layer, c, r, a1 + k * 120, 70, C_CIAN, 2)
    r2, a2 = int(r * 0.78), -int(t * 140) % 360
    for k in range(4):
        arco(layer, c, r2, a2 + k * 90, 40, C_CIAN, 1)
    off = int(t * 30)
    for k in range(0, 360, 15):
        rad = math.radians(k + off)
        p1 = (int(c[0] + (r + 6) * math.cos(rad)), int(c[1] + (r + 6) * math.sin(rad)))
        p2 = (int(c[0] + (r + 12) * math.cos(rad)), int(c[1] + (r + 12) * math.sin(rad)))
        cv2.line(layer, p1, p2, C_CIAN_TENUE, 1, cv2.LINE_AA)
    cv2.circle(layer, c, 4, C_CIAN, -1, cv2.LINE_AA)
    cv2.circle(layer, c, int(r * 0.35), C_CIAN_TENUE, 1, cv2.LINE_AA)
    if progreso > 0:
        cv2.ellipse(layer, c, (r + 20, r + 20), 0, -90, -90 + int(360 * progreso),
                    C_NARANJA, 3, cv2.LINE_AA)


def hud_ojo(layer, c, r, t):
    a = int(t * 120) % 360
    arco(layer, c, r, a, 90, C_CIAN, 2)
    arco(layer, c, r, a + 180, 90, C_CIAN, 2)
    r2 = int(r * 0.65)
    arco(layer, c, r2, -a, 60, C_CIAN, 1)
    arco(layer, c, r2, -a + 180, 60, C_CIAN, 1)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        cv2.line(layer, (c[0] + dx * (r + 4), c[1] + dy * (r + 4)),
                 (c[0] + dx * (r + 12), c[1] + dy * (r + 12)), C_CIAN, 1, cv2.LINE_AA)
    cv2.circle(layer, c, 2, C_NARANJA, -1, cv2.LINE_AA)


def esquinas(layer, x1, y1, x2, y2, color, largo):
    for (px, py, sx, sy) in ((x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)):
        cv2.line(layer, (px, py), (px + sx * largo, py), color, 2, cv2.LINE_AA)
        cv2.line(layer, (px, py), (px, py + sy * largo), color, 2, cv2.LINE_AA)


def analizar_mano(lm, w, h):
    pts = [(p.x * w, p.y * h) for p in lm.landmark]

    def d(a, b):
        return math.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1])

    pulgar = d(4, 17) > d(3, 17)
    otros = [d(tip, 0) > d(pip, 0) for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18))]
    return pts, pulgar, otros, d(0, 9)


def metricas_chasquido(pts, tam):
    tam = max(tam, 1.0)
    cx = sum(pts[k][0] for k in (0, 5, 9, 13, 17)) / 5
    cy = sum(pts[k][1] for k in (0, 5, 9, 13, 17)) / 5
    pinch = math.hypot(pts[4][0] - pts[12][0], pts[4][1] - pts[12][1]) / tam
    palma = math.hypot(pts[12][0] - cx, pts[12][1] - cy) / tam
    return pinch, palma


def dibujar_frase_snap(layer, dt, w, h):
    frase, dur = config.FRASE_SNAP, config.SNAP_TEXTO_SEG
    n = min(len(frase), int(dt / 0.07) + 1)
    fade = 1.0 if dt < dur - 0.6 else max(0.0, (dur - dt) / 0.6)
    (tw0, _), _ = cv2.getTextSize(frase, FONT, 1.0, 3)
    escala = (w * 0.86) / tw0
    (tw, th), _ = cv2.getTextSize(frase, FONT, escala, 3)
    x, y = (w - tw) // 2, h // 2 + th // 2
    cian = tuple(int(c * fade) for c in C_CIAN)
    naranja = tuple(int(c * fade) for c in C_NARANJA)
    cv2.putText(layer, frase[:n], (x, y), FONT, escala, cian, 3, cv2.LINE_AA)
    cv2.line(layer, (x, y + 16), (x + int(tw * n / len(frase)), y + 16), naranja, 2, cv2.LINE_AA)
