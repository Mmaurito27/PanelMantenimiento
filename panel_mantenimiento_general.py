import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
import socket
import shutil
import os
import sys

from logger import log
from config import CONFIG
from theme import aplicar_tema
from update import detectar_modo_ejecucion
import update_checker


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
    except Exception as e:
        messagebox.showerror("Error grave", f"N8N falló:\n{e}")
        log(f"Error al abrir N8N: {e}", level="ERROR")

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
    except Exception as e:
        log(f"Error ejecutando CV Analyzer: {e}", level="ERROR")
        messagebox.showerror("Error grave", str(e))

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

# ---------- PANEL PRINCIPAL ----------
root = tk.Tk()
root.geometry("400x500")
root.resizable(False, False)
style = ttk.Style()
style.theme_use("clam")

verificar_dependencias()
detectar_modo_ejecucion()
version_actual = update_checker.get_local_version()

# ---------- TEMA Y ESTILO ----------
modo_oscuro_activo = CONFIG.get("modo_oscuro", "false").lower() == "true"
tema_actual = "oscuro" if modo_oscuro_activo else "claro"

class ThemeSwitch(ttk.Frame):
    def __init__(self, master, command=None, checked=False):
        super().__init__(master)
        self.command = command
        self.var = tk.BooleanVar(value=checked)
        self.canvas = tk.Canvas(self, width=50, height=24, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.toggle)
        self.draw()

    def toggle(self, event=None):
        self.var.set(not self.var.get())
        self.draw()
        if self.command:
            self.command(self.var.get())

    def draw(self):
        self.canvas.delete("all")
        if self.var.get():
            self.canvas.create_rectangle(2,2,48,22, outline="#4caf50", fill="#4caf50", width=2)
            self.canvas.create_oval(28,4,46,20, fill="#ffffff", outline="#ffffff")
            self.canvas.create_text(14,12, text="☀️")
        else:
            self.canvas.create_rectangle(2,2,48,22, outline="#ccc", fill="#ccc", width=2)
            self.canvas.create_oval(4,4,22,20, fill="#ffffff", outline="#ffffff")
            self.canvas.create_text(36,12, text="🌙")

def toggle_modo_oscuro(valor: bool):
    global modo_oscuro_activo
    modo_oscuro_activo = valor
    tema = "oscuro" if valor else "claro"
    aplicar_tema(root, tema)
    _update_sidebar_theme()
    CONFIG['modo_oscuro'] = 'true' if modo_oscuro_activo else 'false'

theme_switch = ThemeSwitch(root, command=toggle_modo_oscuro, checked=modo_oscuro_activo)
theme_switch.place(x=340, y=10)


def simple_input(prompt: str) -> str:
    win = tk.Toplevel(root)
    win.title('Input')
    tk.Label(win, text=prompt).pack()
    entry = tk.Entry(win, width=50)
    entry.pack()
    entry.focus()

    def submit():
        win.result = entry.get()
        win.destroy()

    tk.Button(win, text='Aceptar', command=submit).pack()
    win.grab_set()
    win.wait_window()
    return getattr(win, 'result', '')


def ver_log_extendido():
    win = tk.Toplevel(root)
    win.title('Log extendido')
    win.geometry('500x400')
    text = tk.Text(win, wrap='none')
    text.pack(fill='both', expand=True, side='left')
    sb = ttk.Scrollbar(win, command=text.yview)
    sb.pack(side='right', fill='y')
    text.configure(yscrollcommand=sb.set)
    try:
        with open(os.path.join('logs', 'panel.log'), 'r', encoding='utf-8') as f:
            for line in f:
                if '[ERROR]' in line:
                    tag = 'error'
                elif '[WARNING]' in line:
                    tag = 'warn'
                else:
                    tag = 'info'
                text.insert('end', line, tag)
    except Exception as e:
        text.insert('end', f'No se pudo cargar el log: {e}')

    text.tag_config('error', background='#ffcccc')
    text.tag_config('warn', background='#fff2cc')


def mostrar_modo_tecnico(event=None):
    clave = simple_input('🔒 Área restringida. Ingresá clave de sistemas:')
    if clave == '2391':
        frame_tecnico.pack(pady=(10, 5))
        slide_in(frame_tecnico)
        log('Modo técnico activado.')
    else:
        messagebox.showwarning('Acceso denegado', 'Clave incorrecta.')
        log('Intento fallido de acceso al modo técnico.')


def slide_in(frame, h=0, target=120):
    frame.pack_propagate(False)
    frame.configure(height=h)
    if h < target:
        frame.after(10, lambda: slide_in(frame, h+10, target))


def abrir_documentacion():
    ruta = CONFIG.get("documentacion", os.path.join("docs", "manual.pdf"))
    if os.path.exists(ruta):
        webbrowser.open(ruta)
        log("Se abrió la documentación local")
    else:
        url = CONFIG.get("documentacion_url", "https://example.com/manual")
        webbrowser.open(url)
        log(f"Documentación local no encontrada. Abrió {url}", level="WARNING")

doc_btn = ttk.Button(root, text="📘 Ayuda / Manual", command=abrir_documentacion)
doc_btn.place(x=220, y=10)
ttk.Label(root, text=f"v{version_actual}").place(x=10, y=10)

aplicar_tema(root, tema_actual)

# ---------- BARRA LATERAL ----------
sidebar_visible = True
sidebar_frame = tk.Frame(root, width=40)
sidebar_frame.pack(side="left", fill="y")

def toggle_sidebar():
    global sidebar_visible
    if sidebar_visible:
        sidebar_frame.pack_forget()
        sidebar_visible = False
    else:
        sidebar_frame.pack(side="left", fill="y")
        sidebar_visible = True

toggle_btn = ttk.Button(root, text="≡", width=2, command=toggle_sidebar)
toggle_btn.place(x=60, y=10)

def _update_sidebar_theme():
    aplicar_tema(sidebar_frame, "oscuro" if modo_oscuro_activo else "claro")

_update_sidebar_theme()

ttk.Button(sidebar_frame, text="🏠", width=3, command=lambda: None).pack(pady=5)
ttk.Button(sidebar_frame, text="👤", width=3, command=lambda: abrir_rrhh()).pack(pady=5)
ttk.Button(sidebar_frame, text="📢", width=3, command=lambda: modulo_en_desarrollo('Marketing')).pack(pady=5)
ttk.Button(sidebar_frame, text="✅", width=3, command=lambda: modulo_en_desarrollo('Calidad')).pack(pady=5)

# ---------- ÍCONO Y TÍTULO ----------
titulo = CONFIG.get("titulo", "Panel de Mantenimiento General")
root.title(titulo)
try:
    root.iconbitmap("assets/Guante.ico")
except Exception:
    pass

# ---------- CABECERA ----------
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

ttk.Label(main_frame, text=titulo, font=("Arial", 14, "bold")).pack(pady=(0,10))

# ---------- BOTONES DE ÁREA ----------
def abrir_rrhh():
    try:
        from subpanels import rrhh_panel
        rrhh_panel.abrir_rrhh_panel()
        log("Abrió subpanel RRHH")
    except Exception as e:
        log(f"Error abriendo RRHH: {e}", level="ERROR")
        messagebox.showerror("Error", str(e))

def modulo_en_desarrollo(nombre):
    log(f"Módulo en desarrollo: {nombre}")
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
    ttk.Button(main_frame, text=nombre, width=30, command=accion).pack(fill="x", pady=3)

ttk.Button(main_frame, text="Salir", command=root.destroy).pack(pady=10)

# ---------- FRAME T\xc9CNICO ----------
frame_tecnico = ttk.LabelFrame(root, text="\ud83d\udd27 Modo T\xe9cnico", padding=10)
ttk.Button(frame_tecnico, text="Ver LOG extendido", command=ver_log_extendido).pack(pady=2)
frame_tecnico.pack_forget()
root.bind("<Control-s>", mostrar_modo_tecnico)

# ---------- FINAL ----------
root.mainloop()
log("Panel general iniciado.")
