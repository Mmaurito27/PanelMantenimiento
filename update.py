import json
import os
import urllib.request

from logger import log

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
