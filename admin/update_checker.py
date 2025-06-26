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
