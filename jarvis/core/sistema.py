"""Datos de rendimiento: RAM, almacenamiento y CPU."""
import os
import psutil


def leer():
    ram = psutil.virtual_memory()
    raiz = os.path.abspath(os.sep)
    disco = psutil.disk_usage(raiz)
    gb = 1024 ** 3
    return {
        "ram": (ram.percent, f"{ram.used / gb:.1f} / {ram.total / gb:.1f} GB"),
        "disco": (disco.percent, f"{disco.used / gb:.0f} / {disco.total / gb:.0f} GB"),
        "cpu": (psutil.cpu_percent(), f"{psutil.cpu_count(logical=True)} núcleos"),
    }
