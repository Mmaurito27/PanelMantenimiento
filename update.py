import json
import os
import sys
import urllib.request

from logger import log
from config import CONFIG, CONFIG_FILE


def detectar_modo_ejecucion() -> str:
    """Determina si el ejecutable se ejecuta de forma portable o fija."""
    exe_path = os.path.abspath(sys.argv[0])
    desktop = os.path.expanduser('~/Desktop')
    if exe_path.startswith(desktop) or 'Desktop' in exe_path:
        modo = 'portable'
    else:
        modo = 'fija'

    # Actualiza config en memoria y archivo
    CONFIG['instalacion'] = modo
    actualizar_entorno(modo)
    log(f"Modo de ejecuci\u00f3n: {modo}")
    return modo


def actualizar_entorno(modo: str) -> None:
    """Escribe el modo de instalaci\u00f3n en entorno.txt."""
    lineas = []
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    escrito = False
    for i, linea in enumerate(lineas):
        if linea.startswith('instalacion='):
            lineas[i] = f'instalacion={modo}\n'
            escrito = True
            break
    if not escrito:
        lineas.append(f'instalacion={modo}\n')
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lineas)

GITHUB_JSON = "https://raw.githubusercontent.com/example/repo/master/version.json"


def buscar_actualizaciones(version_actual: str, offline_path="updates/latest.zip"):
    """Verifica en GitHub si hay una versión nueva y descarga el ZIP."""
    try:
        with urllib.request.urlopen(GITHUB_JSON, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            nueva = data.get("version")
            zip_url = data.get("zip_url")
    except Exception as e:
        log(f"No se pudo verificar actualizaciones online: {e}", level="WARNING")
        return

    if nueva and nueva != version_actual and zip_url:
        try:
            with urllib.request.urlopen(zip_url) as r, open("update.zip", "wb") as f:
                f.write(r.read())
            log("Se descargó actualización nueva")
            # TODO: descomprimir y reemplazar archivos
        except Exception as e:
            log(f"Error al descargar actualización: {e}", level="ERROR")
    else:
        log("No hay actualizaciones disponibles")
