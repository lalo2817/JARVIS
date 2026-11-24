"""Cámara con HUD + control con las manos.

Gestos (con 'manos' activadas):
  ☝ índice solo         -> mueve el cursor;  juntar pulgar+índice = clic
  ✌ paz                 -> scroll (sube/baja la mano)
  🖐 palma + deslizar    -> cambiar de aplicación (Alt+Tab)
  ✊ puño sostenido      -> play/pausa multimedia
  chasquido de dedos    -> "SOY IRON MAN"
"""
import math
import threading
import time
import cv2
import numpy as np
import mediapipe as mp
import config
from core import hud
from core.hud import C_CIAN, C_CIAN_TENUE, C_NARANJA, FONT


class Camara:
    def __init__(self, on_log, on_cerrada):
        self.on_log, self.on_cerrada = on_log, on_cerrada
        self.activa = threading.Event()
        self.frame = None                 # último frame RGB listo
        self.manos_on = config.MANOS_ACTIVAS

    def encender(self):
        if not self.activa.is_set():
            self.activa.set()
            threading.Thread(target=self._hilo, daemon=True).start()

    def apagar(self):
        self.activa.clear()

    # ------------------------------------------------------------------
    def _hilo(self):
        import pyautogui
        pyautogui.PAUSE = 0
        sw, sh = pyautogui.size()
        cap = cv2.VideoCapture(config.CAMARA_INDEX, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.on_log("No pude abrir la cámara (¿está en uso? prueba CAMARA_INDEX = 1).")
            self.activa.clear()
            self.on_cerrada()
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        manos = mp.solutions.hands.Hands(max_num_hands=config.MAX_MANOS, model_complexity=0,
                                         min_detection_confidence=0.6,
                                         min_tracking_confidence=0.6)
        cara = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True,
                                               min_detection_confidence=0.5,
                                               min_tracking_confidence=0.5)
        self.on_log("Cámara activada.")

        puno_desde = 0.0
        ultima_accion = ultimo_clic = ultimo_snap = snap_armado = snap_t0 = 0.0
        cur = None                         # posición suavizada del cursor
        hist_x = []                        # (t, x) de la muñeca para detectar deslizar
        scroll_y, scroll_acc = None, 0.0
        fallos = 0
        n_frame, lm_cara = 0, None

        while self.activa.is_set():
            t_ini = time.time()
            ok, frame = cap.read()
            if not ok:
                fallos += 1
                if fallos > 30:
                    self.on_log("La cámara dejó de responder.")
                    break
                time.sleep(0.05)
                continue
            fallos = 0
            frame = cv2.flip(frame, 1)
            if frame.shape[1] != 320:
                frame = cv2.resize(frame, (320, 240))
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res_m = manos.process(rgb)
            if n_frame % config.CARA_CADA == 0:      # el rostro no hace falta cada cuadro
                rc = cara.process(rgb)
                lm_cara = rc.multi_face_landmarks[0].landmark if rc.multi_face_landmarks else None
            n_frame += 1
            layer = np.zeros_like(frame)
            t = ahora = time.time()

            # ---------- Cara y ojos ----------
            if lm_cara:
                lm = lm_cara
                xs, ys = [p.x * w for p in lm], [p.y * h for p in lm]
                x1, x2 = int(min(xs)) - 10, int(max(xs)) + 10
                y1, y2 = int(min(ys)) - 10, int(max(ys)) + 10
                hud.esquinas(layer, x1, y1, x2, y2, C_CIAN, max(14, (x2 - x1) // 6))
                cv2.putText(layer, "ANALIZANDO ROSTRO", (x1, y1 - 8), FONT, 0.35, C_CIAN, 1, cv2.LINE_AA)
                for ci, a, b in ((468, 469, 471), (473, 474, 476)):
                    c = (int(lm[ci].x * w), int(lm[ci].y * h))
                    ra = math.hypot((lm[a].x - lm[b].x) * w, (lm[a].y - lm[b].y) * h) / 2
                    hud.hud_ojo(layer, c, max(int(ra * 3.2), 14), t)

            # ---------- Manos ----------
            gesto = None
            if res_m.multi_hand_landmarks:
                for i, hl in enumerate(res_m.multi_hand_landmarks):
                    pts, pulgar, otros, tam = hud.analizar_mano(hl, w, h)
                    c = (int(sum(pts[k][0] for k in (0, 5, 9, 13, 17)) / 5),
                         int(sum(pts[k][1] for k in (0, 5, 9, 13, 17)) / 5))
                    r = max(int(tam * 1.25), 30)
                    for tip in (4, 8, 12, 16, 20):
                        p = (int(pts[tip][0]), int(pts[tip][1]))
                        cv2.line(layer, c, p, C_CIAN_TENUE, 1, cv2.LINE_AA)
                        cv2.circle(layer, p, 7, C_CIAN, 1, cv2.LINE_AA)

                    n = sum(otros)
                    if i == 0:
                        if n == 4:
                            gesto = "palma"
                        elif n == 0 and config.GESTO_PUNO:
                            gesto = "puno"
                        elif otros == [True, True, False, False]:
                            gesto = "paz"
                        elif otros == [True, False, False, False]:
                            gesto = "cursor"
                    prog = 0.0
                    if i == 0 and gesto == "puno" and puno_desde:
                        prog = min((ahora - puno_desde) / config.HOLD, 1.0)
                    hud.hud_mano(layer, c, r, t, prog)
                    cv2.putText(layer, f"DEDOS: {int(pulgar) + n}" + (f"  [{gesto.upper()}]" if gesto and i == 0 else ""),
                                (c[0] - r, c[1] - r - 16), FONT, 0.35, C_CIAN, 1, cv2.LINE_AA)

                    # ----- Chasquido -----
                    pinch, palma = hud.metricas_chasquido(pts, tam)
                    if pinch < config.SNAP_PINCH and palma > config.SNAP_PALMA_MIN:
                        snap_armado = ahora
                    elif (snap_armado and ahora - snap_armado < config.SNAP_VENTANA
                          and pinch > config.SNAP_SUELTA and palma < config.SNAP_PALMA_MAX
                          and ahora - ultimo_snap > config.SNAP_COOLDOWN):
                        snap_armado, ultimo_snap, snap_t0 = 0.0, ahora, ahora
                        ultima_accion = ahora
                        self.on_log(f"⚡ {config.FRASE_SNAP}")

                    # ----- Control con la primera mano -----
                    if i == 0 and self.manos_on and ahora - snap_t0 > 1.0:
                        try:
                            if gesto == "cursor":
                                nx = (pts[8][0] / w - config.MARGEN_CAM) / (1 - 2 * config.MARGEN_CAM)
                                ny = (pts[8][1] / h - config.MARGEN_CAM) / (1 - 2 * config.MARGEN_CAM)
                                tx = min(max(nx, 0), 1) * (sw - 12) + 6
                                ty = min(max(ny, 0), 1) * (sh - 12) + 6
                                cur = (tx, ty) if cur is None else (
                                    cur[0] + (tx - cur[0]) * config.SUAVIZADO,
                                    cur[1] + (ty - cur[1]) * config.SUAVIZADO)
                                pyautogui.moveTo(int(cur[0]), int(cur[1]))
                                pinz = math.hypot(pts[4][0] - pts[8][0], pts[4][1] - pts[8][1]) / max(tam, 1)
                                if pinz < config.CLIC_PINCH and ahora - ultimo_clic > 0.8:
                                    ultimo_clic = ahora
                                    pyautogui.click()
                            elif gesto == "paz":
                                y = pts[9][1]
                                if scroll_y is not None:
                                    scroll_acc += scroll_y - y
                                    if abs(scroll_acc) > 14:
                                        pyautogui.scroll(int(math.copysign(config.SCROLL_PASO, scroll_acc)))
                                        scroll_acc = 0.0
                                scroll_y = y
                            elif gesto == "palma":
                                hist_x.append((ahora, pts[0][0] / w))
                                hist_x[:] = [(a, b) for a, b in hist_x if ahora - a < 0.35]
                                if len(hist_x) > 3 and ahora - ultima_accion > config.COOLDOWN:
                                    vel = (hist_x[-1][1] - hist_x[0][1]) / max(hist_x[-1][0] - hist_x[0][0], 0.05)
                                    if abs(vel) > config.SWIPE_VEL:
                                        ultima_accion = ahora
                                        hist_x.clear()
                                        if vel > 0:
                                            pyautogui.hotkey("alt", "tab")
                                        else:
                                            pyautogui.hotkey("alt", "shift", "tab")
                            elif gesto == "puno":
                                puno_desde = puno_desde or ahora
                                if ahora - puno_desde >= config.HOLD and ahora - ultima_accion > config.COOLDOWN:
                                    ultima_accion, puno_desde = ahora, 0.0
                                    pyautogui.press("playpause")
                        except Exception as e:      # p. ej. pyautogui bloqueado
                            self.on_log(f"Gesto falló: {e}")
            if gesto != "puno":
                puno_desde = 0.0
            if gesto != "paz":
                scroll_y, scroll_acc = None, 0.0
            if gesto != "cursor":
                cur = None
            if gesto != "palma":
                hist_x.clear()

            # ---------- Texto chasquido + glow ----------
            if snap_t0:
                dt = ahora - snap_t0
                if dt > config.SNAP_TEXTO_SEG:
                    snap_t0 = 0.0
                else:
                    hud.dibujar_frase_snap(layer, dt, w, h)
            out = cv2.add(cv2.add(frame, cv2.GaussianBlur(layer, (0, 0), 3)), layer)
            cv2.putText(out, "J.A.R.V.I.S. VISION  |  MANOS: " + ("ON" if self.manos_on else "OFF"),
                        (8, 16), FONT, 0.38, C_CIAN, 1, cv2.LINE_AA)
            self.frame = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
            time.sleep(max(0.0, 1.0 / config.FPS_CAMARA - (time.time() - t_ini)))   # tope de FPS

        cap.release()
        manos.close()
        cara.close()
        self.frame = None
        self.on_log("Cámara apagada.")
        self.on_cerrada()
