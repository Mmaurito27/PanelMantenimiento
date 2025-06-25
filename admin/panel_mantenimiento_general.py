import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import subprocess
import webbrowser
import socket
import shutil
import os
import sys
import importlib
import json
from datetime import datetime

from logger import log, log_usuario
from login_window import mostrar_login
import session
from config import CONFIG
from theme import aplicar_tema
from tooltip import Tooltip
from update import detectar_modo_ejecucion, is_running_exe, ensure_embedded_python
import update_checker


def verificar_estructura_inicial():
    """Comprueba y crea la estructura básica del proyecto."""
    carpetas = [
        'config',
        'logs',
        'assets',
        'launchers',
        'subpanels',
        'docs',
    ]
    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta, exist_ok=True)
            log(f'Se creó la carpeta {carpeta}')

    # crear archivo log inicial
    log_path = os.path.join('logs', 'panel.log')
    if not os.path.exists(log_path):
        with open(log_path, 'a', encoding='utf-8'):
            pass
        log('Se creó logs/panel.log')

    # ---------- Archivos requeridos ----------
    entorno = os.path.join('config', 'entorno.txt')
    if not os.path.exists(entorno):
        src = os.path.join('docs', 'entorno_default.txt')
        if os.path.exists(src):
            shutil.copy2(src, entorno)
        else:
            contenido = (
                'modo_oscuro=false\n'
                'titulo=Panel de Mantenimiento General\n'
                'documentacion=docs/manual.pdf\n'
            )
            with open(entorno, 'w', encoding='utf-8') as f:
                f.write(contenido)
        log('Se creó config/entorno.txt')

    panels = os.path.join('config', 'panels.json')
    if not os.path.exists(panels):
        paneles = []
        if os.path.exists('subpanels'):
            for f in os.listdir('subpanels'):
                if f.endswith('_panel.py'):
                    paneles.append(f[:-9])
        with open(panels, 'w', encoding='utf-8') as f:
            json.dump(paneles, f, indent=2)
        log('Se creó config/panels.json')

    if not os.path.exists('requirements.txt'):
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write('')
        log('Se creó requirements.txt vacío')

    version_file = 'version.txt'
    if not os.path.exists(version_file):
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write('version=1.0.0\n')
        log('Se creó version.txt con versión 1.0.0')

    faltantes = []
    exe_cv = os.path.join('launchers', 'cv_api_launcher.exe')
    exe_n8n = os.path.join('launchers', 'n8n_launcher.exe')
    if not os.path.exists(exe_cv):
        faltantes.append('cv_api_launcher.exe')
    if not os.path.exists(exe_n8n):
        faltantes.append('n8n_launcher.exe')

    ico = os.path.join('assets', 'Guante.ico')
    if not os.path.exists(ico):
        log('Guante.ico no encontrado', level='WARNING')
        faltantes.append('Guante.ico')

    if faltantes:
        messagebox.showwarning(
            'Archivos faltantes',
            'El panel funcionará con funciones limitadas. Faltan: ' + ', '.join(faltantes)
        )
        log('Archivos faltantes: ' + ', '.join(faltantes), level='WARNING')

    if is_running_exe():
        modo = detectar_modo_ejecucion()
        log(f'Ejecución empaquetada: {modo}')
        ensure_embedded_python()
    else:
        log('Ejecución en modo desarrollo')


# ---------- FUNCIONES DE SISTEMA ----------
def n8n_disponible_en_path(): return shutil.which("n8n") is not None

def puerto_en_uso(puerto):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', puerto)) == 0

def abrir_n8n():
    try:
        if not n8n_disponible_en_path():
            resp = messagebox.askyesno("N8N no encontrado", "❗ N8N no está instalado.\n¿Deseás instalarlo ahora?")
            log("N8N no encontrado.", level="WARNING")
            if resp: instalar_dependencias_n8n()
            return

        if puerto_en_uso(5678):
            abrir = messagebox.askyesno("Ya se ejecuta", "El puerto 5678 ya está en uso.\n¿Abrir navegador igual?")
            if abrir: abrir_navegador_n8n()
            return

        subprocess.Popen("n8n", shell=True)
        abrir_navegador_n8n()
        log("N8N iniciado.")
        log_usuario(session.usuario_actual, 'Abrir N8N')
    except Exception as e:
        messagebox.showerror("Error grave", f"N8N falló:\n{e}")
        log(f"Error al abrir N8N: {e}", level="ERROR")
        log_usuario(session.usuario_actual, 'Abrir N8N - ERROR')

def abrir_navegador_n8n():
    try:
        webbrowser.open("http://localhost:5678")
        log("Abrió navegador en N8N")
    except Exception as e:
        log(f"No se pudo abrir navegador: {e}", level="WARNING")

def instalar_dependencias_n8n():
    try:
        subprocess.run("npm install -g n8n", shell=True)
        log("Dependencias N8N instaladas")
    except Exception as e:
        log(f"Error al instalar N8N: {e}", level="ERROR")

def abrir_cv_analyzer():
    path = os.path.join("launchers", "cv_api_launcher.exe")
    try:
        if not os.path.exists(path):
            messagebox.showerror("Error", "cv_api_launcher.exe no está en /launchers/")
            log("cv_api_launcher.exe no encontrado", level="ERROR")
            return

        if puerto_en_uso(3001):
            seguir = messagebox.askyesno("Puerto ocupado", "El puerto 3001 ya está en uso.\n¿Ejecutar de todas formas?")
            if not seguir: return

        subprocess.Popen(path, shell=True)
        log("cv_api_launcher iniciado")
        log_usuario(session.usuario_actual, 'Ejecutar CV Analyzer')
    except Exception as e:
        log(f"Error ejecutando CV Analyzer: {e}", level="ERROR")
        messagebox.showerror("Error grave", str(e))
        log_usuario(session.usuario_actual, 'Ejecutar CV Analyzer - ERROR')


def abrir_rrhh():
    """Abre el subpanel de RRHH si está disponible."""
    abrir_subpanel('rrhh')


def modulo_en_desarrollo(nombre: str):
    """Muestra un aviso de módulo en desarrollo."""
    messagebox.showinfo('En desarrollo', f'El módulo {nombre} está en desarrollo')
    log(f'Módulo {nombre} en desarrollo', level='WARNING')
    log_usuario(session.usuario_actual, f'Módulo {nombre} - NO_IMPLEMENTADO')

def verificar_dependencias():
    """Comprueba la existencia de dependencias principales."""
    faltantes = []
    if shutil.which("python") is None:
        faltantes.append("Python")
    if shutil.which("node") is None:
        faltantes.append("Node")
    if shutil.which("n8n") is None:
        faltantes.append("N8N")
    if not os.path.exists(os.path.join("launchers", "cv_api_launcher.exe")):
        faltantes.append("cv_api_launcher.exe")

    if faltantes:
        messagebox.showwarning(
            "Dependencias faltantes",
            "No se encontraron: " + ", ".join(faltantes),
        )
        log("Faltan dependencias: " + ", ".join(faltantes), level="WARNING")
    else:
        log("Todas las dependencias están presentes.")


def _load_panels():
    """Carga la lista de paneles dinámicos desde config/panels.json"""
    path = os.path.join('config', 'panels.json')
    if not os.path.exists(path):
        return ['rrhh']
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return ['rrhh']


def _save_panels(paneles):
    path = os.path.join('config', 'panels.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(paneles, f, indent=2)


def backup_entorno():
    os.makedirs('backups', exist_ok=True)
    origen = os.path.join('config', 'entorno.txt')
    if os.path.exists(origen):
        ts = datetime.now().strftime('%Y-%m-%d_%H%M')
        dest = os.path.join('backups', f'entorno_backup_{ts}.txt')
        shutil.copy2(origen, dest)


def restaurar_backup():
    archivos = []
    if os.path.exists("backups"):
        archivos = [f for f in os.listdir("backups") if f.startswith("entorno_backup_")]
    if not archivos:
        messagebox.showinfo("Restaurar", "No hay backups disponibles")
        return
    win = tk.Toplevel(root)
    win.title("Restaurar backup")
    lb = tk.Listbox(win, width=50)
    for f in archivos:
        lb.insert("end", f)
    lb.pack(padx=10, pady=10)
    def restaurar():
        sel = lb.curselection()
        if not sel:
            return
        archivo = os.path.join("backups", lb.get(sel[0]))
        shutil.copy2(archivo, os.path.join("config", "entorno.txt"))
        messagebox.showinfo("Restaurar", "Archivo restaurado")
        win.destroy()
    ttk.Button(win, text="Restaurar", command=restaurar).pack(pady=5)


# ---------- PANEL PRINCIPAL ----------
if __name__ == '__main__':
    temp_root = tk.Tk()
    temp_root.withdraw()
    verificar_estructura_inicial()
    temp_root.destroy()

    mostrar_login()
    import importlib
    importlib.reload(session)

    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.geometry("900x600")
    root.resizable(False, False)

    titulo = CONFIG.get("titulo", "Panel de Mantenimiento General")
    root.title(titulo)
    try:
        root.iconbitmap("assets/Guante.ico")
    except Exception:
        pass

    sidebar_width = 225
    sidebar = ctk.CTkFrame(root, width=sidebar_width, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    main_content = ctk.CTkFrame(root, corner_radius=0)
    main_content.pack(side="right", expand=True, fill="both")

    nav_buttons = {}
    current_panel = None

    def highlight(btn_key):
        for key, btn in nav_buttons.items():
            if key == btn_key:
                btn.configure(fg_color="#1f6aa5")
            else:
                btn.configure(fg_color=("gray75", "gray25"))

    def cargar_panel(nombre):
        global current_panel
        highlight(nombre)
        if current_panel:
            current_panel.destroy()
        try:
            mod = importlib.import_module(f"subpanels.{nombre}_panel")
            panel = mod.load_panel(main_content)
            panel.pack(fill="both", expand=True, padx=20, pady=20)
            current_panel = panel
            log(f"Abrió subpanel {nombre}")
            log_usuario(session.usuario_actual, f"Abrir subpanel {nombre}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            log(f"Error abriendo {nombre}: {e}", level="ERROR")

    def boton_nav(texto, nombre):
        btn = ctk.CTkButton(
            sidebar,
            text=texto,
            width=sidebar_width-20,
            fg_color=("gray75", "gray25"),
            command=lambda n=nombre: cargar_panel(n),
        )
        btn.pack(pady=10, padx=10)
        nav_buttons[nombre] = btn

    boton_nav("RRHH", "rrhh")
    boton_nav("Marketing", "marketing")
    boton_nav("Calidad", "calidad")

    cargar_panel("rrhh")

    root.mainloop()
    log("Panel general iniciado.")
