"""Pantalla principal: reactor animado + menú lateral (chat / rendimiento).
Optimizada: los fotogramas de giro se cachean y los elementos del canvas se reutilizan."""
import math
import time
import tkinter as tk
from PIL import Image, ImageTk
import config
from ui import recursos

PASO = 6                                  # grados por fotograma cacheado (60 fotogramas)
ONDAS = [recursos.mezclar(config.AZUL_CLARO, config.AZUL_FONDO, i / 9) for i in range(10)]


class PantallaInicio(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=config.AZUL_FONDO)
        self.app = app
        self._base, self._foto, self._cache = None, None, {}
        self._ang, self._t_prev = 0.0, time.time()
        self._reactor = recursos.cargar("reactor.png")
        self._habla_prev = None
        self._textos = {}

        menu = tk.Frame(self, bg=config.AZUL_MENU, width=170)
        menu.pack(side="right", fill="y")
        menu.pack_propagate(False)
        self._ic_chat = recursos.icono_ovalado("icono_chat.png")
        self._ic_rend = recursos.tk_img("icono_rendimiento.png", (74, 74))
        self._boton(menu, self._ic_chat, "chatea con\njarvis", 0.28, lambda: app.mostrar("chat"))
        self._boton(menu, self._ic_rend, "RENDIMIENTO", 0.68, lambda: app.mostrar("rendimiento"))

        self.canvas = tk.Canvas(self, bg=config.AZUL_FONDO, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<Configure>", self._construir)
        tk.Label(self, text="JARVIS\nUNEFA", font=("Segoe UI", 20, "bold"), justify="left",
                 fg=config.BLANCO, bg=config.AZUL_FONDO).place(x=22, y=14)
        self.estado = ""
        self._tick()

    def _boton(self, padre, imagen, texto, rely, comando):
        f = tk.Frame(padre, bg=config.AZUL_MENU, cursor="hand2")
        f.place(relx=0.5, rely=rely, anchor="center")
        for w in (tk.Label(f, image=imagen, bg=config.AZUL_MENU),
                  tk.Label(f, text=texto, fg=config.BLANCO, bg=config.AZUL_MENU,
                           font=("Segoe UI", 10))):
            w.pack(pady=2)
            w.bind("<Button-1>", lambda e: comando())
        f.bind("<Button-1>", lambda e: comando())

    def set_estado(self, texto):
        self.estado = texto

    def _geom(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        return w // 2, h // 2 - 20, int(min(w, h) * 0.62)

    def _click(self, e):
        cx, cy, n = self._geom()
        if math.hypot(e.x - cx, e.y - cy) <= n / 2:
            self.app.alternar_camara()

    def _construir(self, e=None):
        """Crea los elementos UNA vez (y otra vez solo si cambia el tamaño de la ventana)."""
        c = self.canvas
        c.delete("all")
        self._cache.clear()
        cx, cy, n = self._geom()
        if n < 50:
            self._base = None
            return
        self._n = n
        self._base = self._reactor.resize((n, n), Image.LANCZOS)
        self._ondas = [c.create_oval(0, 0, 0, 0, width=2, state="hidden") for _ in range(3)]
        self._img = c.create_image(cx, cy)
        ty = cy + n / 2 + 34
        c.create_text(cx, ty, text="QUE DESEA MI SEÑOR", fill=config.BLANCO, font=("Segoe UI", 13))
        self._t_cam = c.create_text(cx, ty + 26, font=("Segoe UI", 9))
        self._t_est = c.create_text(cx, ty + 46, fill="#9fb0ff", font=("Segoe UI", 9))
        self._textos = {}
        self._habla_prev = None

    def _texto(self, item, texto, color=None):
        if self._textos.get(item) != (texto, color):
            self._textos[item] = (texto, color)
            if color:
                self.canvas.itemconfig(item, text=texto, fill=color)
            else:
                self.canvas.itemconfig(item, text=texto)

    def _tick(self):
        ahora = time.time()
        dt, self._t_prev = ahora - self._t_prev, ahora
        habla = self.app.voz.hablando.is_set()
        if self.winfo_ismapped() and self._base is not None:
            c = self.canvas
            cx, cy, n = self._geom()
            self._ang = (self._ang - (150 if habla else 25) * dt) % 360
            b = int(self._ang // PASO)
            foto = self._cache.get(b)
            if foto is None:
                foto = ImageTk.PhotoImage(self._base.rotate(b * PASO, resample=Image.BILINEAR))
                self._cache[b] = foto
            if foto is not self._foto:
                c.itemconfig(self._img, image=foto)
                self._foto = foto
            if habla:                                    # ondas mientras Jarvis habla
                for k, o in enumerate(self._ondas):
                    p = (ahora * 0.8 + k / 3) % 1
                    r = n / 2 * (0.7 + 0.7 * p)
                    c.coords(o, cx - r, cy - r, cx + r, cy + r)
                    c.itemconfig(o, outline=ONDAS[int(p * 9)], state="normal")
            elif self._habla_prev:
                for o in self._ondas:
                    c.itemconfig(o, state="hidden")
            self._habla_prev = habla
            if self.app.camara.activa.is_set():
                self._texto(self._t_cam, "● CÁMARA ACTIVA  (toca el reactor para apagar)", "#34d399")
            else:
                self._texto(self._t_cam, "toca el reactor para activar la cámara", "#7f8fd8")
            self._texto(self._t_est, self.estado)
        self.after(40 if habla else 80, self._tick)      # reposo: ~12 fps
