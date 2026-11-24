# JARVIS

programa de inteligencia artificial estilo jarvis de iron man primero debes instalar lo siguiente en tu pc

# JARVIS UNEFA

## Instalar (Windows)
    pip install -r requirements.txt
    ollama pull llama3.2        # o el modelo que quieras (cámbialo en config.py -> OLLAMA_MODELO)
    ollama serve                # si no está corriendo ya
    python main.py

## Estructura
    main.py                    arranque
    config.py                  colores, modelo de Ollama, gestos, apps (todo ajustable)
    assets/                    reactor.png, marco_hud.png, icono_chat.png, icono_rendimiento.png
    core/voz.py                Jarvis habla (pyttsx3) y escucha (micrófono)
    core/cerebro.py            chat con Ollama (streaming)
    core/comandos.py           órdenes por voz/texto (apps, YouTube, gestos, pantallas)
    core/apps.py               abrir/cerrar cualquier app (NO hay función de borrar)
    core/youtube.py            abrir, reproducir, siguiente, anterior, pausa, cerrar pestaña
    core/camara.py + hud.py    cámara con HUD y control con las manos
    core/sistema.py            RAM, almacenamiento y CPU
    ui/                        pantallas: inicio, chat, rendimiento, cámara flotante

## Uso
- Toca el reactor: activa cámara + micrófono (ventanita flotante, se arrastra; doble clic = volver).
- Voz: "abre spotify", "cierra chrome", "ponme música de X", "siguiente canción",
  "pausa la música", "cierra youtube", "qué hora es", "muestra el rendimiento",
  "activa/desactiva los gestos", "salir".
- Borrar/eliminar/desinstalar: Jarvis lo rechaza siempre.

## Gestos (cámara)
- Índice solo: mueve el cursor. Pulgar+índice pegados: clic.
- Paz (índice+medio): scroll subiendo/bajando la mano.
- Palma abierta + deslizar rápido: cambia de app (Alt+Tab).
- Puño 1 segundo: play/pausa.
- Chasquido: "SOY IRON MAN".
