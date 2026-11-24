"""Ventana principal: junta pantallas, voz, cámara, comandos y Ollama."""
import queue
import threading
import tkinter as tk
import config
from core import cerebro, comandos
from core.camara import Camara
from core.voz import Voz, Oido
from ui.mini_camara import MiniCamara
from ui.pantalla_chat import PantallaChat
from ui.pantalla_inicio import PantallaInicio
from ui.pantalla_rendimiento import PantallaRendimiento

SALIDA = ("salir", "apágate", "apagate", "adiós", "adios")


class JarvisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S. UNEFA")
        self.root.geometry("1000x620")
        self.root.minsize(820, 540)
        self.root.config(bg=config.AZUL_FONDO)

        self.voz = Voz(on_error=self.log)
        self.oido = Oido(self.voz, lambda t: self.root.after(0, self.enviar, t),
                         self.set_estado, self.log)
        self.camara = Camara(self.log, lambda: self.root.after(0, self._camara_cerrada))
        self.mini = MiniCamara(self.root, self.camara, self.restaurar)

        cont = tk.Frame(self.root, bg=config.AZUL_FONDO)
        cont.pack(fill="both", expand=True)
        cont.grid_rowconfigure(0, weight=1)
        cont.grid_columnconfigure(0, weight=1)
        self.inicio = PantallaInicio(cont, self)
        self.chat = PantallaChat(cont, self)
        self.rend = PantallaRendimiento(cont, self)
        self.pantallas = {"inicio": self.inicio, "chat": self.chat, "rendimiento": self.rend}
        for p in self.pantallas.values():
            p.grid(row=0, column=0, sticky="nsew")

        comandos.hooks.update({
            "log": self.log,
            "camara": lambda v: self.root.after(0, self.set_camara, v),
            "manos": lambda v: setattr(self.camara, "manos_on", v),
            "pantalla": lambda n: self.root.after(0, self.mostrar, n),
            "youtube_abierto": lambda _: self.root.after(0, self._youtube_abierto),
        })
        self.mostrar("inicio")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)
        self._refrescar()

    # ---------- utilidades ----------
    def log(self, texto):
        print("[JARVIS]", texto)
        self.root.after(0, self.inicio.set_estado, texto)

    def set_estado(self, texto):
        self.root.after(0, self.inicio.set_estado, texto)

    def en_ui(self, f, *a):
        """Ejecuta f en el hilo de la interfaz y devuelve su resultado (llamar desde hilos)."""
        q = queue.Queue()
        self.root.after(0, lambda: q.put(f(*a)))
        return q.get()

    def mostrar(self, nombre):
        self.pantallas[nombre].tkraise()

    # ---------- cámara / micrófono ----------
    def alternar_camara(self):
        self.set_camara(not self.camara.activa.is_set())

    def set_camara(self, activar):
        if activar and not self.camara.activa.is_set():
            self.camara.encender()
            self.mini.mostrar(minimizar=False)
            if config.AUTO_MIC_CON_CAMARA and not self.oido.activo.is_set():
                self.alternar_microfono()
            self.voz.decir("Cámara activada, señor.", esperar=False)
        elif not activar and self.camara.activa.is_set():
            self.camara.apagar()

    def _camara_cerrada(self):
        self.mini.ocultar()
        self.root.deiconify()

    def alternar_microfono(self):
        self.oido.alternar()
        self.chat.set_mic(self.oido.activo.is_set())

    def _youtube_abierto(self):
        """YouTube se abrió: cámara pequeña siempre visible (y micrófono para pasar canciones)."""
        self.set_camara(True)
        self.mini.mostrar(minimizar=config.MINIMIZAR_AL_ABRIR_YOUTUBE)

    def restaurar(self):
        self.mini.ocultar()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _refrescar(self):
        self.mini.refrescar()
        self.root.after(50, self._refrescar)

    # ---------- conversación ----------
    def enviar(self, texto):
        """Mensaje del usuario (escrito o por voz). Se llama desde el hilo de la interfaz."""
        self.chat.agregar_usuario(texto)
        threading.Thread(target=self._procesar, args=(texto,), daemon=True).start()

    def _procesar(self, texto):
        if any(p in texto.lower() for p in SALIDA):
            self._responder("Desconectando el micrófono. Que tenga un buen día, señor.")
            self.oido.apagar()
            self.root.after(0, self.chat.set_mic, False)
            return
        r = comandos.comando_local(texto)
        if r:
            frase, accion = r
            self._responder(frase)
            if accion:
                accion()
            return
        # Ollama, con la respuesta apareciendo mientras se escribe
        self.set_estado("Pensando...")
        burbuja = self.en_ui(self.chat.nueva_burbuja_jarvis)
        primero = [True]

        def trozo(t):
            self.root.after(0, self.chat.anexar, burbuja, t, primero[0])
            primero[0] = False

        resp = cerebro.pensar(texto, on_trozo=trozo)
        self.root.after(0, self.chat.poner, burbuja, resp)
        self.set_estado("")
        self.voz.decir(resp, esperar=False)

    def _responder(self, frase):
        self.en_ui(self.chat.nueva_burbuja_jarvis, frase)
        self.voz.decir(frase)

    # ---------- ciclo de vida ----------
    def cerrar(self):
        self.oido.apagar()
        self.camara.apagar()
        self.root.after(400, self.root.destroy)

    def run(self):
        self.voz.decir("Sistemas en línea. ¿Qué desea, señor?", esperar=False)
        self.root.mainloop()
