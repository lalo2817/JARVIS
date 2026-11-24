"""Pantalla de rendimiento: RAM, almacenamiento y CPU con barras animadas.
Optimizada: los elementos se crean una vez y solo se cambia lo que varía."""
import time
import tkinter as tk
import config
from core import sistema
from ui import recursos

SEG = 30
FILAS = (("RAM", "ram"), ("ALMACEN\nAMIENTO", "disco"), ("CPU", "cpu"))
APAGADO = "#13267f"
AZUL, AZUL_B = config.AZUL_CLARO, "#7fa3ff"
ROJO, ROJO_B = "#e03a3a", "#ffb3b3"


class PantallaRendimiento(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=config.AZUL_FONDO)
        self.app = app
        self.canvas = tk.Canvas(self, bg=config.AZUL_FONDO, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._construir)
        volver = tk.Label(self, text="◀ INICIO", fg=config.BLANCO, bg=config.AZUL_FONDO,
                          font=("Segoe UI", 11, "bold"), cursor="hand2")
        volver.place(x=20, y=14)
        volver.bind("<Button-1>", lambda e: app.mostrar("inicio"))
        self.valor = {k: 0.0 for _, k in FILAS}
        self.meta = {k: (0.0, "") for _, k in FILAS}
        self._t_datos = 0.0
        self._filas = None
        self._tick()

    def _construir(self, e=None):
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 100:
            return
        x0, x1 = w * 0.36, w * 0.84
        sw = (x1 - x0) / SEG
        r, cxa = 26, w * 0.30
        self._filas = []
        for i, (titulo, clave) in enumerate(FILAS):
            y = h * (0.25 + 0.25 * i)
            c.create_text(w * 0.17, y, text=titulo, fill=config.BLANCO, justify="center",
                          font=("Segoe UI", 16, "bold"))
            c.create_oval(cxa - r, y - r, cxa + r, y + r, outline="#1d3aa8", width=2)
            arco = c.create_arc(cxa - r, y - r, cxa + r, y + r, start=0, extent=70, style="arc",
                                outline=config.AZUL_CLARO, width=3)
            segs = [c.create_rectangle(x0 + s * sw + 1, y - 16, x0 + (s + 1) * sw - 2, y + 16,
                                       fill=APAGADO, outline="") for s in range(SEG)]
            pct = c.create_text(x1 + 18, y - 8, anchor="w", fill=config.BLANCO, text="0%",
                                font=("Segoe UI", 15, "bold"))
            det = c.create_text(x1 + 18, y + 14, anchor="w", fill="#9fb0ff", text="",
                                font=("Segoe UI", 9))
            self._filas.append({"clave": clave, "arco": arco, "segs": segs, "cols": [APAGADO] * SEG,
                                "pct": pct, "det": det, "t_pct": "0%", "t_det": "", "fase": i * 90})

    def _tick(self):
        if self.winfo_ismapped() and self._filas:
            c, t = self.canvas, time.time()
            if t - self._t_datos > 1.0:
                self._t_datos = t
                self.meta = sistema.leer()
            barrido = (t * 14) % (SEG + 10)             # destello que recorre la barra
            for f in self._filas:
                k = f["clave"]
                pct, det = self.meta[k]
                self.valor[k] += (pct - self.valor[k]) * 0.15      # animación suave
                v = self.valor[k]
                c.itemconfig(f["arco"], start=(t * 200 + f["fase"]) % 360)
                llenos, caliente = v / 100 * SEG, v > 85
                for s in range(SEG):
                    if s < llenos:
                        if abs(s - barrido) < 1.5:
                            col = ROJO_B if caliente else AZUL_B
                        else:
                            col = ROJO if caliente else AZUL
                    else:
                        col = APAGADO
                    if col != f["cols"][s]:
                        c.itemconfig(f["segs"][s], fill=col)
                        f["cols"][s] = col
                tp = f"{v:.0f}%"
                if tp != f["t_pct"]:
                    c.itemconfig(f["pct"], text=tp)
                    f["t_pct"] = tp
                if det != f["t_det"]:
                    c.itemconfig(f["det"], text=det)
                    f["t_det"] = det
        self.after(60, self._tick)
