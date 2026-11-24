"""Ventanita flotante con tu cámara (siempre encima, arrastrable, doble clic = volver a Jarvis)."""
import tkinter as tk
from PIL import Image, ImageTk
import config


class MiniCamara:
    def __init__(self, root, camara, al_restaurar):
        self.root, self.camara, self.al_restaurar = root, camara, al_restaurar
        self.win = None
        self.label = None
        self._arr = (0, 0)
        self._ultimo = None

    def visible(self):
        return self.win is not None and self.win.winfo_exists() and self.win.state() != "withdrawn"

    def mostrar(self, minimizar=False):
        if self.win is None or not self.win.winfo_exists():
            self.win = tk.Toplevel(self.root)
            self.win.overrideredirect(True)
            self.win.config(bg=config.AZUL_CLARO)
            self.label = tk.Label(self.win, bg="black", bd=0)
            self.label.pack(padx=2, pady=2)
            self.label.bind("<Double-Button-1>", lambda e: self.al_restaurar())
            self.label.bind("<ButtonPress-1>", lambda e: setattr(self, "_arr", (e.x, e.y)))
            self.label.bind("<B1-Motion>", self._mover)
            sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
            self.win.geometry(f"+{sw - config.MINI_SIZE[0] - 30}+{sh - config.MINI_SIZE[1] - 90}")
        else:
            self.win.deiconify()
        self.win.attributes("-topmost", True)
        self.win.lift()
        if minimizar:
            self.root.iconify()

    def ocultar(self):
        if self.win is not None and self.win.winfo_exists():
            self.win.withdraw()

    def _mover(self, e):
        self.win.geometry(f"+{self.win.winfo_x() + e.x - self._arr[0]}+{self.win.winfo_y() + e.y - self._arr[1]}")

    def refrescar(self):
        frame = self.camara.frame
        if frame is None or frame is self._ultimo or not self.visible():
            return
        self._ultimo = frame
        img = ImageTk.PhotoImage(Image.fromarray(frame).resize(config.MINI_SIZE, Image.BILINEAR))
        self.label.config(image=img)
        self.label.image = img
