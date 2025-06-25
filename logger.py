import os
import getpass
from datetime import datetime
from colorama import Fore, Style, init

init()

LOG_PATH = os.path.join('logs', 'panel.log')
os.makedirs('logs', exist_ok=True)

def log(message: str, level: str = 'INFO') -> None:
    user = getpass.getuser()
    timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    entry = f"{timestamp} [{level}] ({user}) {message}\n"
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(entry)
    color = {
        'INFO': Fore.WHITE,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
    }.get(level, Fore.WHITE)
    print(color + entry.strip() + Style.RESET_ALL)

import csv
USUARIOS_LOG = os.path.join('logs', 'usuarios.csv')


def log_usuario_csv(accion: str, usuario: str = None, resultado: str = 'OK') -> None:
    """Registra acciones de usuario en logs/usuarios.csv (mantenido por compatibilidad)."""
    if usuario is None:
        usuario = getpass.getuser()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    os.makedirs('logs', exist_ok=True)
    nuevo = not os.path.exists(USUARIOS_LOG)
    with open(USUARIOS_LOG, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if nuevo:
            writer.writerow(['timestamp', 'usuario', 'accion', 'resultado'])
        writer.writerow([timestamp, usuario, accion, resultado])


def log_usuario(usuario: str, accion: str) -> None:
    """Registra acciones por usuario en logs/usuarios/<usuario>.log"""
    from session import area_actual  # import aquí para evitar ciclos
    dir_path = os.path.join('logs', 'usuarios')
    os.makedirs(dir_path, exist_ok=True)
    archivo = os.path.join(dir_path, f'{usuario}.log')
    timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    linea = f"{timestamp} [{area_actual}] {accion}\n"
    with open(archivo, 'a', encoding='utf-8') as f:
        f.write(linea)
