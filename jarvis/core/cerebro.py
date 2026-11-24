"""Cerebro de Jarvis: chat con Ollama (local, sin tokens)."""
import json
import urllib.request
import urllib.error
import config

historial = []


def pensar(prompt, on_trozo=None):
    """Envía el mensaje a Ollama. Si on_trozo está, recibe el texto a medida que llega.
    Devuelve la respuesta completa."""
    historial.append({"role": "user", "content": prompt})
    mensajes = [{"role": "system", "content": config.PERSONALIDAD}] + historial[-10:]
    cuerpo = json.dumps({"model": config.OLLAMA_MODELO, "messages": mensajes,
                         "stream": True,
                         "keep_alive": "30m",
                         "options": {"temperature": 0.6, "num_predict": 160}}).encode()
    req = urllib.request.Request(config.OLLAMA_URL, data=cuerpo,
                                 headers={"Content-Type": "application/json"})
    respuesta = ""
    try:
        with urllib.request.urlopen(req, timeout=config.OLLAMA_TIMEOUT) as r:
            for linea in r:
                if not linea.strip():
                    continue
                datos = json.loads(linea)
                trozo = datos.get("message", {}).get("content", "")
                if trozo:
                    respuesta += trozo
                    if on_trozo:
                        on_trozo(trozo)
                if datos.get("done"):
                    break
    except urllib.error.HTTPError as e:
        historial.pop()
        if e.code == 404:
            return (f"No encuentro el modelo '{config.OLLAMA_MODELO}', señor. "
                    "Revise el nombre en config.py con 'ollama list'.")
        return f"Ollama devolvió el error {e.code}, señor."
    except urllib.error.URLError:
        historial.pop()
        return ("No logro conectarme con Ollama, señor. "
                "Verifique que esté abierto: ejecute 'ollama serve'.")
    except Exception as e:
        historial.pop()
        return f"Ocurrió un error con el modelo, señor: {e}"
    respuesta = respuesta.strip() or "No tengo respuesta para eso, señor."
    historial.append({"role": "assistant", "content": respuesta})
    return respuesta
