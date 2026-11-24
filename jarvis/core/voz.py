"""Texto a voz (Jarvis habla) y reconocimiento de voz (Jarvis escucha)."""
import re
import queue
import threading
import time
import pyttsx3
import speech_recognition as sr
import config


class Voz:
    """Jarvis hablando. `hablando` está activo mientras suena la voz (la UI lo usa para animar)."""

    def __init__(self, on_error=print):
        self.cola = queue.Queue()
        self.hablando = threading.Event()
        self.on_error = on_error
        threading.Thread(target=self._hilo, daemon=True).start()

    @staticmethod
    def _voz_es(eng):
        for v in eng.getProperty("voices"):
            datos = (v.name + " " + str(v.id)).lower()
            if any(k in datos for k in ("spanish", "español", "es-", "helena", "sabina", "pablo")):
                return v.id
        return None

    def _hilo(self):
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except ImportError:
            pass
        while True:
            texto, listo = self.cola.get()
            self.hablando.set()
            try:
                eng = pyttsx3.init()
                voz = self._voz_es(eng)
                if voz:
                    eng.setProperty("voice", voz)
                eng.setProperty("rate", 170)
                eng.say(texto)
                eng.runAndWait()
                eng.stop()
            except Exception as e:
                self.on_error(f"Error de voz: {e}")
            finally:
                if self.cola.empty():
                    self.hablando.clear()
                listo.set()

    def decir(self, texto, esperar=True):
        limpio = re.sub(r"[*_`#>]", "", texto)
        listo = threading.Event()
        self.cola.put((limpio, listo))
        if esperar:
            listo.wait()


class Oido:
    """Bucle de micrófono. Llama on_texto(str) cada vez que entiende algo."""

    def __init__(self, voz, on_texto, on_estado, on_log):
        self.voz, self.on_texto, self.on_estado, self.on_log = voz, on_texto, on_estado, on_log
        self.rec = sr.Recognizer()
        self.activo = threading.Event()

    def alternar(self):
        if self.activo.is_set():
            self.apagar()
        else:
            self.encender()

    def encender(self):
        if not self.activo.is_set():
            self.activo.set()
            threading.Thread(target=self._bucle, daemon=True).start()

    def apagar(self):
        self.activo.clear()
        self.on_estado("En espera")

    def _bucle(self):
        """Abre el micrófono UNA vez y lo mantiene (antes se reabría y recalibraba cada frase)."""
        try:
            with sr.Microphone() as fuente:
                self.rec.adjust_for_ambient_noise(fuente, duration=0.8)
                while self.activo.is_set():
                    if self.voz.hablando.is_set():          # no escucharse a sí mismo
                        time.sleep(0.2)
                        continue
                    self.on_estado("Escuchando...")
                    try:
                        audio = self.rec.listen(fuente, timeout=3, phrase_time_limit=12)
                    except sr.WaitTimeoutError:
                        continue
                    try:
                        self.on_estado("Procesando voz...")
                        texto = self.rec.recognize_google(audio, language=config.IDIOMA_VOZ)
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        self.on_log(f"Falló el reconocimiento de voz (¿internet?): {e}")
                        time.sleep(1)
                        continue
                    if texto and self.activo.is_set():
                        self.on_texto(texto)
        except OSError as e:
            self.on_log(f"No pude abrir el micrófono: {e}")
            self.activo.clear()
        self.on_estado("En espera")
