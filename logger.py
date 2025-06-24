import os
import getpass
from datetime import datetime

LOG_PATH = os.path.join('logs', 'panel.log')
os.makedirs('logs', exist_ok=True)

def log(message: str, level: str = 'INFO') -> None:
    user = getpass.getuser()
    timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    entry = f"{timestamp} [{level}] ({user}) {message}\n"
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(entry)

import csv
USUARIOS_LOG = os.path.join('logs', 'usuarios.csv')


def log_usuario(accion: str, usuario: str = None, resultado: str = 'OK') -> None:
    """Registra acciones de usuario en logs/usuarios.csv"""
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
