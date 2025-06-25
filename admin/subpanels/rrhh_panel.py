import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import subprocess
import webbrowser
import json
import socket
import shutil
import threading
import requests
import sys
from datetime import datetime

from logger import log, log_usuario
from config import CONFIG
from theme import aplicar_tema
import session

# -------------------- RUTAS Y CONFIG --------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LAUNCHER_DIR = os.path.join(BASE_DIR, "launchers")
LOG_FILE = os.path.join(LOG_DIR, "panel.log")
CONFIG_FILE = os.path.join(CONFIG_DIR, "entorno.txt")
KEYWORDS_FILE = os.path.join(CONFIG_DIR, "keywords.json")
CV_LAUNCHER = os.path.join(LAUNCHER_DIR, "cv_api_launcher.exe")
N8N_LAUNCHER = os.path.join(LAUNCHER_DIR, "n8n_launcher.exe")


# -------------------- RUTAS DE LOG --------------------
os.makedirs(LOG_DIR, exist_ok=True)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")


# -------------------- FUNCIONES AUXILIARES --------------------
def crear_estructura():
    for carpeta in [BASE_DIR, CONFIG_DIR, LOG_DIR, OUTPUT_DIR, LAUNCHER_DIR]:
        os.makedirs(carpeta, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            f.write("modo=produccion\napi_port=3001\ninstancia=n8n_rrhh\ndebug=True\n")
    if not os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(["excel", "rrhh", "reclutamiento"], f)

def puerto_en_uso(puerto):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', puerto)) == 0



# -------------------- FUNCIONES DEL PANEL --------------------
def abrir_n8n():
    try:
        if not os.path.exists(N8N_LAUNCHER):
            messagebox.showwarning("Faltante", "n8n_launcher.exe no encontrado")
            log("n8n_launcher.exe no encontrado", level="WARNING")
            log_usuario(session.usuario_actual, 'Abrir N8N - FALTANTE')
            return

        if puerto_en_uso(5678):
            abrir = messagebox.askyesno(
                "N8N ya se está ejecutando",
                "El puerto 5678 ya está en uso.\n¿Abrir navegador igualmente?"
            )
            if abrir:
                abrir_navegador_n8n()
            log("N8N ya estaba corriendo")
            return

        subprocess.Popen(N8N_LAUNCHER, shell=True)
        abrir_navegador_n8n()
        log("Se ejecutó n8n_launcher.exe")
        log_usuario(session.usuario_actual, 'Abrir N8N')
    except Exception as e:
        messagebox.showerror("Error", str(e))
        log(f"Error al abrir N8N: {e}", level="ERROR")
        log_usuario(session.usuario_actual, 'Abrir N8N - ERROR')

def abrir_navegador_n8n():
    try:
        import webbrowser
        # Validación simple: solo abrir si no hay otra pestaña abierta (sin certeza, pero evita spam)
        already_opened = getattr(abrir_navegador_n8n, "already_opened", False)
        if not already_opened:
            webbrowser.open("http://localhost:5678")
            log("Navegador abierto en http://localhost:5678")
            abrir_navegador_n8n.already_opened = True
        else:
            log("Intento duplicado de abrir N8N (navegador ya abierto)", level="WARNING")
    except Exception as e:
        messagebox.showwarning("No se pudo abrir navegador", str(e))
        log(f"No se pudo abrir navegador: {e}", level="WARNING")


def instalar_dependencias_n8n():
    try:
        subprocess.run("npm install -g n8n", shell=True)
        log("Se instalaron dependencias de N8N.")
        messagebox.showinfo("N8N", "Dependencias instaladas.")
    except Exception as e:
        log(f"Error al instalar N8N: {e}", level="ERROR")
        messagebox.showerror("Error", f"Error instalando N8N:\n{e}")

def ejecutar_cv_api():
    try:
        if not os.path.exists(CV_LAUNCHER):
            messagebox.showerror("Error", "cv_api_launcher.exe no encontrado en /launchers/")
            log("No se encontró cv_api_launcher.exe", level="ERROR")
            return

        if puerto_en_uso(3001):
            abrir = messagebox.askyesno(
                "CV API ya se está ejecutando",
                "El puerto 3001 ya está en uso.\n¿Querés continuar de todas formas?"
            )
            log("CV API ya estaba corriendo, ofreció continuar.")
            if not abrir:
                return

        subprocess.Popen(CV_LAUNCHER, shell=True)
        log("Se ejecutó cv_api_launcher.exe")
        log_usuario(session.usuario_actual, 'Ejecutar CV Analyzer')
        messagebox.showinfo("CV API", "El Analizador de CVs se está ejecutando en segundo plano.")
    except Exception as e:
        messagebox.showerror("Error grave", f"Ocurrió un error con CV Analyzer:\n{e}")
        log(f"Error inesperado abrir CV Analyzer: {e}", level="ERROR")
        log_usuario(session.usuario_actual, 'Ejecutar CV Analyzer - ERROR')


def agregar_keywords():
    palabras = simple_input("Ingresá nuevas keywords separadas por coma:")
    if not palabras:
        return

    nuevas = [k.strip() for k in palabras.split(",") if k.strip()]
    try:
        existentes = []
        if os.path.exists(KEYWORDS_FILE):
            with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
                existentes = json.load(f)
        lista = sorted(set(existentes + nuevas))
        with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(lista, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Keywords", "Palabras guardadas correctamente.")
        log_usuario(session.usuario_actual, 'Agregar keyword')
        log(f"Keywords actualizadas: {nuevas}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        log(f"Error al guardar keywords: {e}", level="ERROR")
        log_usuario(session.usuario_actual, 'Agregar keyword - ERROR')

def simple_input(prompt):
    win = tk.Toplevel()
    win.title("Input")
    tk.Label(win, text=prompt).pack()
    entry = tk.Entry(win, width=60)
    entry.pack()
    entry.focus()

    def submit():
        win.result = entry.get()
        win.destroy()

    tk.Button(win, text="Aceptar", command=submit).pack()
    win.wait_window()
    return getattr(win, 'result', '')


def slide_in(frame, h=0, target=120):
    frame.pack_propagate(False)
    frame.configure(height=h)
    if h < target:
        frame.after(10, lambda: slide_in(frame, h+10, target))


def fade_in_window(win, alpha=0.0):
    win.attributes('-alpha', alpha)
    if alpha < 1.0:
        win.after(20, lambda: fade_in_window(win, alpha+0.1))

def mostrar_modo_tecnico(event=None):
    clave = simple_input("🔒 Área restringida. Ingresá clave de sistemas:")
    if clave == "2391":
        frame_tecnico.pack(pady=(20, 5))
        slide_in(frame_tecnico)
        log("Modo técnico activado.")
    else:
        messagebox.showwarning("Acceso denegado", "Clave incorrecta.")
        log("Intento fallido de acceso al modo técnico.")

def ver_estado_servicios():
    estado = []
    try:
        requests.get("http://localhost:5678", timeout=2)
        estado.append("🟢 N8N OK")
    except:
        estado.append("🔴 N8N no responde")
    try:
        requests.get("http://localhost:3001", timeout=2)
        estado.append("🟢 CV API OK")
    except:
        estado.append("🔴 CV API no responde")
    messagebox.showinfo("Estado de servicios", "\n".join(estado))
    log("Se consultó estado de servicios")

def ver_log():
    os.system(f'notepad "{LOG_FILE}"')
    log("Se abrió el archivo de log")

def abrir_carpeta_rrhhbot():
    os.startfile(BASE_DIR)
    log("Se abrió la carpeta RRHHBot")

def editar_entorno():
    backup_dir = os.path.join('backups')
    os.makedirs(backup_dir, exist_ok=True)
    if os.path.exists(CONFIG_FILE):
        ts = datetime.now().strftime('%Y-%m-%d_%H%M')
        shutil.copy2(CONFIG_FILE, os.path.join(backup_dir, f'config_version_anterior_{ts}.json'))
    os.system(f'notepad "{CONFIG_FILE}"')
    log("Se editó entorno.txt")
    log_usuario(session.usuario_actual, 'Editar entorno')
    if messagebox.askyesno(
        "Reiniciar", "¿Reiniciar el panel para aplicar cambios?"
    ):
        log("Reiniciando aplicación por cambio de entorno")
        python = sys.executable
        os.execl(python, python, os.path.join(os.path.dirname(__file__), "..", "panel_mantenimiento_general.py"))



# -------------------- FUNCIÓN DE ENTRADA DEL SUBPANEL --------------------
def abrir_rrhh_panel():
    crear_estructura()

    titulo = CONFIG.get("titulo", "Panel de Mantenimiento - RRHH")
    modo_oscuro = CONFIG.get("modo_oscuro", "false").lower() == "true"
    tema = "oscuro" if modo_oscuro else "claro"

    ventana = tk.Toplevel()
    ventana.title(titulo)
    ventana.geometry("470x380")
    ventana.resizable(False, False)
    ventana.attributes('-alpha', 0.0)

    try:
        ventana.iconbitmap("assets/Guante.ico")
    except Exception as e:
        log(f"No se pudo cargar icono en RRHH: {e}", level="WARNING")

    aplicar_tema(ventana, tema)
    fade_in_window(ventana)

    tk.Label(ventana, text=titulo, font=("Arial", 14)).pack(pady=10)
    frame = tk.Frame(ventana)
    frame.pack(pady=5)

    # Sección N8N
    tk.Label(frame, text="1. N8N", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10)
    tk.Button(frame, text="Instalar dependencias", width=30, command=instalar_dependencias_n8n).grid(row=1, column=0, padx=10, pady=2)
    tk.Button(frame, text="Abrir N8N (localhost)", width=30, command=abrir_n8n).grid(row=2, column=0, padx=10, pady=2)

    # Analizador de CVs
    tk.Label(frame, text="2. Analizador de CVs", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", padx=10, pady=(10, 0))
    tk.Button(frame, text="Ejecutar CV Analyzer", width=30, command=ejecutar_cv_api).grid(row=4, column=0, padx=10, pady=2)

    # Skills
    tk.Label(frame, text="3. Skills / Keywords", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w", padx=10, pady=(10, 0))
    tk.Button(frame, text="Agregar nuevas palabras clave", width=30, command=agregar_keywords).grid(row=6, column=0, padx=10, pady=2)

    # Sistema
    tk.Label(frame, text="4. Sistema", font=("Arial", 12, "bold")).grid(row=7, column=0, sticky="w", padx=10, pady=(10, 0))
    tk.Button(frame, text="Cerrar este panel", width=30, command=ventana.destroy).grid(row=8, column=0, padx=10, pady=2)

    # Frame técnico
    global frame_tecnico
    frame_tecnico = tk.LabelFrame(ventana, text="🔧 Modo Técnico", font=("Arial", 10, "bold"), padx=10, pady=5)
    tk.Button(frame_tecnico, text="Ver estado de servicios", width=30, command=ver_estado_servicios).pack(pady=2)
    tk.Button(frame_tecnico, text="Ver archivo de log", width=30, command=ver_log).pack(pady=2)
    tk.Button(frame_tecnico, text="Abrir carpeta RRHHBot", width=30, command=abrir_carpeta_rrhhbot).pack(pady=2)
    tk.Button(frame_tecnico, text="Editar entorno", width=30, command=editar_entorno).pack(pady=2)
    frame_tecnico.pack_forget()

    ventana.bind("<Control-s>", mostrar_modo_tecnico)
    log("Subpanel RRHH iniciado.")


def load_panel(parent):
    crear_estructura()
    frame = ctk.CTkFrame(parent)

    def tarjeta(texto, comando):
        card = ctk.CTkFrame(frame)
        ctk.CTkLabel(card, text=texto, font=("Arial", 14, "bold")).pack(pady=(10,5))
        ctk.CTkButton(card, text=texto, command=comando, width=200, height=40).pack(pady=(0,10))
        return card

    tarjeta("Ejecutar CV Analyzer", ejecutar_cv_api).pack(fill="x", padx=20, pady=10)
    tarjeta("Abrir N8N", abrir_n8n).pack(fill="x", padx=20, pady=10)
    tarjeta("Agregar nueva keyword", agregar_keywords).pack(fill="x", padx=20, pady=10)

    return frame
