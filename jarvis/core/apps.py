"""Abrir y cerrar aplicaciones. Libertad total para abrir; NO hay ninguna función de borrar."""
import os
import re
import glob
import difflib
import subprocess
import unicodedata
import config

try:
    import psutil
except ImportError:
    psutil = None


def _norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").strip()


def _escanear_inicio():
    """Busca todos los accesos directos del menú Inicio: {nombre_normalizado: ruta}."""
    carpetas = [
        os.path.join(os.environ.get("ProgramData", ""), r"Microsoft\Windows\Start Menu\Programs"),
        os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
    ]
    apps = {}
    for c in carpetas:
        for ext in ("lnk", "url"):
            for ruta in glob.glob(os.path.join(c, "**", f"*.{ext}"), recursive=True):
                nombre = _norm(os.path.splitext(os.path.basename(ruta))[0])
                if "uninstall" in nombre or "desinstalar" in nombre:   # nada de desinstaladores
                    continue
                apps.setdefault(nombre, ruta)
    return apps


_cache = None


def _apps_instaladas():
    global _cache
    if _cache is None:
        _cache = _escanear_inicio()
    return _cache


def _buscar(nombre):
    """Devuelve (nombre_real, ruta) de la app que mejor coincide, o None."""
    n = _norm(nombre)
    for k, exe in config.APPS_RAPIDAS.items():
        if _norm(k) == n:
            return k, exe
    inst = _apps_instaladas()
    if n in inst:
        return n, inst[n]
    for k, ruta in inst.items():                      # "chrome" -> "google chrome"
        if n in k or (len(k) > 3 and k in n):
            return k, ruta
    cerca = difflib.get_close_matches(n, list(inst), n=1, cutoff=0.7)
    return (cerca[0], inst[cerca[0]]) if cerca else None


def abrir(nombre):
    """Abre una app. Devuelve True si pudo."""
    if not re.fullmatch(r"[\w .+\-]{1,60}", nombre):  # sin rutas ni símbolos raros
        return False
    hallada = _buscar(nombre)
    try:
        if hallada:
            os.startfile(hallada[1])
        else:
            os.startfile(nombre.strip())              # App Paths de Windows (chrome, spotify...)
        return True
    except Exception:
        return False


def cerrar(nombre):
    """Cierra una app de forma normal (sin /f). Nunca toca procesos protegidos."""
    if psutil is None:
        return False
    n = _norm(nombre)
    claves = {t for t in re.split(r"\W+", n) if len(t) >= 4}
    for k, exe in config.APPS_RAPIDAS.items():
        if _norm(k) == n:
            claves.add(_norm(exe).replace(".exe", ""))
    exes = set()
    for p in psutil.process_iter(["name"]):
        nom = (p.info["name"] or "").lower()
        if nom in config.PROCESOS_PROTEGIDOS:
            continue
        if any(c in _norm(nom) for c in claves):
            exes.add(nom)
    for exe in exes:
        subprocess.run(["taskkill", "/im", exe], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    return bool(exes)
