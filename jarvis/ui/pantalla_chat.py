"""Pantalla de chat: cara animada de Jarvis + burbujas + barra de mensaje."""
import math
import random
import time
import tkinter as tk
import config
from ui import recursos

PLACEHOLDER = "DE QUE QUIERE HABLAR SEÑOR"
TINTA = "#1a2a9c"
# Posición de la cara dentro del marco HUD (0 a 1). Ajusta si no te cuadra.
OJO_IZQ, OJO_DER, OJO_Y = 0.40, 0.50, 0.46
BOCA_X, BOCA_Y = 0.45, 0.64
CARA = 170


class PantallaChat(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=config.BLANCO)
        self.app = app
        self._ph = True
        self._parpadeo = time.time() + 3

        # ----- barra inferior (se empaqueta primero para que quede abajo) -----
        self.barra = tk.Canvas(self, height=84, bg=config.BLANCO, highlightthickness=0)
        self.barra.pack(side="bottom", fill="x")
        self.entrada = tk.Entry(self.barra, font=("Segoe UI", 12), bg=config.AZUL_INPUT,
                                fg="#dfe4ff", bd=0, relief="flat", insertbackground=config.BLANCO)
        self.entrada.insert(0, PLACEHOLDER)
        self.entrada.bind("<FocusIn>", self._foco_in)
        self.entrada.bind("<FocusOut>", self._foco_out)
        self.entrada.bind("<Return>", self._enviar)
        self.btn_mic = tk.Label(self.barra, text="🎤", font=("Segoe UI Emoji", 15), cursor="hand2",
                                bg=config.AZUL_INPUT, fg=config.BLANCO)
        self.btn_mic.bind("<Button-1>", lambda e: app.alternar_microfono())
        self.barra.bind("<Configure>", self._dibujar_barra)

        # ----- parte superior: cara + título -----
        top = tk.Frame(self, bg=config.BLANCO, height=CARA)
        top.pack(side="top", fill="x")
        top.pack_propagate(False)
        self.cara = tk.Canvas(top, width=CARA, height=CARA, bg=config.BLANCO, highlightthickness=0)
        self.cara.pack(side="left")
        self._marco = recursos.tk_img("marco_hud.png", (CARA, CARA))
        self._crear_cara()
        tk.Label(top, text="JARVIS UNEFA", font=("Segoe UI", 22, "bold"), fg="black",
                 bg=config.BLANCO).pack(side="right", padx=30, anchor="n", pady=14)
        volver = tk.Label(top, text="◀ INICIO", font=("Segoe UI", 11, "bold"), fg=config.AZUL_BURBUJA,
                          bg=config.BLANCO, cursor="hand2")
        volver.place(relx=1.0, x=-34, y=74, anchor="ne")
        volver.bind("<Button-1>", lambda e: app.mostrar("inicio"))

        # ----- lista de mensajes con scroll -----
        self.lienzo = tk.Canvas(self, bg=config.BLANCO, highlightthickness=0)
        self.lienzo.pack(side="top", fill="both", expand=True)
        self.interior = tk.Frame(self.lienzo, bg=config.BLANCO)
        self._win = self.lienzo.create_window((0, 0), window=self.interior, anchor="nw")
        self.lienzo.bind("<Configure>", lambda e: self.lienzo.itemconfig(self._win, width=e.width))
        self.interior.bind("<Configure>",
                           lambda e: self.lienzo.configure(scrollregion=self.lienzo.bbox("all")))
        self.bind_all("<MouseWheel>", self._rueda)

    # ---------- barra ----------
    def _dibujar_barra(self, e):
        b, w = self.barra, e.width
        b.delete("all")
        recursos.rect_redondeado(b, 6, 8, w - 6, 80, 30, fill=config.AZUL_BARRA, outline="")
        recursos.rect_redondeado(b, 26, 20, w - 26, 68, 22, fill=config.AZUL_INPUT, outline="")
        b.create_window(48, 44, window=self.entrada, anchor="w", width=max(w - 170, 100))
        b.create_window(w - 62, 44, window=self.btn_mic, anchor="center")

    def _foco_in(self, e):
        if self._ph:
            self.entrada.delete(0, "end")
            self.entrada.config(fg=config.BLANCO)
            self._ph = False

    def _foco_out(self, e):
        if not self.entrada.get().strip():
            self.entrada.delete(0, "end")
            self.entrada.insert(0, PLACEHOLDER)
            self.entrada.config(fg="#dfe4ff")
            self._ph = True

    def _enviar(self, e=None):
        texto = self.entrada.get().strip()
        if self._ph or not texto:
            return
        self.entrada.delete(0, "end")
        self.app.enviar(texto)

    def set_mic(self, activo):
        self.btn_mic.config(fg="#34d399" if activo else config.BLANCO)

    # ---------- mensajes ----------
    def _rueda(self, e):
        if self.winfo_ismapped():
            self.lienzo.yview_scroll(int(-e.delta / 120) * 2, "units")

    def _burbuja(self, texto, usuario):
        fila = tk.Frame(self.interior, bg=config.BLANCO)
        fila.pack(fill="x", padx=24, pady=6)
        lbl = tk.Label(fila, text=texto, bg=config.AZUL_BURBUJA, fg=config.BLANCO,
                       font=("Segoe UI", 11), justify="left", padx=18, pady=12,
                       wraplength=max(self.winfo_width() - 260, 300))
        lbl.pack(side="right" if usuario else "left")
        self._abajo()
        return lbl

    def _abajo(self):
        self.lienzo.update_idletasks()
        self.lienzo.yview_moveto(1.0)

    def agregar_usuario(self, texto):
        self._burbuja(texto, True)

    def nueva_burbuja_jarvis(self, texto="…"):
        return self._burbuja(texto, False)

    def anexar(self, lbl, trozo, primero=False):
        lbl.config(text=(trozo if primero else lbl.cget("text") + trozo))
        self._abajo()

    def poner(self, lbl, texto):
        lbl.config(text=texto)
        self._abajo()

    # ---------- cara animada (elementos fijos: solo se cambian coordenadas si algo varía) ----------
    def _crear_cara(self):
        c = self.cara
        c.create_image(0, 0, image=self._marco, anchor="nw")
        self._ojos = [c.create_line(0, 0, 0, 0, width=3, fill=TINTA, capstyle="round")
                      for _ in range(2)]
        self._boca = c.create_oval(0, 0, 0, 0, fill=TINTA, outline="")
        self._estado_cara = None
        self._tick()

    def _tick(self):
        t = time.time()
        habla = self.app.voz.hablando.is_set()
        if self.winfo_ismapped():
            if t > self._parpadeo + 0.2:
                self._parpadeo = t + random.uniform(2.5, 5)
            cerrado = self._parpadeo <= t <= self._parpadeo + 0.2
            ab = int(2 + 9 * abs(math.sin(t * 11) * math.cos(t * 6.7))) if habla else 1
            estado = (cerrado, ab)
            if estado != self._estado_cara:
                self._estado_cara = estado
                alto = 1 if cerrado else (9 if habla else 7)
                for x, o in zip((OJO_IZQ, OJO_DER), self._ojos):
                    self.cara.coords(o, x * CARA, OJO_Y * CARA - alto, x * CARA, OJO_Y * CARA + alto)
                bx, by = BOCA_X * CARA, BOCA_Y * CARA
                self.cara.coords(self._boca, bx - 14, by - max(ab, 1.5), bx + 14, by + max(ab, 1.5))
        self.after(80 if habla else 100, self._tick)
