import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import webbrowser
from datetime import datetime
import json
import socket
import shutil
import threading
import requests
import getpass
from datetime import datetime

# -------------------- RUTAS Y CONFIG --------------------
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "RRHHBot")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LAUNCHER_DIR = os.path.join(BASE_DIR, "launchers")
LOG_FILE = os.path.join(LOG_DIR, "panel.log")
CONFIG_FILE = os.path.join(CONFIG_DIR, "entorno.txt")
KEYWORDS_FILE = os.path.join(CONFIG_DIR, "keywords.json")
CV_LAUNCHER = os.path.join(LAUNCHER_DIR, "cv_api_launcher.exe")
N8N_LAUNCHER = "n8n"

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


# -------------------- RUTAS DE LOG --------------------
os.makedirs(LOG_DIR, exist_ok=True)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")
# -------------------- FUNCIONES DE LOG --------------------
def log(mensaje):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {mensaje}\n")
# -------------------- LOG AVANZADO --------------------
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "panel.log")

def write_log(msg, level="INFO"):
    usuario = getpass.getuser()
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    texto = f"{timestamp} [{level}] ({usuario}) {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(texto)

def log_info(msg):
    write_log(msg, level="INFO")

def log_warning(msg):
    write_log(msg, level="WARNING")

def log_error(msg):
    write_log(msg, level="ERROR")


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

def log(mensaje):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {mensaje}\n")

def puerto_en_uso(puerto):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', puerto)) == 0

def n8n_disponible_en_path():
    return shutil.which("n8n") is not None

# -------------------- FUNCIONES DEL PANEL --------------------
def abrir_n8n():
    try:
        if not n8n_disponible_en_path():
            resp = messagebox.askyesno(
                "N8N no encontrado",
                "❗ N8N no está instalado o no está en el PATH.\n¿Deseás instalarlo ahora?"
            )
            log_warning("N8N no encontrado, ofreció instalar.")
            if resp:
                instalar_dependencias_n8n()
            return

        if puerto_en_uso(5678):
            abrir = messagebox.askyesno(
                "N8N ya se está ejecutando",
                "El puerto 5678 ya está en uso.\n¿Querés abrir el navegador igualmente?"
            )
            log_info("N8N ya estaba corriendo, ofreció abrir navegador.")
            if abrir:
                abrir_navegador_n8n()
            return

        subprocess.Popen(N8N_LAUNCHER, shell=True)
        abrir_navegador_n8n()
        log_info("Se ejecutó y abrió N8N.")
        messagebox.showinfo(
            "N8N",
            "N8N se está ejecutando en segundo plano y se abrió el navegador."
        )
    except Exception as e:
        messagebox.showerror("Error grave", f"Ocurrió un error al abrir N8N:\n{e}")
        log_error(f"Error inesperado abrir N8N: {e}")

def abrir_navegador_n8n():
    try:
        import webbrowser
        # Validación simple: solo abrir si no hay otra pestaña abierta (sin certeza, pero evita spam)
        already_opened = getattr(abrir_navegador_n8n, "already_opened", False)
        if not already_opened:
            webbrowser.open("http://localhost:5678")
            log_info("Navegador abierto en http://localhost:5678")
            abrir_navegador_n8n.already_opened = True
        else:
            log_warning("Intento duplicado de abrir N8N (navegador ya abierto)")
    except Exception as e:
        messagebox.showwarning("No se pudo abrir navegador", str(e))
        log_warning(f"No se pudo abrir navegador: {e}")


def instalar_dependencias_n8n():
    try:
        subprocess.run("npm install -g n8n", shell=True)
        log_info("Se instalaron dependencias de N8N.")
        messagebox.showinfo("N8N", "Dependencias instaladas.")
    except Exception as e:
        log_error(f"Error al instalar N8N: {e}")
        messagebox.showerror("Error", f"Error instalando N8N:\n{e}")

def ejecutar_cv_api():
    try:
        if not os.path.exists(CV_LAUNCHER):
            messagebox.showerror("Error", "cv_api_launcher.exe no encontrado en /launchers/")
            log_error("No se encontró cv_api_launcher.exe")
            return

        if puerto_en_uso(3001):
            abrir = messagebox.askyesno(
                "CV API ya se está ejecutando",
                "El puerto 3001 ya está en uso.\n¿Querés continuar de todas formas?"
            )
            log_info("CV API ya estaba corriendo, ofreció continuar.")
            if not abrir:
                return

        subprocess.Popen(CV_LAUNCHER, shell=True)
        log_info("Se ejecutó cv_api_launcher.exe")
        messagebox.showinfo("CV API", "El Analizador de CVs se está ejecutando en segundo plano.")
    except Exception as e:
        messagebox.showerror("Error grave", f"Ocurrió un error con CV Analyzer:\n{e}")
        log_error(f"Error inesperado abrir CV Analyzer: {e}")


def agregar_keywords():
    keywords = simple_input("Ingresá las nuevas keywords separadas por coma:")
    if keywords:
        lista = [k.strip() for k in keywords.split(",")]
        with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(lista, f, indent=2, ensure_ascii=False)
        try:
            r = requests.post("http://localhost:3001/configurar-skills/", json=lista)
            if r.status_code == 200:
                messagebox.showinfo("Éxito", "Skills actualizadas correctamente.")
                log(f"Se actualizaron skills: {lista}")
            else:
                log(f"ERROR al actualizar skills: {r.text}")
                messagebox.showerror("Error", f"Respuesta: {r.text}")
        except Exception as e:
            log(f"ERROR conexión API: {e}")
            messagebox.showerror("Error", str(e))

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

def mostrar_modo_tecnico(event=None):
    clave = simple_input("🔒 Área restringida. Ingresá clave de sistemas:")
    if clave == "2391":
        frame_tecnico.pack(pady=(20, 5))
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



# -------------------- FUNCIÓN DE ENTRADA DEL SUBPANEL --------------------
def abrir_rrhh_panel():
    crear_estructura()

    config = leer_config()
    titulo = config.get("titulo", "Panel de Mantenimiento - RRHH")
    modo_oscuro = config.get("modo_oscuro", "false").lower() == "true"

    ventana = tk.Toplevel()
    ventana.title(titulo)
    ventana.geometry("470x380")
    ventana.resizable(False, False)

    try:
        ventana.iconbitmap("assets/Guante.ico")
    except Exception as e:
        log_warning(f"No se pudo cargar icono en RRHH: {e}")

    if modo_oscuro:
        ventana.configure(bg="#1e1e1e")

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

    ventana.bind("<Control-s>", mostrar_modo_tecnico)
    log_info("Subpanel RRHH iniciado.")