import os
import json
import urllib.request
from tkinter import messagebox
from logger import log
from update import aplicar_actualizacion

VERSION_FILE = os.path.join('config', 'version.txt')
UPDATE_INFO_URL = 'https://example.com/panel/version.json'


def get_local_version():
    if not os.path.exists(VERSION_FILE):
        return '0.0.0'
    with open(VERSION_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()


def check_for_update():
    """Verifica si existe una nueva versi\u00f3n y ofrece descargarla."""
    local_ver = get_local_version()
    try:
        with urllib.request.urlopen(UPDATE_INFO_URL, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            remote = data.get('version')
            exe_url = data.get('exe_url')
    except Exception:
        return False

    if remote and exe_url and remote != local_ver:
        if messagebox.askyesno(
            'Actualización',
            f'Se encontró la versión {remote}. ¿Descargar e instalar?'
        ):
            try:
                with urllib.request.urlopen(exe_url) as r, open('update.zip', 'wb') as f:
                    f.write(r.read())
                if aplicar_actualizacion('update.zip'):
                    messagebox.showinfo('Actualización', 'Actualización aplicada. Reinicie la aplicación.')
                else:
                    messagebox.showerror('Error', 'La actualización falló y se revirtió la versión previa.')
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo descargar: {e}')
                log(f'Error descargando actualización: {e}', level='ERROR')
        return True
    return False
