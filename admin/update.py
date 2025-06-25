import json
import os
import sys
import urllib.request
import shutil
import zipfile

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


def is_running_exe() -> bool:
    """Devuelve True si la aplicación se ejecuta como .exe."""
    return getattr(sys, 'frozen', False)


def ensure_embedded_python() -> None:
    """Extrae el runtime de Python si es necesario."""
    if not is_running_exe():
        return
    runtime = os.path.join('_internal', 'python', 'python.exe')
    if os.path.exists(runtime):
        return
    zip_path = os.path.join('_internal', 'python_runtime.zip')
    if os.path.exists(zip_path):
        try:
            os.makedirs(os.path.join('_internal', 'python'), exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(os.path.join('_internal', 'python'))
            log('Runtime de Python extraído en _internal/python')
        except Exception as e:
            log(f'No se pudo extraer runtime: {e}', level='ERROR')
    else:
        log('python_runtime.zip no encontrado', level='WARNING')

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


def aplicar_actualizacion(zip_path: str) -> bool:
    """Intenta aplicar una actualización ZIP con rollback automático."""
    backup_dir = '_backup'
    try:
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        os.makedirs(backup_dir, exist_ok=True)
        for item in os.listdir('.'):
            if item.startswith('_'):
                continue
            shutil.move(item, os.path.join(backup_dir, item))
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall('.')
        log('Actualización aplicada correctamente')
        return True
    except Exception as e:
        log(f'Error aplicando actualización: {e}', level='ERROR')
        if os.path.exists(backup_dir):
            for item in os.listdir(backup_dir):
                shutil.move(os.path.join(backup_dir, item), item)
        return False

import zipfile
import requests


def subir_version():
    """Comprime el proyecto y lo sube a un servidor indicado en update_config.json"""
    cfg_path = 'update_config.json'
    if not os.path.exists(cfg_path):
        log('update_config.json no encontrado', level='ERROR')
        return
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    url = cfg.get('url')
    version_file = cfg.get('version_file', 'version.json')
    zip_name = 'version_upload.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for folder, _, files in os.walk('.'):
            for file in files:
                if '.git' in folder:
                    continue
                path = os.path.join(folder, file)
                zf.write(path, os.path.relpath(path, '.'))
    try:
        with open(zip_name, 'rb') as fzip:
            requests.post(url, files={'file': fzip})
        log('Versión subida correctamente')
    except Exception as e:
        log(f'Error al subir versión: {e}', level='ERROR')
    finally:
        if os.path.exists(zip_name):
            os.remove(zip_name)
