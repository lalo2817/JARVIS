"""Configuración general de JARVIS UNEFA. Todo lo que quieras ajustar está aquí."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")

# ---------- Ollama (chat) ----------
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODELO = "llama3.2:1b"   # debe coincidir EXACTO con lo que sale en: ollama list
OLLAMA_TIMEOUT = 120
PERSONALIDAD = (
    "Eres JARVIS, el asistente virtual inteligente, educado y eficiente de Tony Stark. "
    "Responde en español, de forma concisa y elegante, tratando al usuario de 'Señor'. "
    "Máximo 3 frases porque tus respuestas se leen en voz alta. "
    "No uses markdown, asteriscos ni emojis."
)

# ---------- Voz / cámara ----------
IDIOMA_VOZ = "es-VE"            # prueba "es-ES" si no te entiende
CAMARA_INDEX = 0                # si no abre, prueba 1
MINI_SIZE = (260, 195)          # tamaño de la cámara flotante
AUTO_MIC_CON_CAMARA = True      # al activar la cámara se enciende el micrófono
MINIMIZAR_AL_ABRIR_YOUTUBE = True

# ---------- Colores (sacados de tus capturas) ----------
AZUL_FONDO = "#0a1c77"
AZUL_MENU = "#0a1340"
AZUL_BURBUJA = "#3a4bc4"
AZUL_BARRA = "#8a95c8"
AZUL_INPUT = "#6470c4"
AZUL_CLARO = "#2f5bff"
BLANCO = "#ffffff"

# ---------- Gestos con las manos ----------
MANOS_ACTIVAS = True            # se puede cambiar por voz: "activa/desactiva los gestos"
HOLD = 1.2                      # segundos manteniendo un gesto (puño, paz)
COOLDOWN = 1.0                  # segundos entre acciones de gestos
CLIC_PINCH = 0.30               # pulgar+índice pegados = clic
SUAVIZADO = 0.35                # 0-1: más bajo = cursor más suave
MARGEN_CAM = 0.18               # zona de la cámara que cubre toda la pantalla
SWIPE_VEL = 1.6                 # velocidad (anchos de cámara/seg) para cambiar de app
SCROLL_PASO = 60

# ---------- Chasquido ----------
FRASE_SNAP = "SOY IRON MAN"
SNAP_TEXTO_SEG = 3.0
SNAP_PINCH, SNAP_SUELTA = 0.40, 0.55
SNAP_PALMA_MIN, SNAP_PALMA_MAX = 0.80, 1.00
SNAP_VENTANA, SNAP_COOLDOWN = 0.8, 2.5

# ---------- Apps ----------
# Atajos rápidos. Además Jarvis busca cualquier app instalada en el menú Inicio.
APPS_RAPIDAS = {
    "bloc de notas": "notepad.exe",
    "calculadora": "calc.exe",
    "paint": "mspaint.exe",
    "explorador": "explorer.exe",
    "cmd": "cmd.exe",
}
# Procesos que Jarvis JAMÁS cierra
PROCESOS_PROTEGIDOS = {
    "explorer.exe", "system", "svchost.exe", "winlogon.exe", "csrss.exe",
    "python.exe", "pythonw.exe", "py.exe", "taskmgr.exe", "lsass.exe",
}
