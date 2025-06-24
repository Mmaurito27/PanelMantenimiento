import tkinter as tk
from tkinter import messagebox
import subprocess
import webbrowser
import socket
import shutil
import os
import getpass
from datetime import datetime

# ---------- LOG AVANZADO ----------
LOG_PATH = os.path.join("logs", "panel.log")
os.makedirs("logs", exist_ok=True)

def write_log(msg, level="INFO"):
    usuario = getpass.getuser()
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    texto = f"{timestamp} [{level}] ({usuario}) {msg}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(texto)

def log_info(msg): write_log(msg, level="INFO")
def log_warning(msg): write_log(msg, level="WARNING")
def log_error(msg): write_log(msg, level="ERROR")

# ---------- CONFIGURACIÓN ----------
def leer_config():
    config = {}
    ruta = os.path.join("config", "entorno.txt")
    if not os.path.exists(ruta):
        log_warning("Archivo entorno.txt no encontrado.")
        return config
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                if "=" in linea:
                    clave, valor = linea.strip().split("=", 1)
                    config[clave.strip()] = valor.strip()
        log_info(f"Se leyó configuración: {config}")
    except Exception as e:
        log_error(f"Error al leer entorno.txt: {e}")
    return config

config = leer_config()

# ---------- FUNCIONES DE SISTEMA ----------
def n8n_disponible_en_path(): return shutil.which("n8n") is not None

def puerto_en_uso(puerto):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', puerto)) == 0

def abrir_n8n():
    try:
        if not n8n_disponible_en_path():
            resp = messagebox.askyesno("N8N no encontrado", "❗ N8N no está instalado.\n¿Deseás instalarlo ahora?")
            log_warning("N8N no encontrado.")
            if resp: instalar_dependencias_n8n()
            return

        if puerto_en_uso(5678):
            abrir = messagebox.askyesno("Ya se ejecuta", "El puerto 5678 ya está en uso.\n¿Abrir navegador igual?")
            if abrir: abrir_navegador_n8n()
            return

        subprocess.Popen("n8n", shell=True)
        abrir_navegador_n8n()
        log_info("N8N iniciado.")
    except Exception as e:
        messagebox.showerror("Error grave", f"N8N falló:\n{e}")
        log_error(f"Error al abrir N8N: {e}")

def abrir_navegador_n8n():
    try:
        webbrowser.open("http://localhost:5678")
        log_info("Abrió navegador en N8N")
    except Exception as e:
        log_warning(f"No se pudo abrir navegador: {e}")

def instalar_dependencias_n8n():
    try:
        subprocess.run("npm install -g n8n", shell=True)
        log_info("Dependencias N8N instaladas")
    except Exception as e:
        log_error(f"Error al instalar N8N: {e}")

def abrir_cv_analyzer():
    path = os.path.join("launchers", "cv_api_launcher.exe")
    try:
        if not os.path.exists(path):
            messagebox.showerror("Error", "cv_api_launcher.exe no está en /launchers/")
            log_error("cv_api_launcher.exe no encontrado")
            return

        if puerto_en_uso(3001):
            seguir = messagebox.askyesno("Puerto ocupado", "El puerto 3001 ya está en uso.\n¿Ejecutar de todas formas?")
            if not seguir: return

        subprocess.Popen(path, shell=True)
        log_info("cv_api_launcher iniciado")
    except Exception as e:
        log_error(f"Error ejecutando CV Analyzer: {e}")
        messagebox.showerror("Error grave", str(e))

# ---------- PANEL PRINCIPAL ----------
root = tk.Tk()
root.geometry("400x500")
root.resizable(False, False)

# ---------- TEMA Y ESTILO ----------
modo_oscuro_activo = config.get("modo_oscuro", "false").lower() == "true"

def aplicar_modo_oscuro(ventana, oscuro=True):
    if oscuro:
        ventana.configure(bg="#16202a")
        ventana.option_add("*TButton*background", "#1e1e1e")
        ventana.option_add("*TButton*foreground", "#ffffff")
        ventana.option_add("*Button*background", "#1e1e1e")
        ventana.option_add("*Button*foreground", "#ffffff")
        ventana.option_add("*Label*background", "#16202a")
        ventana.option_add("*Label*foreground", "#ffffff")
    else:
        ventana.configure(bg="#f0f0f0")
        ventana.option_add("*TButton*background", "#ffffff")
        ventana.option_add("*TButton*foreground", "#000000")
        ventana.option_add("*Button*background", "#ffffff")
        ventana.option_add("*Button*foreground", "#000000")
        ventana.option_add("*Label*background", "#f0f0f0")
        ventana.option_add("*Label*foreground", "#000000")

def toggle_modo_oscuro():
    global modo_oscuro_activo
    modo_oscuro_activo = not modo_oscuro_activo
    aplicar_modo_oscuro(root, oscuro=modo_oscuro_activo)
    btn_tema.config(text="☀️" if modo_oscuro_activo else "🌙")

btn_tema = tk.Button(root, text="☀️" if modo_oscuro_activo else "🌙", command=toggle_modo_oscuro, bd=0)
btn_tema.place(x=360, y=10)

aplicar_modo_oscuro(root, oscuro=modo_oscuro_activo)

# ---------- ÍCONO Y TÍTULO ----------
titulo = config.get("titulo", "Panel de Mantenimiento General")
root.title(titulo)
try:
    root.iconbitmap("assets/Guante.ico")
except: pass

# ---------- CABECERA ----------
tk.Label(root, text=titulo, font=("Arial", 14, "bold")).pack(pady=20)

# ---------- BOTONES DE ÁREA ----------
def abrir_rrhh():
    try:
        from subpanels import rrhh_panel
        rrhh_panel.abrir_rrhh_panel()
        log_info("Abrió subpanel RRHH")
    except Exception as e:
        log_error(f"Error abriendo RRHH: {e}")
        messagebox.showerror("Error", str(e))

def modulo_en_desarrollo(nombre):
    log_info(f"Módulo en desarrollo: {nombre}")
    messagebox.showinfo("En desarrollo", f"🔧 El módulo de {nombre} aún no está disponible.")

areas = [
    ("RRHH", abrir_rrhh),
    ("Marketing", lambda: modulo_en_desarrollo("Marketing")),
    ("Comercial", lambda: modulo_en_desarrollo("Comercial")),
    ("Logística", lambda: modulo_en_desarrollo("Logística")),
    ("Sistemas", lambda: modulo_en_desarrollo("Sistemas")),
    ("Calidad", lambda: modulo_en_desarrollo("Calidad")),
    ("Dirección", lambda: modulo_en_desarrollo("Dirección")),
]

for nombre, accion in areas:
    tk.Button(root, text=nombre, width=30, height=2, command=accion).pack(pady=5)

tk.Button(root, text="Salir", width=20, command=root.destroy).pack(pady=20)

# ---------- FINAL ----------
root.mainloop()
log_info("Panel general iniciado.")
