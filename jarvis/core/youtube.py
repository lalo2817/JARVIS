"""YouTube: abrir, reproducir, pasar canciones y cerrar (solo la pestaña de YouTube)."""
import time
import urllib.parse
import webbrowser


def _teclas(*teclas):
    import pyautogui
    pyautogui.hotkey(*teclas)


def _enfocar():
    """Trae al frente la ventana del navegador que tiene YouTube."""
    try:
        import pygetwindow as gw
        for v in gw.getWindowsWithTitle("YouTube"):
            if v.isMinimized:
                v.restore()
            v.activate()
            time.sleep(0.25)
            return True
    except Exception:
        pass
    return False


def abrir():
    webbrowser.open("https://www.youtube.com")


def reproducir(consulta, on_error=print):
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True,
                               "extract_flat": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(f"ytsearch1:{consulta}", download=False)
        vid = info["entries"][0]["id"]
        # list=RD<id> = mix automático: así "siguiente" siempre tiene otra canción
        webbrowser.open(f"https://www.youtube.com/watch?v={vid}&list=RD{vid}")
    except Exception as e:
        on_error(f"Error buscando en YouTube: {e}")
        webbrowser.open("https://www.youtube.com/results?search_query="
                        + urllib.parse.quote(consulta))


def siguiente():
    if _enfocar():
        _teclas("shift", "n")


def anterior():
    if _enfocar():
        _teclas("shift", "p")


def pausa():
    if _enfocar():
        import pyautogui
        pyautogui.press("k")


def cerrar():
    if _enfocar():
        _teclas("ctrl", "w")
