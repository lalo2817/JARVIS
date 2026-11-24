"""Comandos locales por voz o texto (sin pasar por Ollama).
comando_local(texto) -> (frase_de_jarvis, accion | None)  o  None si no es un comando."""
import re
import time
import config
from core import apps, youtube

# La interfaz registra aquí sus funciones: camara(bool), manos(bool), pantalla(str), log(str)
hooks = {}

VERBOS_REPRODUCIR = r"\b(reproduce|reproduzca|reproducir|ponme|pon|toca)\b"
RELLENO = (r"\b(reproduce|reproduzca|reproducir|ponme|pon|toca|busca|buscar|en youtube|de youtube|"
           r"youtube|esta canción|esta cancion|la canción|la cancion|canción|cancion|el video de|"
           r"un video de|video de|el video|la música de|la musica de|música de|musica de|"
           r"buscame|búscame)\b")
BORRAR = (r"\b(borra|borrar|borrame|bórrame|elimina|eliminar|suprime|suprimir|desinstala|"
          r"desinstalar|formatea|formatear|vacia|vacía|vaciar|destruye)\b")
ARTICULOS = r"(?:(?:la|el|las|los|mi|una|un|aplicaci[oó]n|app|programa|de)\s+)*"


def normalizar(texto):
    t = texto.lower()
    return re.sub(r"\b(?:you|yu|iu|ju|u)\s*-?\s*tub[e]?\b", "youtube", t)


def extraer_consulta(texto):
    return " ".join(re.sub(RELLENO, " ", texto, flags=re.IGNORECASE).split())


def comando_local(texto):
    t = normalizar(texto)

    # --- Seguridad: Jarvis no borra nada, nunca ---
    if re.search(BORRAR, t):
        return ("Por seguridad no tengo permitido borrar ni desinstalar nada, señor.", None)

    abrir = re.search(r"\b[aá]br(?:e|a|ir|eme|ame|ime)\b", t)
    cerrar = re.search(r"\bc(?:ierr|err)\w*", t)

    # --- Controles de YouTube por voz ---
    if re.search(r"\b(siguiente|next|pasa|pasar|salta|saltar|cambia)\b", t) and \
            re.search(r"\b(canci[oó]n|tema|video|v[ií]deo|siguiente|next)\b", t):
        return ("Pasando a la siguiente, señor.", youtube.siguiente)
    if re.search(r"\b(anterior|regresa|vuelve|atr[aá]s)\b", t) and \
            re.search(r"\b(canci[oó]n|tema|video|v[ií]deo|anterior)\b", t):
        return ("Regresando, señor.", youtube.anterior)
    if re.search(r"\b(pausa|pausar|pausa la|det[eé]n|continua|contin[uú]a|reanuda|play)\b", t) and \
            re.search(r"\b(m[uú]sica|canci[oó]n|video|v[ií]deo|pausa|pausar|reanuda|play)\b", t):
        return ("Entendido, señor.", youtube.pausa)
    if cerrar and "youtube" in t:
        return ("Cerrando YouTube, señor.", youtube.cerrar)

    # --- Reproducir / abrir YouTube ---
    verbo_buscar = r"\b(busca|buscar|buscame|búscame)\b"
    quiere_reproducir = (re.search(VERBOS_REPRODUCIR, t)
                         or ("youtube" in t and re.search(verbo_buscar, t))
                         or re.search(verbo_buscar + r".*\b(m[uú]sica|canci[oó]n|v[ií]deo)\b", t))
    if quiere_reproducir:
        consulta = extraer_consulta(t)
        if consulta:
            return (f"Buscando {consulta} en YouTube, señor.",
                    lambda c=consulta: _yt(lambda: youtube.reproducir(c, hooks.get("log", print))))
    if "youtube" in t and (abrir or quiere_reproducir):
        return ("Abriendo YouTube, señor.", lambda: _yt(youtube.abrir))

    # --- Cámara / gestos / pantallas ---
    if "cámara" in t or "camara" in t:
        if re.search(r"\b(activa|enciende|prende|abre)\w*", t):
            return ("Activando la cámara, señor.", lambda: _hook("camara", True))
        if re.search(r"\b(apaga|desactiva|cierra)\w*", t):
            return ("Apagando la cámara, señor.", lambda: _hook("camara", False))
    if re.search(r"\bgestos|\bmanos\b", t):
        if re.search(r"\b(desactiva|apaga|quita)\w*", t):
            return ("Gestos desactivados, señor.", lambda: _hook("manos", False))
        if re.search(r"\b(activa|enciende|prende)\w*", t):
            return ("Gestos activados, señor.", lambda: _hook("manos", True))
    if re.search(r"\b(rendimiento|recursos)\b", t):
        return ("Mostrando el rendimiento, señor.", lambda: _hook("pantalla", "rendimiento"))

    # --- Hora ---
    if "hora" in t and ("qué" in t or "que" in t):
        return ("Son las " + time.strftime("%I:%M %p") + ", señor.", None)

    # --- Abrir / cerrar cualquier app ---
    if abrir:
        m = re.search(r"\b[aá]br(?:e|a|ir|eme|ame|ime)\s+" + ARTICULOS + r"(.+)$", t)
        if m and m.group(1).strip():
            n = m.group(1).strip()
            return (f"Entendido, señor. Abriendo {n}.", lambda: _abrir_app(n))
    if cerrar:
        m = re.search(r"\bc(?:ierr|err)\w*\s+" + ARTICULOS + r"(.+)$", t)
        if m and m.group(1).strip():
            n = m.group(1).strip()
            return (f"Entendido, señor. Cerrando {n}.", lambda: apps.cerrar(n))
    return None


def _abrir_app(nombre):
    if not apps.abrir(nombre):
        hooks.get("log", print)(f"No encontré la app '{nombre}'.")


def _hook(nombre, valor):
    f = hooks.get(nombre)
    if f:
        f(valor)


def _yt(accion):
    _hook("youtube_abierto", None)   # la UI minimiza y muestra la cámara pequeña
    accion()
