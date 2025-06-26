import os
import json
from typing import Tuple

import requests
from logger import log

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'update_config.json')
VERSION_FILE = os.path.join(os.path.dirname(__file__), 'version.txt')


def _cargar_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f'Error leyendo update_config.json: {e}', level='ERROR')
        return {}


def _leer_version_local() -> str:
    if not os.path.exists(VERSION_FILE):
        return '0.0.0'
    with open(VERSION_FILE, 'r', encoding='utf-8') as f:
        contenido = f.read().strip()
    if contenido.startswith('version='):
        contenido = contenido.split('=', 1)[1]
    return contenido.strip()


def _leer_version_remota(url: str) -> str:
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    texto = resp.text.strip()
    if texto.startswith('version='):
        texto = texto.split('=', 1)[1]
    return texto.strip()


def _parse_version(ver: str) -> Tuple[int, ...]:
    try:
        return tuple(int(p) for p in ver.split('.'))
    except ValueError:
        return tuple()


def hay_actualizacion_disponible() -> bool:
    """Retorna True si hay una versi\u00f3n remota m\u00e1s reciente."""
    cfg = _cargar_config()
    if not cfg.get('check_updates', True):
        return False

    local = _leer_version_local()
    url = cfg.get('version_url')
    if not url:
        log('version_url no configurado en update_config.json', level='WARNING')
        return False

    try:
        remote = _leer_version_remota(url)
    except Exception as e:
        log(f'No se pudo verificar actualizaciones: {e}', level='WARNING')
        return False

    return _parse_version(remote) > _parse_version(local)


def descargar_e_instalar_actualizacion() -> bool:
    """Descarga el ZIP de la nueva versión e instala los archivos.

    Devuelve True si la actualización se completó correctamente."""
    cfg = _cargar_config()
    zip_url = cfg.get('zip_url')
    if not zip_url:
        log('zip_url no configurado en update_config.json', level='ERROR')
        return False

    import tempfile
    import zipfile
    import shutil

    log('Descargando actualización...')
    try:
        resp = requests.get(zip_url, stream=True, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        log(f'Error al descargar actualización: {e}', level='ERROR')
        return False

    with tempfile.TemporaryDirectory(prefix='update_') as tmp_dir:
        zip_path = os.path.join(tmp_dir, 'update.zip')
        with open(zip_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        log('Descomprimiendo actualización...')
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmp_dir)
        except Exception as e:
            log(f'Error al descomprimir actualización: {e}', level='ERROR')
            return False

        # Buscar carpeta raíz extraída
        extracted_root = tmp_dir
        subdirs = [d for d in os.listdir(tmp_dir)
                   if os.path.isdir(os.path.join(tmp_dir, d))]
        if len(subdirs) == 1:
            extracted_root = os.path.join(tmp_dir, subdirs[0])

        def should_skip(rel_path: str) -> bool:
            rel_norm = rel_path.replace('\\', '/')
            if rel_norm.startswith('logs/'):
                return True
            if rel_norm.startswith('config/') and os.path.splitext(rel_norm)[1] in ('.txt', '.json'):
                return True
            return False

        log('Copiando archivos...')
        try:
            for root_dir, dirs, files in os.walk(extracted_root):
                rel_dir = os.path.relpath(root_dir, extracted_root)
                if rel_dir == '.':
                    rel_dir = ''
                # Modificar dirs in-place para evitar recorrer las ignoradas
                dirs[:] = [d for d in dirs if not should_skip(os.path.join(rel_dir, d))]
                for file in files:
                    rel_path = os.path.normpath(os.path.join(rel_dir, file))
                    if should_skip(rel_path):
                        continue
                    dest = os.path.join('.', rel_path)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy2(os.path.join(root_dir, file), dest)
        except Exception as e:
            log(f'Error copiando archivos: {e}', level='ERROR')
            return False

    log('Actualización completada.')
    return True
